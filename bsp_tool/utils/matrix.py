from __future__ import annotations
from typing import List


# TODO: generic MxN matrix class
# TODO: vector.vec3 methods
# -- vec3 -> Mat3x1 * Mat3x3 -> vec3
# -- vec3 -> Mat4x1 * Mat


class Mat4x4:
    array: List[List[float]]

    def __init__(self, array=None, cells=dict()):
        if array is None:  # start as an identity matrix
            self.array = [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]]
        else:
            self.array = array
        for (i, j), value in cells.items():
            self[i][j] = value

    def __repr__(self) -> str:
        # return "\n".join([
        #     " ".join(["[", *[f"{self[i][j]}" for j in range(4)],"]"])
        #     for i in range(4)])
        return "".join([
            "Mat4x4([\n",
            ",\n".join([
                " " * 4 + str(self.array[i])
                for i in range(4)]),
            "])"])

    def __getitem__(self, index):
        return self.array[index]

    def __eq__(self, other) -> bool:
        if not isinstance(other, Mat4x4):
            return False
        return all(
            self[i][j] == other[i][j]
            for i in range(4)
            for j in range(4))

    def __add__(self, other: Mat4x4) -> Mat4x4:
        if not isinstance(other, Mat4x4):
            type_ = other.__class__.__name__
            raise NotImplementedError(f"cannot add Mat4x4 with '{type_}'")
        return self.do(lambda i, j: self[i][j] + other[i][j])

    def __mul__(self, other: Mat4x4) -> Mat4x4:
        if isinstance(other, (int, float)):
            return self.do(lambda i, j: self[i][j] * other)
        elif isinstance(other, Mat4x4):
            return self.do(lambda i, j: sum(
                self[i][x] * other[x][j]
                for x in range(4)))
        else:
            type_ = other.__class__.__name__
            raise NotImplementedError(f"cannot multiply Mat4x4 by '{type_}'")

    def do(self, func) -> Mat4x4:
        """powerhouse of the cell"""
        out = Mat4x4()
        for i in range(4):
            for j in range(4):
                out.array[i][j] = func(i, j)
        return out

    def is_valid(self) -> bool:
        return all([
            len(self.array) == 4,
            all(
                len(row) == 4
                for row in self.array),
            all(
                isinstance(cell, (int, float))
                for row in self.array
                for cell in row)])

    def transpose(self) -> Mat4x4:
        return self.do(lambda i, j: self.array[j][i])
