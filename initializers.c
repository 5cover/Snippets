#include <stdio.h>

typedef struct {
    int f0, f1, f2, f3, f4, f5;
} S;

int main()
{
    int arr[6] = { 1, [3] = 2, 3 };
    for (int i = 0; i < 6; ++i) {
        printf("%d ", arr[i]);
    }
    puts("");

    S s = { 1, .f3 = 2, 3 };
    for (int i = 0; i < 6; ++i) {
        printf("%d ", ((int*)&s)[i]);
    }

    return 0;
}
