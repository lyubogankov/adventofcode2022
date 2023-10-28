import math

import pygame

import solution
from solution import Board, BoundingBox, Point

"""
Procedure for ensuring tile size is an integer # of pixels

1. calculate screen w / h
2. calculate tile size based on mapping between board -> screen with initial width / height
3. truncate tile size to integer
4. re-calculate w / h based on truncated tile size!
"""
def calculate_screen_width_height_tilesize(board, boundingbox):
    MAX_WIDTH = 1500
    MAX_HEIGHT = 800

    board_aspect_ratio = boundingbox.width() / boundingbox.height()

    # want to preserve aspect ratio of board -- want tiles to be square.
    if (preferred_width:= boundingbox.width()*50) <= MAX_WIDTH:
        screen_width = preferred_width
    else:
        screen_width = MAX_WIDTH
    width_preferred_height = screen_width / board_aspect_ratio

    if width_preferred_height <= MAX_HEIGHT:
        screen_height = width_preferred_height
    else:
        screen_height = MAX_HEIGHT
        screen_width = MAX_HEIGHT * board_aspect_ratio
        if isinstance(screen_width, float):
            screen_width = int(screen_width)
            screen_height = screen_width / board_aspect_ratio

    def board_to_screen_x(board_x):
        return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    tile_size = int(board_to_screen_x(boundingbox.bottomright.x) / boundingbox.width())

    board_tile_width = screen_width  / boundingbox.width()
    board_tile_height = screen_height  / boundingbox.height()

    return board_tile_width*tile_size, board_tile_height*tile_size, tile_size    

def animate_frames(board: Board, viewbounds: BoundingBox = None, framerate: int=60):
    """
    `viewbounds` overrides use of `board.rock_bounding_box`
    """

    ### start the simulation
    framegen = solution.run_simulation_frame_generator(board, create_board_frame_fn=lambda board, sand_unit: sand_unit)

    ### calculating screen size
    bb = viewbounds if viewbounds else board.rock_bounding_box
    boundingbox = BoundingBox(
        topleft = bb.topleft - Point(1, 1),
        bottomright = bb.bottomright + Point(2, 2)
    )
    board.viewport = boundingbox

    board_aspect_ratio = boundingbox.width() / boundingbox.height()

    # want to preserve aspect ratio of board -- want tiles to be square.
    # MAX_WIDTH = 1500
    # MAX_HEIGHT = 800
    # if (preferred_width:= boundingbox.width()*50) <= MAX_WIDTH:
    #     screen_width = preferred_width
    # else:
    #     screen_width = MAX_WIDTH
    # width_preferred_height = screen_width / board_aspect_ratio

    # if width_preferred_height <= MAX_HEIGHT:
    #     screen_height = width_preferred_height
    # else:
    #     screen_height = MAX_HEIGHT
    #     screen_width = MAX_HEIGHT * board_aspect_ratio
    #     if isinstance(screen_width, float):
    #         screen_width = int(screen_width)
    #         screen_height = screen_width / board_aspect_ratio

    # def board_to_screen_x(board_x):
    #     return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    # def board_to_screen_y(board_y):
    #     return (board_y - boundingbox.topleft.y)*(screen_height / boundingbox.height())

    # screen_tile_px = board_to_screen_x(boundingbox.bottomright.x) / boundingbox.width()
    screen_width, screen_height, screen_tile_px = calculate_screen_width_height_tilesize(board, boundingbox)
    def board_to_screen_x(board_x):
        return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    def board_to_screen_y(board_y):
        return (board_y - boundingbox.topleft.y)*(screen_height / boundingbox.height())

    print('topleft', boundingbox.topleft)
    print('bottomright', boundingbox.bottomright)
    print('bb width', boundingbox.width())
    print('bb height', boundingbox.height())
    print('screen width', screen_width)
    print('screen height', screen_height)
    print('tile size', screen_tile_px)

    ### pygame setup
    pygame.init()
    screen = pygame.display.set_mode(size=(screen_width, screen_height))
    clock = pygame.time.Clock()
    dt = 0

    running = True
    simulation_running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ### rendering!
        # for now, keeping it simple - clearing screen per frame
        screen.fill('black')

        # sand source
        pygame.draw.rect(
            surface=screen, color='magenta', 
            rect=(board_to_screen_x(board.sand_origin_pt.x), board_to_screen_y(board.sand_origin_pt.y), screen_tile_px, screen_tile_px)
        )

        # rocks
        for rock in board.rocks:
            pygame.draw.rect(
                surface=screen, color='gray', 
                rect=(board_to_screen_x(rock.x), board_to_screen_y(rock.y), screen_tile_px, screen_tile_px)
            )
        if board.cave_floor_y < math.inf:
            for x in range(0, screen_width, int(screen_tile_px)):
                pygame.draw.rect(
                    surface=screen, color='gray', 
                    rect=(x, board_to_screen_y(board.cave_floor_y), screen_tile_px, screen_tile_px)
                )
        # sand
        for sand in board.settled_sand:
            pygame.draw.rect(
                surface=screen, color='gold3',
                rect=(board_to_screen_x(sand.x), board_to_screen_y(sand.y), screen_tile_px, screen_tile_px)
            )

        # # next simulation frame
        if simulation_running:
            try:
                falling_sand_unit = next(framegen)
            except StopIteration:
                simulation_running = False
        if falling_sand_unit:
            fallingsand = falling_sand_unit.current_coords
            pygame.draw.rect(
                surface=screen, color='gold3',
                rect=(board_to_screen_x(fallingsand.x), board_to_screen_y(fallingsand.y), screen_tile_px, screen_tile_px)
            )

        ### display to window
        pygame.display.flip()
        dt = clock.tick(framerate) / 1000        

def animate_part_one_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.create_board(filepath='example.txt', sand_origin=sand_origin)
    animate_frames(board, viewbounds=BoundingBox(board.rock_bounding_box.topleft, board.rock_bounding_box.bottomright + Point(0, 2)))

def animate_part_two_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='example.txt', sand_origin=sand_origin)
    animate_frames(board, viewbounds=BoundingBox(Point(488, 0), Point(512, 11)))

def animate_part_one_input(sand_origin=solution.PUZZLE_SAND_ORIGIN, framerate=60):
    board = solution.create_board(filepath='input.txt', sand_origin=sand_origin)
    animate_frames(board, framerate=framerate)

def animate_part_two_input(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='input.txt', sand_origin=sand_origin)
    animate_frames(board)

if __name__ == '__main__':
    # animate_part_one_example()
    # animate_part_two_example()
    animate_part_one_input(framerate=100)

"""
TODO

1. Make the simulation accept a parameter - number_of_time_steps_between_sand_unit_drops: int or None
This will greatly speed up the simulation of the big input.  I can store a list of currently falling
sand units.

2. Simulate inputs on my landscape 1080p monitor!

3. Save images from simulation and make a gif :)
"""