#include <stdio.h>
#include <stdlib.h>

float const Z = 100;
float const K = 10;

int main()
{
    float x = Z * K / (K + 1);
    float y = Z * 1 / (K + 1);

    printf("x + y = %g et x / y = %g\nx = %g\ny = %g\n", Z, K, x, y);

    return EXIT_SUCCESS;
}