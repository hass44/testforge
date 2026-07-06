"""Hard: matrix operations with validation."""


class Matrix:
    def __init__(self, data: list[list[float]]):
        if not data or not data[0]:
            raise ValueError("Matrix cannot be empty")
        row_len = len(data[0])
        for row in data:
            if len(row) != row_len:
                raise ValueError("All rows must have equal length")
        self.data = [row[:] for row in data]
        self.rows = len(data)
        self.cols = row_len

    def get(self, row: int, col: int) -> float:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            raise IndexError("Index out of bounds")
        return self.data[row][col]

    def add(self, other: "Matrix") -> "Matrix":
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions")
        result = [
            [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ]
        return Matrix(result)

    def transpose(self) -> "Matrix":
        result = [
            [self.data[i][j] for i in range(self.rows)]
            for j in range(self.cols)
        ]
        return Matrix(result)

    def scalar_multiply(self, scalar: float) -> "Matrix":
        result = [
            [self.data[i][j] * scalar for j in range(self.cols)]
            for i in range(self.rows)
        ]
        return Matrix(result)

    def to_list(self) -> list[list[float]]:
        return [row[:] for row in self.data]
