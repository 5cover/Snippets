# Exercices

Current page :

## 1.4

This function returns a + b if a > 0 and a - b if a < 0.

It is equivalent to a + |b|.

## 1.5

### Applicative order

(test 0 (p))

(if (= 0 0) 0 (p))

(0)

### Normal order

(test 0 (p))

Infinite recursion

## 1.6

Depending on the order strategy, sqrt-iter may be always evaluated, even if the condition evalutes to false.

This causes infinite recursion.
