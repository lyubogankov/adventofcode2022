from functools import partial
import os
import time

import solution
from solution import Board, SandUnit, Point

def board_as_string(board: Board, sand_unit: SandUnit, viewbounds: tuple[Point]):
    """
    viewbounds: expecting tuple (topleft, bottomright) containing view bounds
    """
    board_str = ""
    # top -> bottom, left -> right
    topleft, bottomright = viewbounds
    for y in range(topleft.y, bottomright.y + 1):
        for x in range(topleft.x, bottomright.x + 1):
            curr = Point(x, y)
            if curr in board.rocks:
                board_str += '#'
            elif curr in board.settled_sand or (sand_unit and curr == sand_unit.current_coords):
                board_str += 'o'
            elif curr == board.sand_origin_pt:
                board_str += '+'
            else:
                board_str += '.'
        if y < bottomright.y:
            board_str += '\n'
    return board_str

create_board_frame_fn = partial(board_as_string, viewbounds=(Point(494, 0), Point(503, 9)))

def animate_frames():
    for i, frame in enumerate(solution.run_simulation(
            inputfile='example.txt',
            sand_origin=Point(500, 0),
            create_board_frame_fn=create_board_frame_fn)):
        os.system('cls')  # windows only
        print(frame)
        time.sleep(0.3)

if __name__ == '__main__':
    # create_board_frame_fn = partial(board_as_string, viewbounds=(Point(494, 0), Point(503, 9)))
    # for i, frame in enumerate(solution.run_simulation(
    #         inputfile='example.txt',
    #         sand_origin=Point(500, 0),
    #         create_board_frame_fn=create_board_frame_fn)):
    #     print(f'===================================== {i+1} ===')
    #     print(frame, end='\n\n')
    animate_frames()