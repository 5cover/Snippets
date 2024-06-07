#!/usr/bin/env python3

from dataclasses import dataclass
from os import path
from typing import IO, Sequence, Optional, Callable, Any, NamedTuple, TypeAlias
import argparse as ap
import functools
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
    max_volume: float
    bitrate: float

    def __str__(self):
        return f'{self.max_volume} dB, {self.bitrate} kb/s'


@dataclass(frozen=True)
class Args:
    copyd: bool
    copys: bool
    copyv: bool
    ffmpeg_path: str
    global_opts: Sequence[str]
    input_files: Sequence[str]
    log: Callable[..., None]
    onerror: str
    output_encoder: Optional[str]
    output_files: Optional[Sequence[str]]
    set_x_mode: bool

    def ffmpeg(
            self, args: Sequence[str],
            *, allow_failure=False, stdout: FILE = None, stderr: FILE = None, capture_output: bool = False) -> sp.CompletedProcess:
        args = (self.ffmpeg_path,) + args + self.global_opts
        if self.set_x_mode:
            print('+', sp.list2cmdline(args), file=sys.stderr)
        cp = sp.run(args, stdout=stdout, stderr=stderr, capture_output=capture_output)
        if not allow_failure and self.onerror == 'stop':
            cp.check_returncode()
        return cp


def normalize_volume(args: Args):
    args.log('Normalizing', len(args.input_files), 'files')

    if args.output_files:
        for nFile, (IN_F, OUT_F) in enumerate(zip(args.input_files, args.output_files, strict=True), start=1):
            def ffmpeg_io(input_args: tuple[str], output_args: tuple[str]) -> sp.CompletedProcess:
                ffmpeg_args = input_args + ('-b:a', f'{BITRATE}k',
                                            '-stats', '-loglevel', 'warning') \
                    + (('-c:s', 'copy') if args.copys else ('-sn',)) \
                    + (('-c:v', 'copy') if args.copyv else ('-vn',)) \
                    + (('-c:d', 'copy') if args.copyd else ('-dn',)) \
                    + output_args
                if args.output_encoder:
                    ffmpeg_args += '-c:a', args.output_encoder
                return args.ffmpeg(ffmpeg_args, stdout=sp.PIPE, stderr=sp.PIPE)

            args.log(f'({nFile}/{len(args.input_files)})')

            VOL, BITRATE = get_audio_info(args, IN_F)

            pathlib.Path(OUT_F).parent.mkdir(parents=True, exist_ok=True)

            if VOL >= 0:
                args.log(f"'{IN_F}' has max volume >= 0 ({VOL}), copying to '{OUT_F}'")
                ffmpeg_io(('-i', IN_F), (OUT_F,))
                continue

            args.log(f"normalizing '{IN_F}' to '{OUT_F}': {-VOL} dB")
            ffmpeg_io(('-i', IN_F, '-filter:a', f'volume={-VOL}dB'), (OUT_F,))
            new_volume = get_audio_info(args, OUT_F).max_volume
            if new_volume != 0:
                args.log(format_warning(f"'{OUT_F}' max volume is {new_volume} afer normalization."))


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
        max_volume=float(match_output('max volume', f'max_volume: ({REGEXP_FLOAT}) dB')),
        bitrate=float(match_output('bitrate', fr'Audio: .*, ({REGEXP_FLOAT}) kb/s')))
    args.log(f'{input_file}: {info}')
    return info


def indent(text: str, count: int) -> str:
    prefix = ' ' * count
    return prefix + text.replace('\n', '\n' + prefix)


def format_error(msg: Any) -> str:
    return format_message('error', msg, 'red')


def format_warning(msg: Any) -> str:
    return format_message('warning', msg, 'yellow')


def format_message(cat: str, msg: Any, color: str):
    return tc.colored(f'{path.basename(sys.argv[0])}: {cat}: {msg}', color=color)


if __name__ == '__main__':
    parser = ap.ArgumentParser(description='Normalize audio files by peak volume',
                               formatter_class=ap.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', nargs='+', help='input files')
    parser.add_argument(
        '-o', '--output', nargs='+', required=True,
        help='output files. If unspecified, no normalization is done. If there is only one output file and it is a directory, the input file names will be reused.')
    parser.add_argument('-c', '--encoder', help='output encoder')
    parser.add_argument('--ext', help="Target extension (including leading dot) to replace output file extensions with.")
    parser.add_argument('--ffmpeg-path', default=shutil.which('ffmpeg'), help='ffmpeg executable path')
    parser.add_argument('-q', '--quiet', action='store_true', help='quiet output')
    parser.add_argument('-x', action='store_true', help="print every ffmpeg call ('set -x' mode)")
    parser.add_argument('-c:d', action='store_true', dest='c_d', help="copy the video streams")
    parser.add_argument('-c:s', action='store_true', dest='c_s', help="copy the subtitle streams")
    parser.add_argument('-c:v', action='store_true', dest='c_v', help="copy the data streams")

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

    log = (lambda *_: None) if a.quiet else functools.partial(print, file=sys.stderr)

    if a.output:
        if len(a.output) == 1 and path.isdir(a.output[0]):
            log("Expanding output dir.")
            output_dir = path.abspath(a.output[0])
            common_head = path.commonpath(map(path.abspath, a.input))
            output_files = tuple(path.join(output_dir, path.relpath(input_file, common_head)) for input_file in a.input)
        elif len(a.output) != len(a.input):
            parser.error(f'got ({len(a.input)}) input files for ({len(a.output)}) output files')
        else:
            output_files = a.output

        if a.ext:
            output_files = tuple(path.splitext(o)[0] + a.ext for o in output_files)
    else:
        output_dir = tuple()
    try:
        normalize_volume(Args(input_files=a.input,
                              output_files=output_files,
                              output_encoder=a.encoder,
                              ffmpeg_path=a.ffmpeg_path,
                              set_x_mode=a.x,
                              onerror=a.onerror,
                              log=log,
                              copyd=a.c_d,
                              copys=a.c_s,
                              copyv=a.c_v,
                              global_opts=('-nostdin', '-y' if a.overwrite else '-n')))
    except sp.CalledProcessError as e:
        if e.stdout:
            print(indent(e.stdout.decode(), 4), file=sys.stderr)
        print(format_error(f'{e} (stdout above, stderr below)'), file=sys.stderr)
        if e.stderr:
            print(indent(e.stderr.decode(), 4), file=sys.stderr)
        exit(e.returncode)
    except NormalizationError as e:
        print(indent(e.output, 4), file=sys.stderr)
        print(format_error(f'{e.msg} (wrong output above)'), file=sys.stderr)
        exit(65)
