from functools import partial
import os
import time

import solution
from solution import Board, SandUnit, Point, BoundingBox

def board_as_string(board: Board, sand_unit: SandUnit, viewbounds: BoundingBox, fall_path=[]):
    board_str = ""
    # top -> bottom, left -> right
    topleft, bottomright = viewbounds.topleft, viewbounds.bottomright
    for y in range(topleft.y, bottomright.y + 1):
        for x in range(topleft.x, bottomright.x + 1):
            curr = Point(x, y)
            if curr in board.rocks:
                board_str += '#'
            elif curr in board.settled_sand or (sand_unit and curr == sand_unit.current_coords):
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

def animate_frames(create_board_frame_fn, inputfile: str, sand_origin: Point, frame_delay=0.3):
    for i, frame in enumerate(solution.run_simulation(
            inputfile=inputfile,
            sand_origin=sand_origin,
            create_board_frame_fn=create_board_frame_fn)):
        os.system('cls')  # windows only
        print(frame)
        time.sleep(frame_delay)

def generate_falling_sand_block_path(inputfile: str, sand_origin: Point, viewbounds: BoundingBox):
    # get a fresh board
    board = solution.create_board(filepath=inputfile, sand_origin=sand_origin)
    # run the sim to obtain final board state
    solution.run_simulation(board=board, create_board_frame_fn=lambda board, sand_unit: None)
    # trace fall path
    fall_path_points = solution.obtain_path_of_indefinitely_falling_sand_unit(board, viewbounds)
    # generate / return string!
    return board_as_string(board, sand_unit=None, viewbounds=viewbounds, fall_path=fall_path_points)

if __name__ == '__main__':
    # animate_frames(
    #     inputfile='example.txt',
    #     sand_origin=solution.PUZZLE_SAND_ORIGIN,
    #     create_board_frame_fn=partial(board_as_string, viewbounds=BoundingBox(Point(494, 0), Point(503, 9)))
    # )

    # print(generate_falling_sand_block_path(
    #     inputfile='example.txt',
    #     sand_origin=Point(x=500, y=0),
    #     viewbounds=BoundingBox(topleft=Point(x=493, y=0), bottomright=Point(x=503, y=12))
    # ))

    board = solution.obtain_part_two_simulated_board(inputfile='example.txt')
    print(board_as_string(board, sand_unit=None, viewbounds=BoundingBox(Point(488, 0), Point(512, 11))))