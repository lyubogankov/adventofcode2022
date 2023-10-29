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
from common.point import BoundingBox, Point_2D as Point #noqa: E402

# pairwise = itertools.pairwise
def pairwise(collection):
    for i in range(0, len(collection) - 1):
        yield (collection[i], collection[i+1])

PUZZLE_SAND_ORIGIN = Point(500, 0)

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
        self.cave_floor_y = math.inf # by default, no floor = abyss
        self.rock_bounding_box = None
        self.viewport = None # user-set, overrides self.rock_bounding_box

    def is_tile_occupied(self, tile: Point):
        return tile in self.rocks \
            or tile in self.settled_sand \
            or tile.y == self.cave_floor_y

    def add_rock(self, coords: Point) -> None:
        self.rocks.add(coords)
        self.largest_x  = max(coords.x, self.largest_x)
        self.largest_y  = max(coords.y, self.largest_y)
        self.smallest_x = min(coords.x, self.smallest_x)
        self.smallest_y = min(coords.y, self.smallest_y)
        self.rock_bounding_box = BoundingBox(
            topleft=Point(self.smallest_x, self.smallest_y),
            bottomright=Point(self.largest_x, self.largest_y)
        )

class SandUnit:
    def __init__(self, starting_coords: Point):
        self.current_coords = starting_coords
        self.at_rest = False
        self.falling_indefinitely = False

    def fall_step(self, board: Board):
        if not board.is_tile_occupied(below := self.current_coords + Point(x=0, y=1)):
            self.current_coords = below
        elif not board.is_tile_occupied(downleft := self.current_coords + Point(x=-1, y=1)):
            self.current_coords = downleft
        elif not board.is_tile_occupied(downright := self.current_coords + Point(x=1, y=1)):
            self.current_coords = downright
        else:
            self.at_rest = True
            board.settled_sand.add(self.current_coords)

def create_board(filepath: str, sand_origin: Point=PUZZLE_SAND_ORIGIN) -> Board:
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
    if board.cave_floor_y == math.inf \
            and moving_sand_unit.current_coords not in (board.viewport if board.viewport else board.rock_bounding_box):
        moving_sand_unit.falling_indefinitely = True

def run_simulation_frame_generator(board: Board, create_board_frame_fn = None, sand_unit_limit=math.inf, time_steps_between_sand_unit_drops=None):
    if create_board_frame_fn:
        yield create_board_frame_fn(board, sand_units=[])
    
    num_sand_blocks_dropped = 0
    time_step = 0

    falling_sand_units = []
    
    while num_sand_blocks_dropped < sand_unit_limit or falling_sand_units:
        # simulate time step - move all currently falling sand units, if needed spawn a new one
        for sand_unit in falling_sand_units:
            simulate_time_step(board, moving_sand_unit=sand_unit)

        if ((time_steps_between_sand_unit_drops and time_step % time_steps_between_sand_unit_drops == 0) \
                or falling_sand_units == []) \
                and num_sand_blocks_dropped < sand_unit_limit:
            falling_sand_units.append(SandUnit(board.sand_origin_pt))
            num_sand_blocks_dropped += 1
        time_step += 1

        # now, remove the units that are not at rest
        falling_sand_units = [s for s in falling_sand_units if not s.at_rest]

        # create simulation frame
        if create_board_frame_fn:
            yield create_board_frame_fn(board, sand_units=falling_sand_units)

        # test for loop break conditions
        if any(s.falling_indefinitely for s in falling_sand_units):
            sand_unit_limit = num_sand_blocks_dropped
        if board.sand_origin_pt in board.settled_sand:
            break

def run_simulation(board: Board, create_board_frame_fn = None, sand_unit_limit=math.inf, time_steps_between_sand_unit_drops=None):
    return list(run_simulation_frame_generator(board, create_board_frame_fn, sand_unit_limit, time_steps_between_sand_unit_drops))

def obtain_path_of_indefinitely_falling_sand_unit(board: Board, viewbounds: BoundingBox):
    """Need to pass in a board that is already in a "completed" state"""
    sand_unit = SandUnit(board.sand_origin_pt)
    fall_path = []
    while sand_unit.current_coords in viewbounds:
        fall_path.append(sand_unit.current_coords)
        sand_unit.fall_step(board)
    return fall_path

def obtain_part_one_simulated_board(inputfile: str, sand_origin: Point=PUZZLE_SAND_ORIGIN) -> Board:
    board = create_board(filepath=inputfile, sand_origin=sand_origin)
    run_simulation(board=board)
    return board

def obtain_part_two_board(inputfile: str, sand_origin: Point=PUZZLE_SAND_ORIGIN, floor_offset=2) -> Board:
    board = create_board(filepath=inputfile, sand_origin=sand_origin)
    board.cave_floor_y = board.largest_y + floor_offset
    return board

def obtain_part_two_simulated_board(inputfile: str, sand_origin: Point=PUZZLE_SAND_ORIGIN, floor_offset=2) -> Board:
    board = obtain_part_two_board(inputfile, sand_origin, floor_offset)
    run_simulation(board=board)
    return board

if __name__ == '__main__':
    ### part one - how many sand units come to rest with abyss?
    board = obtain_part_one_simulated_board(inputfile='input.txt')
    print(f'[1] Number of sand units at rest: {len(board.settled_sand)}')
    ### part two - how many sand units come to rest with cave floor?
    board = obtain_part_two_simulated_board(inputfile='input.txt')
    print(f'[2] Number of sand units at rest: {len(board.settled_sand)}')

    # import cProfile
    # cProfile.run("obtain_part_two_simulated_board(inputfile='example.txt', sand_origin=Point(500, -35))", 'sim_stats')
    # import pstats
    # p = pstats.Stats('sim_stats')
    # p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()