import random
from typing import List
import sys
import time
import math

#  global constants
MAZE_WIDTH_: int = 5  # 迷路の幅
MAZE_HEIGHT_: int = 5  # 迷路の高さ
GAME_END_TURN_: int = 5  # ゲーム終了のターン
GAME_NUMBERS_:int = 10000 # ゲーム回数
CHARACTER_N: int = 3  # キャラクターの数
ACTIONS: int = 4  # 移動方向　右(0)、左(1)、下(2)、上(3)
DX: List[int] = [1, -1, 0, 0]
DY: List[int] = [0, 0, 1, -1]
PRINT_STATE_: bool = True

INF: int = sys.maxsize
F_INF:float = float('inf')


class Coord:
    y_: int
    x_: int

    def __init__(self, y: int = 0, x: int = 0):
        self.y_, self.x_ = y, x


class AutoMoveMazeState():
    point_: List[List[int]]
    turn_: int
    characters_: List[Coord]
    game_score_: int
    evaluated_score_: int

    def __init__(self, turn: int = -1, point: List[List[int]] = [[0]],
                 characters: List[Coord] = [], game_score: int = -1) -> None:
        if turn == -1:
            self.turn_ = 0
            self.point_ = [[random.randint(1, 9) for _ in range(MAZE_WIDTH_)] for _ in range(MAZE_HEIGHT_)]
            # ---- test
            # self.point_ = [[9, 1, 3, 7, 8], [7, 8, 2, 2, 1], [9, 3, 7, 4, 2], [3, 1, 1, 6, 4], [9, 3, 9, 3, 9]]
            # -----
            self.characters_ = []
            for _ in range(CHARACTER_N):
                cd = Coord()
                self.characters_.append(cd)
            self.game_score_ = 0
        else:
            self.turn_ = turn
            self.point_ = [[c for c in r] for r in point]
            self.characters_ = [Coord(cd.y_, cd.x_) for cd in characters]
            self.game_score_ = game_score

        self.evaluated_score_ = 0

    def is_done(self):
        return self.turn_ == GAME_END_TURN_

    def set_character(self, character_id: int, y: int, x: int) -> None:
        self.characters_[character_id].y_ = y
        self.characters_[character_id].x_ = x

    def move_player(self, character_id: int) -> None:
        character: Coord = self.characters_[character_id]
        best_point: int = -INF
        best_action_index: int = 0
        for action in range(ACTIONS):
            ty, tx = character.y_ + DY[action], character.x_ + DX[action]
            if (0 <= ty < MAZE_HEIGHT_) and (0 <= tx < MAZE_WIDTH_):
                if (point := self.point_[ty][tx]) > best_point:
                    best_point = point
                    best_action_index = action
        character.y_ += DY[best_action_index]
        character.x_ += DX[best_action_index]
        self.characters_[character_id] = character

    def advance(self):
        for character_id in range(CHARACTER_N):
            self.move_player(character_id)
        for character in self.characters_:
            self.game_score_ += self.point_[character.y_][character.x_]
            self.point_[character.y_][character.x_] = 0
        self.turn_ += 1

    def random_action(self) -> None:
        for character_id in range(CHARACTER_N):
            self.set_character(character_id,
                               random.randint(0, MAZE_HEIGHT_ - 1),
                               random.randint(0, MAZE_WIDTH_ - 1))
        # ----- test
        # for i, (y, x) in enumerate([(3, 0), (3, 4), (4, 4)]):
        #     self.set_character(i, y, x)
        # ----------

    def initial_solution(self):
        for id in range(CHARACTER_N):
            self.characters_[id].y_ = random.randint(0, MAZE_HEIGHT_ - 1)
            self.characters_[id].x_ = random.randint(0, MAZE_WIDTH_ - 1)

    def transition(self):
        id = random.randint(0, CHARACTER_N - 1)
        self.characters_[id].y_ = random.randint(0, MAZE_HEIGHT_ - 1)
        self.characters_[id].x_ = random.randint(0, MAZE_WIDTH_ - 1)

    def print_maze_state(self) -> None:
        charcters = [(id.y_, id.x_) for id in self.characters_]
        print(f'turn_={self.turn_} , game_score_={self.game_score_}', end=':charcters ')
        for id in self.characters_:
            print(f'{id.y_, id.x_} ', end='')
        print('')
        for h in range(MAZE_HEIGHT_):
            for w in range(MAZE_WIDTH_):
                if (h, w) in charcters:
                    print("@", end='')
                elif self.point_[h][w] > 0:
                    print(self.point_[h][w], end='')
                else:
                    print(".", end='')
            print()


class SimulatedAnnealing():
    now_state: AutoMoveMazeState
    next_state: AutoMoveMazeState
    characters_path: List[List[Coord]]
    best_characters: List[Coord]
    score_path: List[int]

    def __init__(self):
        self.characters_path = []
        self.best_characters = []
        self.score_path = []

    def get_score(self, state: AutoMoveMazeState, is_print: bool = False) -> int:
        tmp_state: AutoMoveMazeState = AutoMoveMazeState(
            state.turn_, state.point_,
            state.characters_, state.game_score_)
        for character in state.characters_:
            tmp_state.point_[character.y_][character.x_] = 0
        while not tmp_state.is_done():
            tmp_state.advance()
            if is_print:
                tmp_state.print_maze_state()
        return tmp_state.game_score_

    def play_game(self, numbers: int = 10, start_temp:float = 500.0, end_temp:float = 10.0) -> None:
        now_score:int
        next_score: int
        best_score: int
        temp:float
        probability: float
        is_force_next: bool

        random.seed(int(time.time()))
        now_state = AutoMoveMazeState()
        now_state.initial_solution()
        total_number:int = sum(sum(x) for x in now_state.point_) \
            - sum(now_state.point_[cd.y_][cd.x_] for cd in now_state.characters_)

        print(f'  ------------ initial state (total numbers in maze = {total_number=})')
        now_state.print_maze_state()

        now_characters = [cd for cd in now_state.characters_]
        self.characters_path.append(now_characters)
        best_score = self.get_score(now_state)
        now_score = best_score
        self.best_characters = now_characters
        self.score_path.append(best_score)
        for i in range(numbers):
            next_state: AutoMoveMazeState = AutoMoveMazeState(
                now_state.turn_, now_state.point_,
                now_characters, now_state.game_score_
            )
            next_state.transition()
            characters = [Coord(cd.y_, cd.x_) for cd in next_state.characters_]
            next_score = self.get_score(next_state)
            temp = start_temp + (end_temp - start_temp)*(i / numbers)
            probability = math.exp((next_score - now_score) / temp)
            is_force_next = (probability > (random.random() ))
            if next_score > now_score or is_force_next:
                now_score = next_score
                now_characters = characters
            if next_score > best_score:
                best_score = next_score
                self.best_characters = characters
                self.characters_path.append(characters)
                self.score_path.append(next_score)

        print(' -------------- solution')
        if PRINT_STATE_ and len(self.characters_path) < 100:
            print('        --- charcters  :  score')
            for i in range(len(self.characters_path)):
                self.print_path(self.score_path[i], self.characters_path[i])
        now_state.characters_ = self.best_characters
        now_state.print_maze_state()
        best_score_ = self.get_score(now_state, PRINT_STATE_)
        scoring_rate:float = best_score_ / total_number
        print()
        print(f'Score of simulated annealing: {best_score_=} , scoring_rate={scoring_rate:.4f} ')

    def print_path(self, score: int, characters: List[Coord]):
        """for test """
        for cd in characters:
            print(f'{cd.y_, cd.x_}, ', end='')
        print(f'  :  {score=}')

    def set_const(self):
        global MAZE_WIDTH_, MAZE_HEIGHT_, GAME_END_TURN_, PRINT_STATE_, GAME_NUMBERS_

        try:
            args = "".join(sys.argv[1:]).split('--')[1:]
            for arg in args:
                argkv = arg.split('=')
                k = argkv[0].upper()
                if k == "PRINT_STATE":
                    if argkv[1].upper() == 'Y':
                        PRINT_STATE_ = True
                    else:
                        PRINT_STATE_ = False
                    continue
                v = int(argkv[1])
                if k == "MAZE_WIDTH":
                    MAZE_WIDTH_ = v
                elif k == "MAZE_HEIGHT":
                    MAZE_HEIGHT_ = v
                elif k == "GAME_END_TURN":
                    GAME_END_TURN_ = v
                elif k == "GAME_NUMBERS":
                    GAME_NUMBERS_ = v
                else:
                    raise Exception()
        except:
            print('args error in comandoline, the command line is written as follows')
            print(
                './simulated_annealing_py MAZE_WIDTH=4 --MAZE_HEIGHT=3 --GAME_END_TURN=4 --PRINT_STATE=y --GAME_NUMBERS=10000')
            sys.exit(0)
        print(f'maze_state: {MAZE_WIDTH_=} {MAZE_HEIGHT_=} {GAME_END_TURN_=} {PRINT_STATE_=} {GAME_NUMBERS_=}')


stime = time.time()
sa = SimulatedAnnealing()
sa.set_const()
sa.play_game(10000)
etime = time.time()
print(f'処理時間 {etime - stime}(秒)')

"""

"""