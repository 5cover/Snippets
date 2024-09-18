#!/usr/bin/env python3

from dataclasses import dataclass
from os import path
from typing import IO, Sequence, Optional, Callable, Any, NamedTuple, TypeAlias
import argparse as ap
import functools
import math
import os
import pathlib
import re
import shutil
import subprocess as sp
import sys
import termcolor as tc

CMD: TypeAlias = Sequence[str] | str
FILE: TypeAlias = Optional[int | IO[Any]]

REGEXP_FLOAT = r'-?\d*(?:\.\d+)?'


@dataclass(frozen=True)
class NormalizationError(Exception):
    msg: str
    output: str


class AudioInfo(NamedTuple):
    max_vol: float
    mean_vol: float
    bitrate: float

    def __str__(self):
        return f'max: {self.max_vol} dB, mean: {self.mean_vol} dB, {self.bitrate} kb/s'


@dataclass(frozen=True)
class Args:
    copyd: bool
    copys: bool
    copyv: bool
    ffmpeg_path: str
    global_opts: Sequence[str]
    input_files: Sequence[str]
    log: Callable[..., None]
    mode: str
    max_bitrate: float
    quality: Optional[str]
    onerror: str
    output_encoder: Optional[str]
    output_files: Optional[Sequence[str]]
    overwrite: bool
    set_x_mode: bool
    two_pass: bool

    def ffmpeg(
            self, args: Sequence[str],
            *, allow_failure=False, stdout: FILE = None, stderr: FILE = None, capture_output: bool = False) -> sp.CompletedProcess:
        args = (self.ffmpeg_path,) + self.global_opts + args
        if self.set_x_mode:
            print('+', sp.list2cmdline(args), file=sys.stderr)
        cp = sp.run(args, stdout=stdout, stderr=stderr, capture_output=capture_output)
        if not allow_failure and self.onerror == 'stop':
            cp.check_returncode()
        return cp


def flteq(x: float, y: float, epsilon: float = .1) -> bool:
    return abs(x - y) < epsilon


def get_mean_target_volume(args: Args, audio_infos: Sequence[AudioInfo]):
    """mean normalization : consistent volume + as high as possible"""
    from statistics import median
    median_mean_vol = median(a.mean_vol for a in audio_infos)
    args.log(format_info(f'Median of mean volumes: {median_mean_vol}'))

    # correction necessary in order to enforce invariant max_vol <= 0
    correct = max(median_mean_vol - a.mean_vol + a.max_vol for a in audio_infos)
    args.log(format_info(f'Correct for max volume <= 0: {correct}'))

    return median_mean_vol - correct


def ffmpeg_io(args: Args, audio: AudioInfo, in_f: str, out_f: str,
              post_input_args: tuple[str] = (), pre_output_args: tuple[str] = ()) -> sp.CompletedProcess:
    def ffmpeg_io_2_pass(post_input_args: tuple[str], pre_output_args: tuple[str]) -> sp.CompletedProcess:
        # pass 1: output to /dev/null
        # since we can't know what to give to the -f argument, create a symlink to /dev/null and have ffmpeg output to it.
        # what matters is that output has the extension so ffmpeg can choose the appropriate format.
        if args.overwrite:
            try:
                os.remove(out_f)
            except FileNotFoundError:
                pass
        os.symlink('/dev/null', out_f)  # raises FileExistsError if the file exists
        ffmpeg_io_1_pass(post_input_args, ('-pass', '1') + pre_output_args)
        os.remove(out_f)

        # pass 2
        return ffmpeg_io_1_pass(post_input_args, ('-pass', '2') + pre_output_args)

    def ffmpeg_io_1_pass(post_input_args: tuple[str], pre_output_args: tuple[str]) -> sp.CompletedProcess:
        ffmpeg_args = (
            '-i', in_f, *post_input_args,
            '-b:a', f'{min(args.max_bitrate, audio.bitrate)}k',
            '-stats', '-loglevel', 'warning',
            '-y' if a.overwrite else '-n') + (
            ('-c:s', 'copy') if args.copys else ('-sn',)) + (
            ('-c:v', 'copy') if args.copyv else ('-vn',)) + (
            ('-c:d', 'copy') if args.copyd else ('-dn',)) + (
            *pre_output_args, out_f)
        if args.output_encoder:
            ffmpeg_args += '-c:a', args.output_encoder
        if args.quality:
            ffmpeg_args += '-q:a', args.quality

        return args.ffmpeg(ffmpeg_args, stdout=sp.PIPE, stderr=sp.PIPE)

    return ffmpeg_io_2_pass(
        post_input_args, pre_output_args) if args.two_pass else ffmpeg_io_1_pass(
        post_input_args, pre_output_args)


def normalize_volume(args: Args):
    AUDIO_INFOS = (get_audio_info(args, f) for f in args.input_files)

    TARGET_VOL, vol = (get_mean_target_volume(args, AUDIO_INFOS := tuple(AUDIO_INFOS)),
                       lambda a: a.mean_vol) if args.mode == 'mean' else (0, lambda a: a.max_vol)

    args.log(format_info(f'Normalizing {len(args.input_files)} files ({args.mode} mode)'))
    args.log(format_info(f'Expected volume: {TARGET_VOL}'))

    if not args.output_files:
        return

    for NFILE, (AUDIO, IN_F, OUT_F) in enumerate(zip(AUDIO_INFOS, args.input_files, args.output_files, strict=True), start=1):
        args.log(f'{NFILE}/{len(args.input_files)}: {IN_F}')

        pathlib.Path(OUT_F).parent.mkdir(parents=True, exist_ok=True)

        if flteq(vol(AUDIO), TARGET_VOL):
            args.log(format_info(f'Volume ({vol(AUDIO)}) already matches expected volume, copying\ncopied to: {OUT_F}'))
            ffmpeg_io(args, AUDIO, IN_F, OUT_F)
            continue

        delta_vol = TARGET_VOL - vol(AUDIO)
        args.log(f"normalizing: {delta_vol:+f} dB")
        ffmpeg_io(args, AUDIO, IN_F, OUT_F, ('-filter:a', f'volume={delta_vol}dB'))
        new_vol = vol(get_audio_info(args, OUT_F))
        if not flteq(new_vol, TARGET_VOL):
            args.log(format_warning(f"output volume is {new_vol}, expected {TARGET_VOL}"))


def get_audio_info(args: Args, input_file: str) -> AudioInfo:
    output = args.ffmpeg(('-i', input_file, '-filter:a', 'volumedetect',
                          '-vn', '-sn', '-dn',
                         '-f', 'null', '/dev/null'),
                         capture_output=True).stderr.decode()

    def match_output(attr_name: str, pattern: str):
        match = re.search(pattern, output)
        if not match:
            raise NormalizationError(f"{attr_name} not found for file '{input_file}'", output)
        return match[1]
    info = AudioInfo(
        max_vol=float(match_output('max volume', f'max_volume: ({REGEXP_FLOAT}) dB')),
        mean_vol=float(match_output('mean volume', f'mean_volume: ({REGEXP_FLOAT}) dB')),
        bitrate=float(match_output('bitrate', fr'Audio: .*, ({REGEXP_FLOAT}) kb/s')))
    args.log(f'{info}\t{input_file}')
    return info


def indent(text: str, count: int) -> str:
    prefix = ' ' * count
    return prefix + text.replace('\n', '\n' + prefix)


def format_error(msg: object) -> str:
    return format_message('error', msg, 'red')


def format_warning(msg: object) -> str:
    return format_message('warning', msg, 'yellow')


def format_info(msg: object) -> str:
    return format_message('info', msg, 'blue')


def format_message(cat: str, msg: Any, color: str):
    return tc.colored(f'{path.basename(sys.argv[0])}: {cat}: {msg}', color=color)


if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Normalize audio files by peak or average volume',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)

    parser.add_argument('mode', choices={'peak', 'mean'}, help='normalization mode')
    parser.add_argument('input', nargs='+', help='input files')
    parser.add_argument(
        '-o', '--output', nargs='+', required=True,
        help='output files. If unspecified, no normalization is done, but information about the target volume is still displayed. If there is only one output file and it is non-existent or a directory, it is treated as a directory and the input file names will be reused relatively to it.')
    parser.add_argument('-c', '--encoder', help='output encoder')
    parser.add_argument('-q', '--quality', help='quality (-q:a) argument')
    parser.add_argument('--ext', help="Target extension (including leading dot) to replace output file extensions with.")
    parser.add_argument('--ffmpeg-path', default=shutil.which('ffmpeg'), help='ffmpeg executable path')
    parser.add_argument('-x', action='store_true', help="print every ffmpeg invocation ('set -x' mode)")
    parser.add_argument('-c:d', action='store_true', dest='c_d', help='copy the video streams')
    parser.add_argument('-c:s', action='store_true', dest='c_s', help='copy the subtitle streams')
    parser.add_argument('-c:v', action='store_true', dest='c_v', help='copy the data streams')
    parser.add_argument('--two-pass', action='store_true', help='use two-pass encoding')
    parser.add_argument('-b', '--max-bitrate', type=float, default=math.inf, help='cap the average bitrate (kbps)')

    overwrite_options = parser.add_mutually_exclusive_group()
    overwrite_options.add_argument('-y', action='store_true', dest='overwrite', help='Overwrite output files',)
    overwrite_options.add_argument(
        '-n', action='store_false', dest='overwrite', default=False,
        help='Do not overwrite output files, and exit immediately if a specified output file already exists (default)')

    parser.add_argument(
        '--onerror', choices={'stop', 'ignore'},
        default='stop',
        help="action on non-zero exit code from ffmpeg. 'stop' exits with the exit code of the faulty ffmpeg call. 'ignore' ignores the error.")

    a = parser.parse_args()

    log = functools.partial(print, file=sys.stderr)

    if a.output:
        if len(a.output) == 1 and (not path.exists(a.output[0]) or path.isdir(a.output[0])):
            output_dir = path.abspath(a.output[0])
            common_head = path.commonpath(map(path.abspath, a.input))
            output_files = tuple(path.join(output_dir, path.relpath(input_file, common_head)) for input_file in a.input)
            log(format_info(f"Expanded output dir '{output_dir}' into {len(output_files)} files"))
        elif len(a.output) != len(a.input):
            parser.error(f'got ({len(a.input)}) input files for ({len(a.output)}) output files')
        else:
            output_files = a.output

        if a.ext:
            output_files = tuple(path.splitext(o)[0] + a.ext for o in output_files)
    else:
        output_files = tuple()

    try:
        normalize_volume(Args(input_files=a.input,
                              output_files=output_files,
                              output_encoder=a.encoder,
                              ffmpeg_path=a.ffmpeg_path,
                              set_x_mode=a.x,
                              onerror=a.onerror,
                              quality=a.quality,
                              log=log,
                              max_bitrate=a.max_bitrate,
                              mode=a.mode,
                              overwrite=a.overwrite,
                              two_pass=a.two_pass,
                              copyd=a.c_d,
                              copys=a.c_s,
                              copyv=a.c_v,
                              global_opts=('-nostdin',)))
    except sp.CalledProcessError as e:
        if e.stdout:
            print(indent(e.stdout.decode(), 4), file=sys.stderr)
        print(format_error(f'{e} (stdout above, stderr below)'), file=sys.stderr)
        if e.stderr:
            print(indent(e.stderr.decode(), 4), file=sys.stderr)
        exit(e.returncode)
    except FileExistsError as e:
        print(format_error(e), file=sys.stderr)
        exit(e.errno)
    except NormalizationError as e:
        print(indent(e.output, 4), file=sys.stderr)
        print(format_error(f'{e.msg} (wrong output above)'), file=sys.stderr)
        exit(65)
