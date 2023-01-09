# std library imports
import os
import time
from pprint import pprint
# local imports
import solution

def outward_square_spiral_counterclockwise_from_center(grid, start_pt):

    # calculate the square dimensions for spiralling
    spiral_radius = min(
        # considering x
        start_pt.x - grid.topl.x,
        grid.botr.x - start_pt.x,
        # considering y
        start_pt.y - grid.botr.y,
        grid.topl.y - start_pt.y
    )
    spiral_size = spiral_radius*2 + 1

    h_pos = solution.Point_2D(x=start_pt.x, y=start_pt.y)
    move_list = []

    # +x, +y, -x, -y
    for radius in range(1, spiral_size+1):
        odd = radius % 2 == 1
        for axis, direction_str in [('x', 'R' if odd else 'L'), ('y', 'U' if odd else 'D')]:
            # ensure that we end in the bottom right corner to cover all positions in spiral without repeats
            if radius == spiral_size and axis == 'y':
                break
            h_pos = append_new_move_to_list_and_update_h_pos(move_list, h_pos, direction_str, repetitions=min(radius, spiral_size-1))

    return move_list, h_pos

def inward_square_spiral_counterclockwise_from_corner(grid, start_pt, return_all_knots_to_center=False, num_knots=None):

    # calculate the spiral square dimensions - making sure we have a square
    start_right_side = (start_pt.x - grid.topl.x) > (grid.botr.x - start_pt.x)
    start_top_side   = (start_pt.y - grid.botr.y) > (grid.topl.y - start_pt.y)
    
    width_option_one = (start_pt.x - grid.topl.x) if start_right_side else (grid.botr.x - start_pt.x)
    width_option_two = (start_pt.y - grid.botr.y) if start_top_side   else (grid.topl.y - start_pt.y)
    spiral_width = min(width_option_one, width_option_two) + 1

    # decide when to skip first x -- if we're at bottom right or top left
    skip_first_x_iteration = start_right_side != start_top_side

    # generate move list for spiral
    move_list = []
    h_pos = solution.Point_2D(x=start_pt.x, y=start_pt.y)

    for radius in reversed(range(1, spiral_width+1)):
        odd  = radius % 2 == 1

        for axis, direction_str in [('x', 'R' if odd else 'L'), ('y', 'U' if odd else 'D')]:
            if skip_first_x_iteration and axis == 'x':
                skip_first_x_iteration = False
                continue
            h_pos = append_new_move_to_list_and_update_h_pos(move_list, h_pos, direction_str, repetitions=min(radius, spiral_width-1))

    if not return_all_knots_to_center:
        return move_list, h_pos

    # generate move list for return to return knots to center
    # - ropes with even knot count have largest-idx knot adjacent to start point, so it needs to move.
    # - ropes with odd  knot count have largest-idx knot          on start point, so don't move it!
    last_moved_knot_idx = 0
    for knot in reversed(range(num_knots if num_knots % 2 == 0 else num_knots - 1)):
        h_pos = append_new_move_to_list_and_update_h_pos(
            move_list, h_pos,
            direction_str = 'R' if knot % 2 == 1 else 'L',
            repetitions = knot + last_moved_knot_idx
        )
        last_moved_knot_idx = knot
    
    return move_list, h_pos

def append_new_move_to_list_and_update_h_pos(move_list, old_h_pos, direction_str, repetitions):
    move = solution.Move(
        transform=solution.moves[direction_str],
        repetitions=repetitions,
        name=direction_str
    )
    move_list.append(move)
    return old_h_pos + move.transform*move.repetitions    

if __name__ == '__main__':

    square_grid_side_len = 11
    num_knots = center_point = square_grid_side_len // 2

    fixed_grid = solution.Grid.create_grid_with_dimensions(width=square_grid_side_len, height=square_grid_side_len)
    start_pt = solution.Point_2D(x=center_point, y=center_point)  # grid botl is (0, 0)!
    move_list_one, new_h_pos = outward_square_spiral_counterclockwise_from_center(fixed_grid, start_pt)
    move_list_two, new_h_pos = inward_square_spiral_counterclockwise_from_corner(fixed_grid, new_h_pos, return_all_knots_to_center=True, num_knots=num_knots)

    # for capturing GIF frames
    screenshotparams = solution.ScreenshotParams(
        topoffset=56,
        leftoffset=0,
        width=275,
        height=524,
        framefolder='frames_bonus'
    )

    _, t_move_str = solution.simulate_rope(
        move_list_one + move_list_two,
        num_knots=num_knots,
        fixed_grid=fixed_grid,
        start_point=start_pt,
        print_after_full_rope_update=True,
        print_tail_pos=True,
        animation_framedelay=0.2,
        screenshotparams=screenshotparams,
        print_all_final_knot_pos=False
    )

    # if solution.ANIMATION_GIF_MODE:
    #     time.sleep(1)
    #     os.system('clear') # linux only :/
    #     print(t_move_str)
    # print(t_move_str)
    # if solution.ANIMATION_GIF_MODE:
    #     time.sleep(1)
    #     solution.screenshot(
    #         screenshotparams=None,
    #         sim_iteration='tail_visited'
    #     )