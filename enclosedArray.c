#include <stdio.h>
#include <stdlib.h>

#include "macros.h"

#define VALARRAY(type, length) struct { type at[length]; }
#define VALARRAY_SIZE(arr) ARRAY_LENGTH(arr.at)

typedef VALARRAY(int, 5) Array5Int;

typedef VALARRAY(char, 128) ShortString;

Array5Int addToEach(Array5Int array, int n)
{
    Array5Int result;
    for(int i = 0; i < VALARRAY_SIZE(array); ++i) {
        result.at[i] = n + array.at[i];
    }
    return result;
}

int main()
{
    Array5Int array = {{1,2,3,4,5}};

    array = addToEach(array, 2);
    
    for(int i = 0; i < VALARRAY_SIZE(array); ++i) {
        printf("%d\n", array.at[i]);
    }

    return 0;
}

