// opaque shell type template
// replace TYPE with your type

// interface: TYPE.h

typedef union {
    char _[sizeof(int) * 2];
    int _align;
} TYPE_t;

// implementation: TYPE.c

#include <stdio.h>

struct TYPE {
    int valueA, valueB;
};

_Static_assert(sizeof(struct TYPE) == sizeof(TYPE_t),
    "TYPE: shell and opaque types must have same size");
_Static_assert(_Alignof(struct TYPE) == _Alignof(TYPE_t),
    "TYPE: shell and opaque types must have same alignment");

#define O(t) ((struct t *)(t))

void TYPE_init(TYPE_t *TYPE, int value)
{
    O(TYPE)->valueB = (O(TYPE)->valueA = value) / 2;
}

void TYPE_put(TYPE_t *TYPE)
{
    printf("%d %d\n", O(TYPE)->valueA, O(TYPE)->valueB);
}

// usage

void no_pointer_needed(void)
{
    TYPE_t shell = {0};
    TYPE_init(&shell, 19);
    TYPE_put(&shell);
}
