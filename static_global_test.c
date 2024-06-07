#include <stdio.h>

typedef struct {
    int value;
} Object;

static int gs_val;

static Object gs_obj;

int main() {
    printf("%d %d\n", gs_val, gs_obj.value);

    gs_val = 5;
    gs_obj = (Object) { .value = 5 };

    printf("%d %d\n", gs_val, gs_obj.value);
}