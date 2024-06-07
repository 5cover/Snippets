/// @brief Declares and dynamically allocates a bidimensional array of the specified size.
/// @param type The type of the array
/// @param name The name of the variable to declare
/// @param rows the number of rows of the matrix
/// @param cols the number of columns of the matrix
/// @remark The array is in row-major order.
/// @remark @ref free must be called for destruction.
/// @remark This macro is used to abstract the confusing C99 dynamic n-dimensional array syntax.
#define create_matrix(type, name, rows, cols) type (*name)[cols] = malloc(rows * sizeof *name)

/// @brief Expands to the right part of a dynamic bidimensional array type. Must be preceded by the element type.
#define matrix(name, cols) (*name)[cols]