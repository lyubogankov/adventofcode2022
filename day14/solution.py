"""
1. parse input file into internal repreesntation of the "game board" - the 2D position of the rocks in space
2. simulate the sand falling - need to have a concept of "time steps".  there are rules evaluated for the currently falling sand block per time step.
    - Need to track
        - board (rocks)
        - currently falling sand block (treated specially, as it moves until it comes to rest)
        - all sand blocks that have already come to rest
3. Want to have different "visualizers" - each consumes a current board state (or maybe a list of all board states as "frames" (like animation)) and display them
    - generate string (for unit tests, printing to terminal)
    - GUI-based (for nice animation of falling sand, visuzlization of full solution) - pyglet package?

"""
# import itertools
import math
import sys

sys.path.append(r'C:\Users\lg\Documents\code\adventofcode2022')
from common.point import Point_2D as Point  #nolint E402

# pairwise = itertools.pairwise
def pairwise(collection):
    for i in range(0, len(collection) - 1):
        yield (collection[i], collection[i+1])

# this is the internal representation of the 2D cave slice
class Board:
    """Program representation of 2D cave slice.
    +x = right, -x = left
    +y = down,  -y = up
    """
    def __init__(self, sand_origin: Point):
        self.sand_origin_pt = sand_origin
        self.rocks = set()
        self.settled_sand = set()
        # keeping track of smallest/largest x/y
        # - used to determine when a sand block has "fallen off the board"
        # - may be useful to Visualizers
        self.smallest_x = self.largest_x = sand_origin.x
        self.smallest_y = self.largest_y = sand_origin.y

    def occupied_tiles(self):
        return self.rocks.union(self.settled_sand)

    def add_rock(self, coords: Point) -> None:
        self.rocks.add(coords)
        self.largest_x  = max(coords.x, self.largest_x)
        self.largest_y  = max(coords.y, self.largest_y)
        self.smallest_x = min(coords.x, self.smallest_x)
        self.smallest_y = min(coords.y, self.smallest_y)

class SandUnit:
    def __init__(self, starting_coords: Point):
        self.current_coords = starting_coords
        self.at_rest = False
        self.falling_indefinitely = False

    def fall_step(self, board: Board):
        if (below := self.current_coords + Point(x=0, y=1)) not in board.occupied_tiles():
            self.current_coords = below
        elif (downleft := self.current_coords + Point(x=-1, y=1)) not in board.occupied_tiles():
            self.current_coords = downleft
        elif (downright := self.current_coords + Point(x=1, y=1)) not in board.occupied_tiles():
            self.current_coords = downright
        else:
            self.at_rest = True
            board.settled_sand.add(self.current_coords)

def create_board(filepath: str, sand_origin: Point) -> Board:
    board = Board(sand_origin)
    with open(filepath, 'r') as input:
        lines = input.readlines()
    for line in lines:
        # per line, parse format into list of Points representing line ends
        line_ends = []
        for coord_str in line.rstrip().split(' -> '):
            x, y = coord_str.split(',')
            line_ends.append(Point(int(x), int(y)))
        # now, look at adjacent point pairs to create set of rocks within the line        
        for (start, end) in pairwise(line_ends):
            # calculate which direction we are travelling over the line
            if start.x == end.x:
                iterator = Point(x=0, y=1) if start.y < end.y else Point(x=0, y=-1)
            elif start.y == end.y:
                iterator = Point(x=1, y=0) if start.x < end.x else Point(x=-1, y=0)
            else:
                raise RuntimeError("ruh roh, didn't expect a line not parallel to x or y axis")
            # add rocks to the board!
            current_point = start
            while current_point != end + iterator:
                board.add_rock(current_point)
                current_point = current_point + iterator
    return board

def simulate_time_step(board: Board, moving_sand_unit: SandUnit):
    moving_sand_unit.fall_step(board)
    # detect if we're in "falling" state for current sand block
    if moving_sand_unit.current_coords.x > board.largest_x \
            or moving_sand_unit.current_coords.y > board.largest_y \
            or moving_sand_unit.current_coords.x < board.smallest_x \
            or moving_sand_unit.current_coords.y < board.smallest_y:
        moving_sand_unit.falling_indefinitely = True

def run_simulation(inputfile: str, sand_origin: Point, create_board_frame_fn, board: Board = None, sand_unit_limit=math.inf):
    frames = []
    
    if board is None:
        board = create_board(inputfile, sand_origin)
    frames.append(create_board_frame_fn(board, sand_unit=None))

    num_sand_blocks_dropped = 0
    while num_sand_blocks_dropped < sand_unit_limit:
        # spawn a new sand unit from origin
        sand_unit = SandUnit(board.sand_origin_pt)
        frames.append(create_board_frame_fn(board, sand_unit))
        # drop it!
        while not sand_unit.at_rest and not sand_unit.falling_indefinitely:
            simulate_time_step(board, moving_sand_unit=sand_unit)
            frames.append(create_board_frame_fn(board, sand_unit))
        # if this sand unit is in free fall, all others will also be
        if sand_unit.falling_indefinitely:
            break
        
        num_sand_blocks_dropped += 1

    return frames

    # TODO: after the sim is run, use a "tracer" sand unit to see the path of falling sand!