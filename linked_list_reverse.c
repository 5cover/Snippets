#include <stddef.h>

struct list;

struct list {
    void *item;
    struct list *next;
};

struct list *reverse(struct list *list)
{
    struct list *next, *prev = NULL;
    while (list) {
        next = list->next;
        list->next = prev; 
        prev = list;
        list = next;
    }
    return prev;
}


/*
A <- B
B <- C

B -> A
C -> B

C -> B -> A
4 -> 5 -> 6
4    4    5
  
 /-----------------------------\
 |                             V
next <- list->next <- prev <- list

1 -> 2 -> 3 -> 4 -> NULL

\#|next|list->next|prev|list
-|--|--|--|--
0||2|NULL|1
1|2|NULL|1|2

prev=NULL
list=1

1 -> NULL
prev=1
list=2

NULL <- 1    2 -> 3 -> 4 -> NULL

2 -> 1
prev=2
list=3

NULL <- 1 <- 2    3 -> 4 -> NULL

3 -> 2
prev=3
list=4

NULL <- 1 <- 2 <- 3    4 -> NULL

4 -> 3
prev=4
list=NULL

NULL <- 1 <- 2 <- 3 <- 4
*/
