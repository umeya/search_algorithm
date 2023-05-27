import random
from typing import List
import sys
import time



class Coord:
    y_: int
    x_: int

    def __init__(self, x: int = 0, y: int = 0):
        self.y_, self.x_ = y, x


MAZE_HEIGHT_: int = 4  # 迷路の長さ
MAZE_WIDTH_: int = 3  # 迷路の幅
END_TURN: int = 4  # ゲーム終了のターン

BEAM_WIDTH_:int = 2
BEAM_DEPTH_:int = 4


class MazeState():
    dx: List[int]
    dy: List[int]
    point_: List[List[int]]
    turn_: int
    character_: Coord
    game_score_: int

    evaluated_score_: int

    first_action_:int

    def __init__(self, point: List[List[int]] = [[0]], turn: int = -1, game_score: int = -1, char_y: int = -1,
                 char_x: int = -1) -> None:
        if char_x == -1 and char_y == -1:
            self.point_ = [[0 for _ in range(MAZE_WIDTH_)] for _ in range(MAZE_HEIGHT_)]
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
        self.first_action_ = -1

    def generate_maze(self, seed:int = int(time.time())) -> None:
        self.turn_ = 0
        self.game_score_ = 0
        random.seed(seed)
        self.character_.y_, self.character_.x_ \
            = random.randint(0, MAZE_HEIGHT_ - 1), random.randint(0, MAZE_WIDTH_ - 1)
        for y in range(MAZE_HEIGHT_):
            for x in range(MAZE_WIDTH_):
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
            if (0 <= ty < MAZE_HEIGHT_) and (0 <= tx < MAZE_WIDTH_):
                actions.append(action)
        return actions

    def print_maze_state(self) -> None:
        print(f'turn_={self.turn_} , game_score_={self.game_score_} , ', end='')
        print(f'character_(y_,x_)=({self.character_.y_},{self.character_.x_})')
        for h in range(MAZE_HEIGHT_):
            for w in range(MAZE_WIDTH_):
                if self.character_.y_ == h and self.character_.x_ == w:
                    print("@", end='')
                elif self.point_[h][w] > 0:
                    print(self.point_[h][w], end='')
                else:
                    print(".", end='')
            print()

    def evaluate_score(self):
        self.evaluated_score_ = self.game_score_


class TestAiScore():
    mz: MazeState

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
            now_mz = MazeState(self.mz.point_, self.mz.turn_, self.mz.game_score_, self.mz.character_.y_,
                               self.mz.character_.x_)
            now_mz.advance(action)
            now_mz.evaluate_score()
            if now_mz.evaluated_score_ > best_score:
                best_score = now_mz.evaluated_score_
                best_action = action
            del now_mz
        return best_action

    def play_game(self) -> None:
        self.mz.generate_maze()
        self.mz.print_maze_state()
        while not self.mz.is_done():
            # self.mz.advance(self.mz.random_action())
            self.mz.advance(self.greedy_action())
            self.mz.print_maze_state()

    def beam_search(self, BEAM_WIDTH_=2, BEAM_DEPTH_:int=4):
        best_state:MazeState
        now_beam:List[MazeState]
        next_beam: List[MazeState]
        next_beam_index: int
        next_beam_indexes: List[int]
        now_state: MazeState
        leagal_actions: List[int]
        next_state:MazeState

        best_first_action:int
        best_is_done:bool

        now_beam = [self.mz]

        for d in range(BEAM_DEPTH_):
            next_beam = []

            for w in range(BEAM_WIDTH_):
                if len(now_beam) == 0:
                    break
                now_state = now_beam.pop()
                leagal_actions = now_state.legal_action()
                for action in leagal_actions:
                    next_state = MazeState(now_state.point_, now_state.turn_, now_state.game_score_,
                                  now_state.character_.y_, now_state.character_.x_)
                    next_state.advance(action)
                    next_state.evaluate_score()
                    if d == 0:
                        next_state.first_action_ = action
                    else:
                        next_state.first_action_ = now_state.first_action_
                    next_beam.append(next_state)
            l:int = len(next_beam)
            for i in range(l-1):
                if i >= BEAM_WIDTH_:
                    break
                best_score = next_beam[i].game_score_
                for j in range(i+1, l):
                    if best_score < next_beam[j].game_score_:
                        best_score = next_beam[j].game_score_
                        next_beam[i], next_beam[j] = next_beam[j], next_beam[i]
                if i == 0:
                    best_first_action = next_beam[i].first_action_
                    best_is_done = next_beam[i].is_done()
            now_beam = []
            for i, m in enumerate(next_beam):
                if i >= BEAM_WIDTH_:
                    break
                now_beam.append(m)
            if best_is_done:
                break
        return best_first_action

    def test_ai_score(self, game_number:int = 10):
        stime = time.time()

         # ---- beam search score
        score_total: int = 0
        for i in range(game_number):
            self.mz.generate_maze()
            while not self.mz.is_done():
                self.mz.advance(self.beam_search())
            score_total += self.mz.game_score_
        print(f'beam search score : {score_total / game_number}')

        etime = time.time()
        print(f'処理時間 {etime-stime}(秒)')

if __name__ == '__main__':
    tas = TestAiScore()
    tas.test_ai_score(1000000)

"""
"""