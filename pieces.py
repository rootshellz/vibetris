from typing import List, Tuple

# Colors from main.py
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tetromino definitions
TETROMINOES = {
    "I": {
        "shape": [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        "color": CYAN,
    },
    "O": {"shape": [[2, 2], [2, 2]], "color": YELLOW},
    "T": {"shape": [[0, 0, 0], [3, 3, 3], [0, 3, 0]], "color": MAGENTA},
    "S": {"shape": [[0, 0, 0], [0, 4, 4], [4, 4, 0]], "color": GREEN},
    "Z": {"shape": [[0, 0, 0], [5, 5, 0], [0, 5, 5]], "color": RED},
    "J": {"shape": [[0, 0, 0], [6, 0, 0], [6, 6, 6]], "color": BLUE},
    "L": {"shape": [[0, 0, 0], [0, 0, 7], [7, 7, 7]], "color": ORANGE},
}


class Tetromino:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.shape = TETROMINOES[name]["shape"]
        self.color = TETROMINOES[name]["color"]
        self.x = x  # Top-left corner x position on the grid
        self.y = y  # Top-left corner y position on the grid

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    def rotate(self) -> None:
        # Rotate the shape 90 degrees clockwise
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_positions(self) -> List[Tuple[int, int]]:
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell != 0:
                    positions.append((self.x + x, self.y + y))
        return positions

    def collides(
        self, grid: List[List[Tuple[int, int, int]]], dx: int = 0, dy: int = 0
    ) -> bool:
        grid_width = len(grid[0])
        grid_height = len(grid)
        for x, y in self.get_positions():
            new_x = x + dx
            new_y = y + dy
            if (
                new_x < 0
                or new_x >= grid_width
                or new_y >= grid_height
                or (new_y >= 0 and grid[new_y][new_x] != BLACK)
            ):
                return True
        return False
