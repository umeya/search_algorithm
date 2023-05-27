import random
from typing import List
import sys
import time


class Coord:
    y_: int
    x_: int

    def __init__(self, x: int = 0, y: int = 0):
        self.y_, self.x_ = y, x


CONST_H: int = 3  # 迷路の長さ
CONST_W: int = 4  # 迷路の幅
END_TURN: int = 4  # ゲーム終了のターン


class RandomAction():
    dx: List[int]
    dy: List[int]
    point_: List[List[int]]
    turn_: int
    character_: Coord
    game_score_: int

    evaluated_score_: int

    # stack for maze state
    stk_point_: List[List[List[int]]]
    stk_turn_: List[int]
    stk_character_x_: List[int]
    stk_character_y_: List[int]
    stk_game_score_: List[int]

    def __init__(self) -> None:
        self.point_ = [[0 for _ in range(CONST_W)] for _ in range(CONST_H)]
        self.turn_ = 0
        self.character_ = Coord()
        self.game_score_ = 0
        self.character_.y_, self.character_.x_ = 0, 0
        self.dx = [1, -1, 0, 0]
        self.dy = [0, 0, 1, -1]

        self.evaluated_score_ = self.game_score_

        self.stk_point_ , self.stk_turn_, self.stk_character_x_, self.stk_character_y_, \
            self.stk_game_score_   = [], [], [], [], []
    def generate_maze(self) -> None:
        self.turn_ = 0
        self.game_score_ = 0
        random.seed(int(time.time()))
        self.character_.y_, self.character_.x_ \
            = random.randint(0, CONST_H - 1), random.randint(0, CONST_W - 1)
        for y in range(CONST_H):
            for x in range(CONST_W):
                if y == self.character_.y_ and x == self.character_.x_:
                    continue
                else:
                    self.point_[y][x] = random.randint(0, 9)

    def is_done(self) -> bool:
        return self.turn_ == END_TURN

    def advance(self, action: int) -> None:
        self.character_.x_ += self.dx[action]
        self.character_.y_ += self.dy[action]
        point = self.point_[self.character_.y_][self.character_.x_]
        if point > 0:
            self.game_score_ += point
            self.point_[self.character_.y_][self.character_.x_] = 0
        self.turn_ += 1

    def legal_action(self) -> list:
        actions = []
        for action in range(len(self.dx)):
            ty: int = self.character_.y_ + self.dy[action]
            tx: int = self.character_.x_ + self.dx[action]
            if (0 <= ty < CONST_H) and (0 <= tx < CONST_W):
                actions.append(action)
        return actions

    def print_maze_state(self) -> None:
        print(f'turn_={self.turn_} , game_score_={self.game_score_} , ', end='')
        print(f'character_(y_,x_)=({self.character_.y_},{self.character_.x_})')
        for h in range(CONST_H):
            for w in range(CONST_W):
                if self.character_.y_ == h and self.character_.x_ == w:
                    print("@", end='')
                elif self.point_[h][w] > 0:
                    print(self.point_[h][w], end='')
                else:
                    print(".", end='')
            print()

    def stack_maze_state(self):
        self.stk_point_.append([ [c for c in r] for r in self.point_])
        self.stk_turn_.append(self.turn_)
        self.stk_character_x_.append(self.character_.x_)
        self.stk_character_y_.append(self.character_.y_)
        self.stk_game_score_.append(self.game_score_)

    def pop_maze_state(self):
        self.point_ = [[c for c in r] for r in  self.stk_point_.pop()]
        self.turn_ = self.stk_turn_.pop()
        self.character_.x_ = self.stk_character_x_.pop()
        self.character_.y_ = self.stk_character_y_.pop()
        self.game_score_ = self.stk_game_score_.pop()

    def random_action(self):
        legal_actions: list = self.legal_action()
        return legal_actions[random.randint(0, len(legal_actions) - 1)]

    def evaluate_score(self):
        self.evaluated_score_ = self.game_score_


    def greedy_action(self):
        best_score:int = -sys.maxsize
        best_action:int = -1
        legal_actions: list = self.legal_action()
        for action in legal_actions:
            self.stack_maze_state()
            self.advance(action)
            self.evaluate_score()
            if self.evaluated_score_ > best_score:
                best_score = self.evaluated_score_
                best_action = action
            self.pop_maze_state()
        return best_action

    def play_game(self) -> None:
        self.generate_maze()
        self.print_maze_state()
        while not self.is_done():
            self.advance(self.random_action())
            self.print_maze_state()


if __name__ == '__main__':
    rz = RandomAction()
    rz.play_game()
