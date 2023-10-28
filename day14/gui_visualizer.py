import math

import pygame

import solution
from solution import Board, BoundingBox, Point

def animate_frames(board: Board, viewbounds: BoundingBox = None, framerate: int=60):
    """
    `viewbounds` overrides use of `board.rock_bounding_box`
    """

    ### start the simulation
    framegen = solution.run_simulation_frame_generator(board, create_board_frame_fn=lambda board, sand_unit: sand_unit)

    ### calculating screen size
    MAX_WIDTH = 1600
    MAX_HEIGHT = 900

    bb = viewbounds if viewbounds else board.rock_bounding_box
    boundingbox = BoundingBox(
        topleft = bb.topleft - Point(1, 1),
        bottomright = bb.bottomright + Point(2, 2)
    )
    board.viewport = boundingbox
    # want to preserve aspect ratio of board -- want tiles to be square.
    # TODO implement logic for this.  Example will be fine without.
    screen_width  = min(MAX_WIDTH,  boundingbox.width() *50)
    screen_height = min(MAX_HEIGHT, boundingbox.height()*50)

    def board_to_screen_x(board_x):
        return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    def board_to_screen_y(board_y):
        return (board_y - boundingbox.topleft.y)*(screen_height / boundingbox.height())

    screen_tile_px = board_to_screen_x(boundingbox.bottomright.x) / boundingbox.width()

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

        pygame.display.flip()
        dt = clock.tick(framerate) / 1000        

def animate_part_one_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.create_board(filepath='example.txt', sand_origin=sand_origin)
    animate_frames(board, viewbounds=BoundingBox(board.rock_bounding_box.topleft, board.rock_bounding_box.bottomright + Point(0, 2)))

def animate_part_two_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='example.txt', sand_origin=sand_origin)
    animate_frames(board, viewbounds=BoundingBox(Point(488, 0), Point(512, 11)))

def animate_part_one_input(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.create_board(filepath='input.txt', sand_origin=sand_origin)

def animate_part_two_input(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='input.txt', sand_origin=sand_origin)

if __name__ == '__main__':
    animate_part_two_example()