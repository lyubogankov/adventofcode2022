from functools import partial
import os
import sys
import time

import solution
from solution import Board, SandUnit, Point, BoundingBox, PUZZLE_SAND_ORIGIN

if sys.platform == 'win32':
    CLEAR_SCREEN_CMD = 'cls'
elif sys.platform == 'linux':
    CLEAR_SCREEN_CMD = 'clear'

def board_as_string(board: Board, sand_units, viewbounds: BoundingBox, fall_path=[]):
    board_str = ""
    # top -> bottom, left -> right
    topleft, bottomright = viewbounds.topleft, viewbounds.bottomright
    for y in range(topleft.y, bottomright.y + 1):
        for x in range(topleft.x, bottomright.x + 1):
            curr = Point(x, y)
            if curr in board.rocks or curr.y == board.cave_floor_y:
                board_str += '#'
            elif curr in board.settled_sand or (sand_units and any(curr == s.current_coords for s in sand_units)):
                board_str += 'o'
            elif curr == board.sand_origin_pt:
                board_str += '+'
            elif curr in fall_path:
                board_str += '~'
            else:
                board_str += '.'
        if y < bottomright.y:
            board_str += '\n'
    return board_str

def animate_frames(board: Board, viewbounds: BoundingBox, frame_delay=0.3):
    for i, frame in enumerate(solution.run_simulation(
            board=board,
            create_board_frame_fn=partial(board_as_string, viewbounds=viewbounds))):
        os.system(CLEAR_SCREEN_CMD)
        print(frame)
        time.sleep(frame_delay)

def generate_falling_sand_block_path(inputfile: str, viewbounds: BoundingBox, sand_origin: Point = PUZZLE_SAND_ORIGIN):
    # get a fresh board
    board = solution.create_board(filepath=inputfile, sand_origin=sand_origin)
    # run the sim to obtain final board state
    solution.run_simulation(board=board)
    # trace fall path
    fall_path_points = solution.obtain_path_of_indefinitely_falling_sand_unit(board, viewbounds)
    # generate / return string!
    return board_as_string(board, sand_units=[], viewbounds=viewbounds, fall_path=fall_path_points)

if __name__ == '__main__':
    
    ## part one command line animation
    # board = solution.create_board(filepath='example.txt')
    # animate_frames(board, viewbounds=BoundingBox(Point(494, 0), Point(503, 9)))

    ## part one falling sand unit path
    print(generate_falling_sand_block_path(
        inputfile='example.txt',
        viewbounds=BoundingBox(topleft=Point(x=493, y=0), bottomright=Point(x=503, y=12))
    ))

    ## part two command line animation
    # board = solution.obtain_part_two_board(inputfile='example.txt')
    # animate_frames(board=board, viewbounds=BoundingBox(Point(488, 0), Point(512, 11)), frame_delay=0.005)

    ## part two ending state
    board = solution.obtain_part_two_simulated_board(inputfile='example.txt')
    print(board_as_string(board, sand_units=[], viewbounds=BoundingBox(Point(488, 0), Point(512, 11))))