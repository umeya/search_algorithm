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


class MazeState():
    dx: List[int]
    dy: List[int]
    point_: List[List[int]]
    turn_: int
    character_: Coord
    game_score_: int

    evaluated_score_: int


    def __init__(self, point:List[List[int]]=[[0]], turn:int=-1, game_score:int=-1, char_y:int=-1, char_x:int=-1) -> None:
        if char_x == -1 and char_y == -1:
            self.point_ = [[0 for _ in range(CONST_W)] for _ in range(CONST_H)]
            self.turn_ = 0
            self.character_ = Coord()
            self.game_score_ = 0
            self.character_.y_, self.character_.x_ = 0, 0
        else:
            self.point_ = [[c for c in r] for r in point]
            self.turn_ = turn
            self.character_ = Coord()
            self.game_score_ = game_score
            self.character_.y_, self.character_.x_ = char_y, char_x
        self.dx = [1, -1, 0, 0]
        self.dy = [0, 0, 1, -1]
        self.evaluated_score_ = self.game_score_

        
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

    def evaluate_score(self):
        self.evaluated_score_ = self.game_score_

class Greedy():
    
    mz:MazeState
    
    def __init__(self):
        self.mz = MazeState()
        
    def random_action(self):
        legal_actions: list = self.mz.legal_action()
        return legal_actions[random.randint(0, len(legal_actions) - 1)]

    

    def greedy_action(self):
        best_score: int = -sys.maxsize
        best_action: int = -1
        legal_actions: list = self.mz.legal_action()

        for action in legal_actions:
            now_mz = MazeState(self.mz.point_, self.mz.turn_, self.mz.game_score_, self.mz.character_.y_, self.mz.character_.x_)
            now_mz.advance(action)
            now_mz.evaluate_score()
            if now_mz.evaluated_score_ > best_score:
                best_score = now_mz.evaluated_score_
                best_action = action
            del  now_mz
        return best_action

    def play_game(self) -> None:
        self.mz.generate_maze()
        self.mz.print_maze_state()
        while not self.mz.is_done():
            # self.mz.advance(self.mz.random_action())
            self.mz.advance(self.greedy_action())
            self.mz.print_maze_state()


if __name__ == '__main__':
    gr = Greedy()
    gr.play_game()
