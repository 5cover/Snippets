void va_advance_printf(va_list *ap, const char *fmt) {
    while (*fmt) {
        if (*fmt++ == '%') { // Found format specifier
            while (*fmt == '-'
                || *fmt == '+'
                || *fmt == ' '
                || *fmt == '#'
                || *fmt == '0') {
                fmt++;
            }
            if (*fmt == '*') {
                fmt++;
                va_arg(*ap, int);
            } else while ('0' <= *fmt && *fmt <= '9') {
                fmt++;
            }
            if (*fmt == '.') {
                fmt++;
                if (*fmt == '*') {
                    fmt++;
                    va_arg(*ap, int);
                } else while ('0' <= *fmt && *fmt <= '9') {
                    fmt++;
                }
            }
            switch (*fmt) {
            case 'h':
                switch (*(fmt + 1)) {
                case 'h':
                    switch (*(fmt + 2)) {
                    case 'd':
                    case 'i': fmt += 3; va_arg(*ap, int); break; // signed char
                    case 'o':
                    case 'x':
                    case 'X':
                    case 'u': fmt += 3; va_arg(*ap, int); break; // unsigned char
                    case 'n': fmt += 3; va_arg(*ap, signed char *); break;
                    }
                    break;
                case 'd':
                case 'i': fmt += 2; va_arg(*ap, int); break; // short
                case 'o':
                case 'x':
                case 'X':
                case 'u': fmt += 2; va_arg(*ap, int); break; // unsigned short
                case 'n': fmt += 2; va_arg(*ap, short *); break;
                }
                break;
            case 'c': fmt++; va_arg(*ap, int); break;
            case 's': fmt++; va_arg(*ap, char *); break;
            case 'd':
            case 'i': fmt++; va_arg(*ap, int); break;
            case 'o':
            case 'x': fmt++; va_arg(*ap, unsigned int); break;
            case 'X': fmt++; va_arg(*ap, unsigned int); break;
            case 'u': fmt++; va_arg(*ap, unsigned int); break;
            case 'f':
            case 'F':
            case 'e':
            case 'E':
            case 'a':
            case 'A':
            case 'g':
            case 'G': fmt++; va_arg(*ap, double); break;
            case 'n': fmt++; va_arg(*ap, int *); break;
            case 'p': fmt++; va_arg(*ap, void *); break;
            case 'l':
                switch (*(fmt + 1)) {
                case 'c': fmt += 2; va_arg(*ap, wint_t); break;
                case 's': fmt += 2; va_arg(*ap, wchar_t *); break;
                case 'd':
                case 'i': fmt += 2; va_arg(*ap, long); break;
                case 'o':
                case 'x':
                case 'X':
                case 'u': fmt += 2; va_arg(*ap, unsigned long); break;
                case 'f':
                case 'F':
                case 'e':
                case 'E':
                case 'a':
                case 'A':
                case 'g':
                case 'G': fmt += 2; va_arg(*ap, double); break;
                case 'n': fmt += 2; va_arg(*ap, long *); break;
                case 'l':
                    switch (*(fmt + 2)) {
                    case 'd':
                    case 'i': fmt += 3; va_arg(*ap, long long); break;
                    case 'o':
                    case 'x':
                    case 'X':
                    case 'u': fmt += 3; va_arg(*ap, unsigned long long); break;
                    case 'n': fmt += 3; va_arg(*ap, long long *); break;
                    }
                    break;
                }
                break;
            case 'j':
                switch (*(fmt + 1)) {
                case 'd':
                case 'i': fmt += 2; va_arg(*ap, intmax_t); break;
                case 'o':
                case 'x':
                case 'X':
                case 'u': fmt += 2; va_arg(*ap, uintmax_t); break;
                case 'n': fmt += 2; va_arg(*ap, intmax_t *); break;
                }
                break;
            case 'z':
                switch (*(fmt + 1)) {
                case 'd':
                case 'i': fmt += 2; va_arg(*ap, ssize_t); break;
                case 'o':
                case 'x':
                case 'X':
                case 'n': fmt += 2; va_arg(*ap, size_t *); break;
                case 'u': fmt += 2; va_arg(*ap, size_t); break;
                }
                break;
            case 't':
                switch (*(fmt + 1)) {
                case 'd':
                case 'i': fmt +=2; va_arg(*ap, ptrdiff_t); break;
                case 'o':
                case 'x':
                case 'X':
                case 'u': fmt += 2; va_arg(*ap, unsigned long); break; // uptrdiff_t
                case 'n': fmt += 2; va_arg(*ap, ptrdiff_t *); break;
                }
                break;
            case 'L':
                switch (*(fmt + 1)) {
                case 'f':
                case 'F':
                case 'e':
                case 'E':
                case 'a':
                case 'A':
                case 'g':
                case 'G': fmt += 2; va_arg(*ap, long double); break;
                }
                break;
            }
        }
    }
}
