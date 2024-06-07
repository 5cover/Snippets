#ifndef CSHARP_H
#define CSHARP_H

#include <stdio.h>
#include <stdint.h>

typedef long double decimal;

typedef unsigned char byte;
typedef signed char sbyte;
#define short int16_t
typedef uint16_t ushort;
#define int int32_t
typedef uint32_t uint;
#define long int64_t
typedef uint64_t ulong;
typedef intptr_t nint;
typedef uintptr_t nuint;

typedef void* dynamic;

typedef struct {

} String;
typedef String string;

struct _console {
    void (*const WriteLine)(char const *);
};

static void _console_WriteLine(char const *str) {
    puts(str);
}

static struct _console const Console = (struct _console) {
    .WriteLine = _console_WriteLine,
};

#endif // CSHARP_H