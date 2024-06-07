#ifndef MACROS_H
#define MACROS_H

/// @brief Determines the length of a static array.
#define ARRAYLENGTH(array) (sizeof(array) / sizeof((array)[0]))

/// @brief Determines the length of a string literal.
#define STRLEN(s) (sizeof(s) / sizeof(char) - 1)

/// @brief Foreach loop construct.
#define foreach(type, varName, array, count) for ( \
    type *varName = array;                         \
    varName != array + count;                      \
    ++varName)

/// @brief Checks if i is a valid index of an array of length length.
#define IN_ARRAY_BOUNDS(i, length) (0 <= (i) && (i) < (length))

/// @brief Determines whether 2 strings are equal using strcmp.
#define streq(str1, str2) (strcmp((str1), (str2)) == 0)

/// @brief Determines whether 2 strings are equal using strncmp.
#define streqn(str1, str2, n) (strncmp((str1), (str2), (n)) == 0)

#ifdef __GNUC__

#define max(a,b)             \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a > _b ? _a : _b;       \
})

#define min(a,b)             \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a < _b ? _a : _b;       \
})

#else

#define max(a,b) ((a) > (b) ? (a) : (b))
#define min(a,b) ((a) < (b) ? (a) : (b))

#endif // __GNUC__

#endif // MACROS_H