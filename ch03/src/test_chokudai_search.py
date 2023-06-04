import random
from typing import List
import sys
import time


class Coord:
    y_: int
    x_: int

    def __init__(self, x: int = 0, y: int = 0):
        self.y_, self.x_ = y, x

MIN_VALUE_:int = -1

MAZE_DIRS_:int = 4
MAZE_DX_:List[int] = [1, -1, 0, 0]
MAZE_DY_:List[int] = [0, 0, 1, -1]

MAZE_WIDTH_: int = 30  # 迷路の幅
MAZE_HEIGHT_: int = 30  # 迷路の高さ
GAME_END_TURN_: int = 100  # ゲーム終了のターン
PRINT_STATE_:bool = False
BEAM_WIDTH_:int = 1
BEAM_DEPTH_:int = 4
BEAM_NUMBER_:int = 2


class MazeState():
    point_: List[List[int]]
    turn_: int
    character_: Coord
    game_score_: int
    evaluated_score_: int
    first_action_:int
    selected_:bool
    # parent_maze_index:tuple
    # from_action:int

    def __init__(self, point: List[List[int]] = [[0]], turn: int = MIN_VALUE_, game_score: int = MIN_VALUE_, char_y: int = MIN_VALUE_,
                 char_x: int = MIN_VALUE_) -> None:
        if char_x == MIN_VALUE_ and char_y == MIN_VALUE_:
            self.point_ = [[0 for _ in range(MAZE_WIDTH_)] for _ in range(MAZE_HEIGHT_)]
            self.turn_ = 0
            self.game_score_ = 0
            self.character_ = Coord()
            self.character_.y_, self.character_.x_ = 0, 0
        else:
            self.point_ = [[c for c in r] for r in point]
            self.turn_ = turn
            self.character_ = Coord()
            self.game_score_ = game_score
            self.character_.y_, self.character_.x_ = char_y, char_x


        self.evaluated_score_ = self.game_score_
        self.first_action_ = MIN_VALUE_
        self.selected_ = False

    def generate_maze(self, seed:int = int(time.time())) -> None:

        self.turn_ = 0
        self.game_score_ = 0
        random.seed(seed)
        self.character_.y_, self.character_.x_ \
            = random.randint(0, MAZE_HEIGHT_ - 1), random.randint(0, MAZE_WIDTH_ - 1)

        # ---- for test
        # tp=[[4, 6, 1, 3], [0,0,2,0],[7,5,6,6]]
        # self.character_.y_, self.character_.x_ = 1,1
        # -----------
        for y in range(MAZE_HEIGHT_):
            for x in range(MAZE_WIDTH_):
                if y == self.character_.y_ and x == self.character_.x_:
                    continue
                else:
                    self.point_[y][x] = random.randint(0, 9)
                    # self.point_[y][x] = tp[y][x]               # -- for test

    def is_done(self) -> bool:
        return self.turn_ == GAME_END_TURN_

    def advance(self, action: int) -> None:

        self.character_.x_ += MAZE_DX_[action]
        self.character_.y_ += MAZE_DY_[action]
        point = self.point_[self.character_.y_][self.character_.x_]
        if point > 0:
            self.game_score_ += point
            self.point_[self.character_.y_][self.character_.x_] = 0
        self.turn_ += 1

    def legal_action(self) -> list:
        actions = []
        for action in range(MAZE_DIRS_):
            ty: int = self.character_.y_ + MAZE_DY_[action]
            tx: int = self.character_.x_ + MAZE_DX_[action]
            if (0 <= ty < MAZE_HEIGHT_) and (0 <= tx < MAZE_WIDTH_):
                actions.append(action)
        return actions

    def print_maze_state(self) -> None:
        print(f'turn_={self.turn_} , game_score_={self.game_score_} , ', end='')
        print(f'character_(y_,x_)=({self.character_.y_},{self.character_.x_})')
        print(f'                        ------ {self.first_action_=} , {self.selected_=}')
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

    def get_index_of_max_gamescore(self, states:List[MazeState], ignore_slelection:bool = False):
        max_score, max_score_index, i = MIN_VALUE_, -1, -1
        for i, state in enumerate(states):
            if ignore_slelection:
                if state.game_score_ > max_score:
                    max_score, max_score_index = state.game_score_, i
            if not state.selected_ and state.game_score_ > max_score:
                max_score, max_score_index = state.game_score_, i
        return max_score_index


    def chokudai_search(self, BEAM_WIDTH_=1, BEAM_DEPTH_:int=4, BEAM_NUMBER_:int=2):
        each_turn_mazes:List[List[MazeState]]

        each_turn_mazes = [[self.mz]]
        parent_turn = self.mz.turn_
        turn_depth = GAME_END_TURN_ - parent_turn
        if turn_depth < BEAM_DEPTH_:
            last_turn_offset = turn_depth
        else:
            last_turn_offset = BEAM_DEPTH_

        for _ in range(last_turn_offset+1):
            each_turn_mazes.append([])

        for action in each_turn_mazes[0][0].legal_action():
            first_state = MazeState(
                each_turn_mazes[0][0].point_, each_turn_mazes[0][0].turn_, each_turn_mazes[0][0].game_score_,
                each_turn_mazes[0][0].character_.y_, each_turn_mazes[0][0].character_.x_)
            first_state.first_action_ = action
            first_state.advance(action)
            each_turn_mazes[1].append(first_state)

        if last_turn_offset > 1:
            for beam_number in range(BEAM_NUMBER_):
                for t_offset in range(1, last_turn_offset+1):
                    next_turn = t_offset + 1
                    next_state_list = []
                    for w in range(BEAM_WIDTH_):
                        if (idx := self.get_index_of_max_gamescore(each_turn_mazes[t_offset])) == -1:
                            break
                        each_turn_mazes[t_offset][idx].selected_ = True
                        now_state = each_turn_mazes[t_offset][idx]
                        if now_state.is_done():
                            break
                        leagal_actions = now_state.legal_action()
                        for action in leagal_actions:
                            next_state = MazeState(now_state.point_, now_state.turn_, now_state.game_score_,
                                                   now_state.character_.y_, now_state.character_.x_)
                            next_state.first_action_ = now_state.first_action_
                            next_state.advance(action)
                            next_state_list.append(next_state)
                    if len(next_state_list) > 0:
                        for m in next_state_list:
                            each_turn_mazes[next_turn].append(m)
                    else:
                        break

                # print(f'///// {beam_number=}')
                # for i, t in enumerate(each_turn_mazes):
                #     print(f'        ---- t_offset={i}')
                #     for m in t:
                #         m.print_maze_state()


        idx = self.get_index_of_max_gamescore(each_turn_mazes[last_turn_offset], ignore_slelection=True)
        best_first_action = each_turn_mazes[last_turn_offset][idx].first_action_


        # bs = each_turn_mazes[last_turn_offset][idx].game_score_
        # print(f'**** {last_turn_offset=} , {idx}:{best_first_action=}, game_score={bs} **')

        del each_turn_mazes
        return best_first_action


    def play_game(self, BEAM_WIDTH_:int=1, BEAM_DEPTH_:int=4) -> None:
        self.mz.generate_maze()
        print(' ----- start maze state')
        self.mz.print_maze_state()
        while not self.mz.is_done():
            self.mz.advance(self.chokudai_search(BEAM_WIDTH_, BEAM_DEPTH_, BEAM_NUMBER_))
            if PRINT_STATE_:
                print('-------advanced')
                self.mz.print_maze_state()
        print(' ----- end maze state')
        self.mz.print_maze_state()

    def set_const(self):
        global MAZE_WIDTH_, MAZE_HEIGHT_, GAME_END_TURN_, PRINT_STATE_, BEAM_WIDTH_, BEAM_DEPTH_, BEAM_NUMBER_
        MAZE_WIDTH_, MAZE_HEIGHT_, GAME_END_TURN_ = 4, 3, 4
        PRINT_STATE_ = False
        BEAM_WIDTH_, BEAM_DEPTH = 1, 4
        BEAM_NUMBER_ = 2

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
                elif k == "BEAM_WIDTH":
                    BEAM_WIDTH_ = v
                elif k == "BEAM_DEPTH":
                    BEAM_DEPTH_ = v
                elif k == "BEAM_NUMBER_":
                    BEAM_NUMBER_ = v
                else:
                    raise Exception()
            print(f'{MAZE_WIDTH_=}, {MAZE_HEIGHT_=}, {GAME_END_TURN_=}, {PRINT_STATE_=}, {BEAM_WIDTH_=}, {BEAM_DEPTH_=}, {BEAM_NUMBER_=}')
        except:
            print('args error in comandoline, the command line is written as follows')
            print(
                './test_chokudai_search MAZE_WIDTH=4 --MAZE_HEIGHT=3 --GAME_END_TURN=4 --PRINT_STATE=y --BEAM_WIDTH=2 --BEAM_DEPTH=4')
            sys.exit(0)

    def test_ai_score(self, game_number: int = 10):

        stime = time.time()

        # ---- chokudai search score
        score_total: int = 0
        for i in range(game_number):
            self.mz.generate_maze()
            while not self.mz.is_done():
                self.mz.advance(self.chokudai_search(BEAM_WIDTH_, BEAM_DEPTH_, BEAM_NUMBER_))
            score_total += self.mz.game_score_

        print(f'chokudai search score : {score_total / game_number}')

        etime = time.time()
        print(f'処理時間 {etime - stime}(秒)')


if __name__ == '__main__':
    tas = TestAiScore()
    tas.set_const()
    tas.test_ai_score(100)

