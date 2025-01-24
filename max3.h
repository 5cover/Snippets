#define max3(a, b, c) \
    a > b             \
        ? a > c       \
            ? a       \
            : c       \
    : b > c ? b       \
            : c