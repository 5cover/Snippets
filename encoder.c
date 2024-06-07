#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Primary component
#define COMP(str, c, len) (((((str - c + 17) << 5) ^ (len * 0xDEDE + (((str - c) | len) ^ 0xBADAFF))) + 0xCECA) / 3)

void encode(char *str)
{
    size_t len = strlen(str);
    for (char *c = str; c < str + len; ++c) {
        *c -= COMP(str, c, len) % (CHAR_MAX - len + 1);
    }
}

void decode(char *str)
{
    size_t len = strlen(str);
    for (char *c = str; c < str + len; ++c) {
        *c += COMP(str, c, len) % (CHAR_MAX - len + 1);
    }
}

void printChars(char const *str)
{
    for (char const *c = str; *c != '\0'; ++c) {
        printf("%ld \t %d = '%c'\n", c - str, *c, *c);
    }
}

int main()
{
    char str[] = "secrets";

    printf("Before : \"%s\"\n", str);
    encode(str);

    printf("Encode : \"%s\"\n", str);
    printChars(str);

    decode(str);

    printf("Decode : \"%s\"\n", str);

    return 0;
}
