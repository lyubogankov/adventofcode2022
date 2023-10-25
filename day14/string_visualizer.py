import solution
from solution import Board, SandUnit, Point

def board_as_string(board: Board, sandunit: SandUnit, viewbounds: tuple[Point]):
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
            elif curr in board.settled_sand or (sandunit and curr == sandunit.current_coords):
                board_str += 'o'
            elif curr == board.sand_origin_pt:
                board_str += '+'
            else:
                board_str += '.'
        if y < bottomright.y:
            board_str += '\n'

def print_board(board: Board, sandunit: SandUnit, viewbounds: tuple[Point]):
    for line in board_as_string(board, sandunit, viewbounds).split('\n'):
        print(line)

if __name__ == '__main__':
    board = solution.create_board(filepath='example.txt', sand_origin=Point(500, 0))
    print_board(board, sandunit=None, viewbounds=(Point(494, 0), Point(503, 9)))