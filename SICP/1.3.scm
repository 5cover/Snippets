; Ex 1.3

(define (f a b c)
    (cond ((and (<= a b) (<= a c)) (+ (* b b) (* c c)))
          ((and (<= b a) (<= b c)) (+ (* c c) (* a a)))
          (else (+ (* a a) (* b b)))
    )
)