from typing import Literal

import collections


class TronPlayer:
    def __init__(
        self,
        name: str,
        color: str,
        dir: Literal["up", "down", "left", "right"] = "right",
        head: tuple[int, int] = (0, 0),
    ):
        self.name = name
        self.color = color
        self.dir = dir
        self.head = head

        self.trail = set()

    def next_move(
        self,
        width: int,
        height: int,
        opponent_trail: set,
        opponent_head: tuple[int, int],
    ) -> tuple[int, int]:
        x, y = self.head
        if self.dir == "up":
            y -= 1
        elif self.dir == "down":
            y += 1
        elif self.dir == "left":
            x -= 1
        elif self.dir == "right":
            x += 1
        return (x, y)

    def move_to(self, x: int, y: int):
        self.head = (x, y)
        self.trail.add(self.head)

    def is_manully_controlled(self):
        return True


class TronBot(TronPlayer):
    def __init__(
        self,
        name: str,
        color: str,
        dir: Literal["up", "down", "left", "right"] = "right",
        head: tuple[int, int] = (0, 0),
    ):
        super().__init__(name, color, dir, head)

    def next_move(
        self,
        width: int,
        height: int,
        opponent_trail: set,
        opponent_head: tuple[int, int],
    ) -> tuple[int, int]:
        x, y = self.head

        directions = {
            "up": (x, y - 1, "down"),
            "down": (x, y + 1, "up"),
            "left": (x - 1, y, "right"),
            "right": (x + 1, y, "left"),
        }

        all_obstacles = set()
        all_obstacles.update(self.trail)
        all_obstacles.update(opponent_trail)

        valid_moves = {}

        for d_name, (nx, ny, opposite) in directions.items():
            if self.dir == opposite:
                continue

            if nx <= 0 or nx >= width - 1 or ny <= 0 or ny >= height - 1:
                continue

            if (nx, ny) in all_obstacles:
                continue
            valid_moves[d_name] = (nx, ny)

        if self.dir in valid_moves:
            return valid_moves[self.dir]

        if valid_moves:
            chosen_dir = list(valid_moves.keys())[0]
            self.dir = chosen_dir
            return valid_moves[chosen_dir]

        return super().next_move(width, height, opponent_trail, opponent_head)

    def is_manully_controlled(self):
        return False
