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
from common.point import Point_2D as Point

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
        self.smallest_x = math.inf
        self.smallest_y = math.inf
        self.largest_x  = -math.inf
        self.largest_y  = -math.inf

    def occupied_tiles(self):
        return self.rocks.union(self.settled_sand)

    def add_rock(self, coords: Point):
        self.rocks.add(coords)
        self.largest_x  = max(coords.x, self.largest_x)
        self.largest_y  = max(coords.y, self.largest_y)
        self.smallest_x = min(coords.x, self.smallest_x)
        self.smallest_y = min(coords.y, self.smallest_y)

class SandUnit:
    def __init__(self, starting_coords: Point):
        self.current_coords = starting_coords
        self.at_rest = False

    def fall_step(self, board: Board):
        if (below := self.current_coords + Point(x=0, y=1)) not in board.occupied_tiles():
            self.current_coords = below
        elif (downleft := self.current_coords + Point(x=-1, y=1)) not in board.occupied_tiles():
            self.current_coords = downleft
        elif (downright := self.current_coords + Point(x=1, y=1)) not in board.occupied_tiles():
            self.current_coords = downright
        else:
            self.at_rest = True

def create_board(filepath: str, sand_origin: Point, printout=False):
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
            if printout:
                print('start:    ', start)
                print('end:      ', end)
                print('iterator: ', iterator)
            # add rocks to the board!
            current_point = start
            while current_point != end + iterator:
                board.add_rock(current_point)
                if printout:
                    print('        added: ', current_point)
                current_point += iterator
    return board


"""
parsing:
- per line, split by the arrow.  Iterate pairwise over the x,y coords - these are the lines of rock.

? how to represent the board, as well as lines of rock?  I'll need to check position of sand vs rocks.
    - set of (point, type) tuples?
    - keep track of the bounds - smallest/largest x, y for in case the display wants to use that info.
        For the unit test printouts, I'll need to manually specify the display view coord window to match
"""