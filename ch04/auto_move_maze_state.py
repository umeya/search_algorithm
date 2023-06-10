import random
from typing import List
import sys
import time

#  global constants
MAZE_WIDTH_: int = 5  # 迷路の幅
MAZE_HEIGHT_: int = 5  # 迷路の高さ
GAME_END_TURN_: int = 5  # ゲーム終了のターン
CHARACTER_N: int = 3  # キャラクターの数
ACTIONS: int = 4  # 移動方向　右(0)、左(1)、下(2)、上(3)
DX: List[int] = [1, -1, 0, 0]
DY: List[int] = [0, 0, 1, -1]
PRINT_STATE_: bool = True

INF: int = sys.maxsize


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
            self.characters_ = [cd for cd in characters]
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


class RandomAction():
    maze_state: AutoMoveMazeState

    def __init__(self):
        self.maze_state = AutoMoveMazeState()

    def get_score(self, state:AutoMoveMazeState, is_print: bool = False) -> int:
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

    def play_game(self, seed: int = time.time()) -> None:
        random.seed(seed)
        self.maze_state.random_action()
        self.maze_state.print_maze_state()
        self.maze_state.game_score_ = self.get_score(self.maze_state, PRINT_STATE_)
        print()
        print(f'Score of random action: {self.maze_state.game_score_}')

    def set_const(self):
        global MAZE_WIDTH_, MAZE_HEIGHT_, GAME_END_TURN_, PRINT_STATE_

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
                else:
                    raise Exception()
        except:
            print('args error in comandoline, the command line is written as follows')
            print(
                './auto_move_maze_state_py MAZE_WIDTH=4 --MAZE_HEIGHT=3 --GAME_END_TURN=4 --PRINT_STATE=y')
            sys.exit(0)
        print(f'maze_state: {MAZE_WIDTH_=} {MAZE_HEIGHT_=} {GAME_END_TURN_=} {PRINT_STATE_=}')


stime = time.time()
rs = RandomAction()
rs.set_const()
rs.play_game(2023)
etime = time.time()
print(f'処理時間 {etime - stime}(秒)')

"""
test data is  70 page in the text
   comment out line 40,90,91

maze_state: MAZE_WIDTH_=5 MAZE_HEIGHT_=5 GAME_END_TURN_=5 PRINT_STATE_=True
turn_=0 , game_score_=0:charcters (3, 0) (3, 4) (4, 4) 
91378
78221
93742
@116@
9393@
turn_=1 , game_score_=18:charcters (4, 0) (3, 3) (4, 3) 
91378
78221
93742
.11@.
@39@.
turn_=2 , game_score_=34:charcters (4, 1) (2, 3) (4, 2) 
91378
78221
937@2
.11..
.@@..
turn_=3 , game_score_=43:charcters (3, 1) (2, 2) (3, 2) 
91378
78221
93@.2
.@@..
.....
turn_=4 , game_score_=46:charcters (2, 1) (2, 1) (3, 3) 
91378
78221
9@..2
...@.
.....
turn_=5 , game_score_=55:charcters (2, 0) (2, 0) (3, 4) 
91378
78221
@...2
....@
.....

Score of random action: 55
処理時間 0.0010001659393310547(秒)
.....
turn_=4 , game_score_=46:charcters (2, 1) (2, 1) (3, 3) 
91378
78221
9@..2
...@.
.....
turn_=5 , game_score_=55:charcters (2, 0) (2, 0) (3, 4) 
91378
78221
@...2
....@
.....

Score of random action: 55
処理時間 0.0010466575622558594(秒)
"""