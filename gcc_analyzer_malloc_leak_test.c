// compile command: gcc-12 -Wall -Wextra -pedantic -fanalyzer -fsanitize=leak -g -Og test.c -o test && ./test && rm test
// testing malloc leak static analysis

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

typedef struct {
    // dynamic array inside dynamic array of structure : works
    int *dynArray;
} Cell;

typedef struct {
    // dynamic array inside structure : works
    Cell *cells;
    size_t size;
} Grid;


Grid grid_create(size_t arraySize) {
    Grid grid = (Grid) {
        .size = arraySize,
    };

    // Allocate outer array
    grid.cells = malloc(arraySize * sizeof *grid.cells);
    assert(grid.cells != NULL);

    // Allocate inner arrays
    for (size_t i = 0; i < arraySize; ++i) {
        grid.cells[i].dynArray = malloc(arraySize * sizeof *grid.cells[i].dynArray);
        assert(grid.cells[i].dynArray != NULL);
    }

    return grid;
}

void grid_destroy(Grid *grid) {
    for (size_t i = 0; i < grid->size; ++i) {
        free(grid->cells[i].dynArray);
    }
    free(grid->cells);
}

int main() {
    int n = 5;

    Grid grid = grid_create(n);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            grid.cells[i].dynArray[j] = i + j;
        }
        
    }

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            printf("%d ", grid.cells[i].dynArray[j]);
        }
        putchar('\n');
    }

    grid_destroy(&grid);
}
