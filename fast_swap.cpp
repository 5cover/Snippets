#include <iostream>

template <class T>
void swap(T&, T&);

int main()
{
    auto a = 4;
    auto b = 5;
    std::cout << a << ' ' << b << '\n';
    swap(a, b);
    std::cout << a << ' ' << b << '\n';

    return 0;
}

template <class T>
void swap(T& a, T& b) {
    a ^= b;
    b ^= a;
    a ^= b;
}

