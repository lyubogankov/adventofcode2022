import copy
import functools
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

    def board_to_screen_x(board_x):
        return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    tile_size = int(board_to_screen_x(boundingbox.bottomright.x) / boundingbox.width())

    return boundingbox.width()*tile_size, boundingbox.height()*tile_size, tile_size    

def animate_frames(board: Board, viewbounds: BoundingBox = None, framerate: int=60, time_steps_between_sand_unit_drops=None, save_folder=None):
    """
    `viewbounds` overrides use of `board.rock_bounding_box`
    """

    # run the simulation to see if the sand spills over the rock bounding box (like for input, pt 2)
    print('Performing preliminary simulation before visualization to confirm view bounds...')
    boardbb = solution.obtain_board_bb(board)

    ### start the simulation
    framegen = solution.run_simulation_frame_generator(
        board,
        create_board_frame_fn=lambda board, sand_units: sand_units,
        time_steps_between_sand_unit_drops = time_steps_between_sand_unit_drops
    )

    ### calculating screen size
    bb = viewbounds if viewbounds else boardbb
    boundingbox = BoundingBox(
        topleft = bb.topleft - Point(1, 1),
        bottomright = bb.bottomright + Point(x=2, y=2 + ((board.cave_floor_y - board.rock_bounding_box.bottomright.y) if board.cave_floor_y < math.inf else 0))
    )
    board.viewport = boundingbox

    screen_width, screen_height, screen_tile_px = calculate_screen_width_height_tilesize(board, boundingbox)
    def board_to_screen_x(board_x):
        return (board_x - boundingbox.topleft.x)*(screen_width  / boundingbox.width())
    def board_to_screen_y(board_y):
        return (board_y - boundingbox.topleft.y)*(screen_height / boundingbox.height())
    def draw_square(color, board_toplx, board_toply):
        pygame.draw.rect(
            surface=screen, color=color, 
            rect=(board_to_screen_x(board_toplx), board_to_screen_y(board_toply), screen_tile_px, screen_tile_px)
        )
    draw_rock = functools.partial(draw_square, 'gray35')
    draw_sand = functools.partial(draw_square, 'gold3')

    ### pygame setup
    pygame.init()
    screen = pygame.display.set_mode(size=(screen_width, screen_height))
    clock = pygame.time.Clock()
    dt = 0

    running = True
    simulation_running = True
    if save_folder:
        framecounter = 0

    while running:
        # checking for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # framerate up/down, but only if it's running for the user to see (as opposed to saving images to hard drive)
        if not save_folder:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                framerate += 1
            if keys[pygame.K_s]:
                framerate -= 1

        ### rendering!
        # for now, keeping it simple - clearing screen per frame
        screen.fill('black')

        # sand source
        draw_square(color='magenta', board_toplx=board.sand_origin_pt.x, board_toply=board.sand_origin_pt.y)

        # rocks
        for rock in board.rocks:
            draw_rock(rock.x, rock.y)
        if board.cave_floor_y < math.inf:
            # for x in range(0, screen_width, int(screen_tile_px)):
            for x in range(boundingbox.topleft.x, boundingbox.bottomright.x):
                draw_rock(x, board.cave_floor_y)
        # sand
        for sand in board.settled_sand:
            draw_sand(sand.x, sand.y)

        # # next simulation frame
        if simulation_running:
            try:
                falling_sand_units = next(framegen)
            except StopIteration:
                simulation_running = False
        any_sand_indefinitely_falling = any(s.falling_indefinitely for s in falling_sand_units)
        for falling_sand_unit in falling_sand_units:
            fallingsand = falling_sand_unit.current_coords
            if not any_sand_indefinitely_falling:
                draw_sand(fallingsand.x, fallingsand.y)
            else:
                draw_square('red', fallingsand.x, fallingsand.y)

        # save image to folder, if specified
        if save_folder and simulation_running:
            pygame.image.save(screen, f'{save_folder}/screenshot{framecounter:05}.png')
            framecounter += 1

        ### display to window
        pygame.display.flip()
        dt = clock.tick(framerate) / 1000        

def animate_part_one_example(sand_origin=solution.PUZZLE_SAND_ORIGIN, framerate=15, time_steps_between_sand_unit_drops=None, save_folder=None):
    board = solution.create_board(filepath='example.txt', sand_origin=sand_origin)
    animate_frames(
        board,
        viewbounds=BoundingBox(board.rock_bounding_box.topleft, board.rock_bounding_box.bottomright + Point(0, 2)),
        framerate=framerate,
        time_steps_between_sand_unit_drops=time_steps_between_sand_unit_drops,
        save_folder=save_folder
    )

def animate_part_two_example(sand_origin=solution.PUZZLE_SAND_ORIGIN, framerate=15, time_steps_between_sand_unit_drops=None, save_folder=None):
    board = solution.obtain_part_two_board(inputfile='example.txt', sand_origin=sand_origin)
    animate_frames(
        board,
        viewbounds=BoundingBox(Point(488, 0), Point(512, 11)),
        framerate=framerate,
        time_steps_between_sand_unit_drops=time_steps_between_sand_unit_drops,
        save_folder=save_folder
    )

def animate_part_one_input(sand_origin=solution.PUZZLE_SAND_ORIGIN, framerate=60, time_steps_between_sand_unit_drops=None, save_folder=None):
    board = solution.create_board(filepath='input.txt', sand_origin=sand_origin)
    animate_frames(
        board,
        framerate=framerate,
        time_steps_between_sand_unit_drops=time_steps_between_sand_unit_drops,
        save_folder=save_folder
    )

def animate_part_two_input(sand_origin=solution.PUZZLE_SAND_ORIGIN, framerate=60, time_steps_between_sand_unit_drops=None, save_folder=None):
    board = solution.obtain_part_two_board(inputfile='input.txt', sand_origin=sand_origin)
    animate_frames(
        board,
        framerate=framerate,
        time_steps_between_sand_unit_drops=time_steps_between_sand_unit_drops,
        save_folder=save_folder
    )

if __name__ == '__main__':
    ## simulation, for viewing
    # animate_part_one_example(time_steps_between_sand_unit_drops=None)
    # animate_part_two_example(time_steps_between_sand_unit_drops=2)
    animate_part_one_input(framerate=60, time_steps_between_sand_unit_drops=2)
    # animate_part_two_input(framerate=60, time_steps_between_sand_unit_drops=2)

    ## simulation, for saving screenshots to hard drive for GIF-making
    # animate_part_one_example(time_steps_between_sand_unit_drops=None, save_folder='/home/lyubo/script/advent_of_code/2022/media/day14/example_gui_p1')
    # animate_part_one_example(time_steps_between_sand_unit_drops=2, save_folder='/home/lyubo/script/advent_of_code/2022/media/day14/example_gui_p1_multigrain')
    # animate_part_two_example(time_steps_between_sand_unit_drops=2, save_folder='/home/lyubo/script/advent_of_code/2022/media/day14/example_gui_p2_multigrain')
    # animate_part_one_input(time_steps_between_sand_unit_drops=2, save_folder='/home/lyubo/script/advent_of_code/2022/media/day14/input_gui_p1_multigrain')
    # animate_part_two_input(time_steps_between_sand_unit_drops=2, save_folder='/home/lyubo/script/advent_of_code/2022/media/day14/input_gui_p2_multigrain')

"""
DONE
1. Make the simulation accept a parameter - number_of_time_steps_between_sand_unit_drops: int or None
This will greatly speed up the simulation of the big input.  I can store a list of currently falling
sand units.

TODO
2. Simulate inputs on my landscape 1080p monitor!
3. Save images from simulation and make a gif :)
"""