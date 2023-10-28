import pygame

import solution
from solution import Board, BoundingBox, Point

def animate_frames(board: Board, viewbounds: BoundingBox = None, framerate: int=60):
    """
    
    `viewbounds` overrides use of `board.rock_bounding_box`
    """

    ### calculating screen size
    MAX_WIDTH = 1600
    MAX_HEIGHT = 900

    if viewbounds:
        boundingbox = BoundingBox(
            topleft = viewbounds.topleft - Point(1, 1),
            bottomright = viewbounds.bottomright + Point(2, 2)
        )
    else:
        boundingbox = BoundingBox(
            topleft = board.rock_bounding_box.topleft - Point(1, 1),
            bottomright = board.rock_bounding_box.bottomright + Point(2, 2) 
        )
    # want to preserve aspect ratio of board -- want tiles to be square.
    # TODO implement logic for this.  Example will be fine without.
    screen_width  = min(MAX_WIDTH,  boundingbox.width() *50)
    screen_height = min(MAX_HEIGHT, boundingbox.height()*50)

    board_to_screen_x = lambda board_x: (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    board_to_screen_y = lambda board_y: (board_y - boundingbox.topleft.y)*(screen_height / boundingbox.height())

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
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # rendering!
        # for now, keeping it simple - clearing screen per frame
        screen.fill('black')
        for rock in board.rocks:
            pygame.draw.rect(
                surface=screen, color='gray', 
                rect=(board_to_screen_x(rock.x), board_to_screen_y(rock.y), screen_tile_px, screen_tile_px)
            )
            # print(rock.x, board_to_screen_x(rock.x))
            # print(rock.y, board_to_screen_y(rock.y))
            # print(screen_tile_px)
            # breakpoint()

        pygame.display.flip()
        dt = clock.tick(framerate) / 1000
        

def animate_part_one_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.create_board(filepath='example.txt', sand_origin=sand_origin)
    animate_frames(board) #, viewbounds=BoundingBox(board.rock_bounding_box.topleft, board.rock_bounding_box.bottomright + Point(0, 2)))

def animate_part_two_example(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='example.txt', sand_origin=sand_origin)

def animate_part_one_input(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.create_board(filepath='input.txt', sand_origin=sand_origin)

def animate_part_two_input(sand_origin=solution.PUZZLE_SAND_ORIGIN):
    board = solution.obtain_part_two_board(inputfile='input.txt', sand_origin=sand_origin)

if __name__ == '__main__':
    animate_part_one_example()