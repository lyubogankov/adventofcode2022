from collections import namedtuple
from pprint import pprint
import os
import time

# colors
RED = '\033[31m'
RESET = '\033[0m'

# reading text file -> set of moves

'''
General rules for coords:

x = left/right = cols  (+x = right)
y = up  / down = rows  (+y = up   )
'''
class Point_2D:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point_2D(x={' ' if self.x >= 0 else ''}{self.x}, y={' ' if self.y >= 0 else ''}{self.y})"

    def __str__(self):
        return f"({' ' if self.x >= 0 else ''}{self.x}, {' ' if self.y >= 0 else ''}{self.y})"

    def __add__(self, point2):
        point1 = self
        x = point1.x + point2.x
        y = point1.y + point2.y
        return Point_2D(x, y)

    def __sub__(self, point2):
        point1 = self
        x = point1.x - point2.x
        y = point1.y - point2.y
        return Point_2D(x, y)

    def __iadd__(self, point2):
        point1 = self
        point1.x += point2.x
        point1.y += point2.y
        return point1

    # heavily inspired by https://stackoverflow.com/q/390250
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    # https://stackoverflow.com/a/1608882 -- if I implement __eq__, I also need to implement __hash__
    # https://stackoverflow.com/a/2909119 -- solution for implementing hash.  Rely on hash of tuple!
    def __hash__(self):
        key = (self.x, self.y)
        return hash(key)

# Move = namedtuple('Move', ['transform', 'repetitions', 'name'])
class Move:
    '''Making this a class instead of a namedtuple so I can do equality check during testing!'''

    def __init__(self, transform, repetitions, name):
        self.transform = transform
        self.repetitions = repetitions
        self.name = name

    def __repr__(self):
        return f"Move(transform={repr(self.transform)}, repetitions={self.repetitions}, name='{self.name}')"

    def __str__(self):
        return f"{self.name} {self.repetitions}"

    @staticmethod
    def turn_repeated_move_into_atomic_move_list(move):
        if move.repetitions == 1:
            return [move]
        return [Move(move.transform, 1, move.name) for _ in range(move.repetitions)]

# Grid = namedtuple('Grid', ['topl', 'botr'])
class Grid:
    '''Made this into a class so I can make the create_grid_with_dimensions() method'''
    def __init__(self, topl, botr):
        self.topl = topl
        self.botr = botr
    @staticmethod
    def create_grid_with_dimensions(width, height, botl=Point_2D(x=0, y=0)):
        return Grid(
            topl=Point_2D(x=botl.x,             y=botl.y + (height-1)),
            botr=Point_2D(x=botl.x + (width-1), y=botl.y             )
        )

PrintItem = namedtuple('PrintItem', ['printchar', 'point'])
moves = {
    'U' : Point_2D(x= 0, y= 1),
    'D' : Point_2D(x= 0, y=-1),
    'R' : Point_2D(x= 1, y= 0),
    'L' : Point_2D(x=-1, y= 0)
}

def read_input_file_into_move_list(inputfile):
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()
    move_list = []
    lines = contents.split('\n')[:-1]  # Since splitting by \n, last entry will be blank. Skip.
    for line in lines:
        direction, num_steps = line.split(' ')
        move_list.append(Move(transform=moves[direction], repetitions=int(num_steps), name=direction))
    return move_list

### printing

# generic printer
def generate_print_grid_string(items, grid, animation_framedelay=None):
    '''Creates string to be printed from list of items, note that items are applied FIFO (so they can override each other).
    Wrote separately from print function so I can do unit tests against this function.

    animation_framedelay = don't print as many dots, only do it for the border.
    '''

    # sort the items by x (row), then y (col) -- reverse order of loops below (y (row) = outer, x (col) = inner)
    #   This gives us items ordered by row, then within each row by col, the same order in which the loops iterate.
    #   That allows the character replacement to work!
    items.sort(key=lambda item: item.point.x)
    items.sort(key=lambda item: item.point.y, reverse=True)  
    curr_item = 0

    # generate each row at a time.  if our current coord matches an item, print its string, and get new item from list, otherwise point = .
    print_grid_string = ''     
    for row_idx in reversed(range(grid.botr.y, grid.topl.y+1)):  # need to reverse bc row 0 is on bottom, n on top...
        for col_idx in range(grid.topl.x, grid.botr.x+1):
            nextchar = '.'
            if animation_framedelay and grid.topl.x < col_idx < grid.botr.x and grid.botr.y < row_idx < grid.topl.y:
                nextchar = ' '
            while curr_item < len(items) and items[curr_item].point.x == col_idx and items[curr_item].point.y == row_idx:
                nextchar = items[curr_item].printchar
                curr_item += 1
            print_grid_string += nextchar
        if row_idx > grid.botr.y:
            print_grid_string += '\n'
    return print_grid_string

# part one printer, for showing changes to grid state
def generate_current_grid_state_string(knots, grid, start_point, animation_framedelay=None, color_indices=[]):
    startpt_printchar = f'{RED}s{RESET}' if animation_framedelay else 's'
    items = [PrintItem(startpt_printchar, start_point)]
    if len(knots) == 2:
        h_point, t_point = knots
        items += [PrintItem('T', t_point), PrintItem('H', h_point)]
    else:
        # add items to the list from least -> greatest (largest #d knot is last, up to 1, then H (0))
        for _i, point in enumerate(reversed(knots)):
            i = len(knots)-(_i+1)
            printstr = RED if i in color_indices else ''
            printstr += str(i) if i > 0 else 'H'
            printstr += RESET if i in color_indices else ''
            items.append(PrintItem(printstr, point))
    return  generate_print_grid_string(items=items, grid=grid, animation_framedelay=animation_framedelay )
def print_current_grid_state(*args, **kwargs):
    print(generate_current_grid_state_string(*args, **kwargs), end='\n\n')

# printer for unique t locations questions (parts 1/2)
def generate_unique_t_locations_string(t_locations_set, grid, start_point, color_s=False):
    startpt_printchar = f'{RED}s{RESET}' if color_s else 's'
    return  generate_print_grid_string(
                items=[PrintItem('#', point) for point in t_locations_set] + [PrintItem(startpt_printchar, start_point)],
                grid=grid
            )
def print_unique_t_locations(*args, **kwargs):
    print(generate_unique_t_locations_string(*args, **kwargs), end='\n\n')

### rope simulation
def update_adjacent_following_knot_pos(lead_old, follow_old, lead_atomic_move):
    transform = lead_atomic_move.transform

    ### update leader
    lead_new = lead_old + lead_atomic_move.transform

    ### update follower
    # case one: is L within one square of F?  if so, no need to move it.
    if abs(lead_new.x - follow_old.x) <= 1 and abs(lead_new.y - follow_old.y) <= 1:
        follow_new = follow_old
    # case two (special multiknot case):  Lead makes diagonal move.
    #   Had to introduce this during part two, my sim wasn't matching the example output!
    elif abs(transform.x) > 0 and abs(transform.y) > 0:
        # 2a: Ran into this with example_two.
        #     Can't blindly apply diagonal move, goal is to get knots to be in same row or col?
        if lead_new.x == follow_old.x:
            follow_new = follow_old + Point_2D(x=0, y=transform.y)
        elif lead_new.y == follow_old.y:
            follow_new = follow_old + Point_2D(x=transform.x, y=0)
        # 2b: What I had previously - apply same diagonal move
        else:
            follow_new = follow_old + transform
    # case three: L starts in same x (or y) as F (not both) and moves further away in x (or y) dir
    elif (follow_old.x == lead_old.x == lead_new.x) or (follow_old.y == lead_old.y == lead_new.y):
        follow_new = follow_old + transform
    # case four: L starts diagonal to F and moves away.  F has to move diagonally to keep up (aka take L's original spot)
    # NOTE -- originally had "follow_new = lead_old", but that only works for knots 0/1.
    else:
        # lead knot = 1 or higher
        if transform.x > 0 and transform.y > 0:
            follow_new = follow_old + transform
        # lead knot = 0  (can only move rows/cols, not diagonally')
        else:
            follow_new = lead_old

    # calculate the move made by the follower - needed for 2+ knots case
    follow_atomic_transform = follow_new - follow_old
    follow_atomic_move = Move(transform=follow_atomic_transform, repetitions=1, name='')

    return follow_new, follow_atomic_move

def update_lead_knot_pos(old_pos, atomic_move):
    return old_pos + atomic_move.transform

def update_all_knot_pos(knots, lead_move, grid, start_point, rep=0, print_atomic_moves=False, animation_framedelay=None):
    if print_atomic_moves:
        print('-'*(grid.botr.x + 3), f'rep {rep+1} / {lead_move.repetitions}')

    # update position of all knots (0 happens outside of the loop)
    _move = lead_move
    updated_knots = [update_lead_knot_pos(knots[0], _move)]
    if print_atomic_moves:
        print(_move.transform)
        print_knots = updated_knots + knots[1:]                
        print_current_grid_state(knots=print_knots, grid=grid, start_point=start_point, color_indices=[0])
    # the 'tails' happen within the loop
    _break = False
    for i, (lead_old, follow_old) in enumerate(zip(knots, knots[1:])):                
        follow_new, follow_move = update_adjacent_following_knot_pos(lead_old, follow_old, lead_atomic_move=_move)
        _move = follow_move  # the follow_move of nth adjacent pair is the lead_move of (n+1)th pair
        updated_knots.append(follow_new)

        # if the later knots aren't moving, we're done!
        if updated_knots[-1] == knots[len(updated_knots)-1]:
            updated_knots += knots[len(updated_knots):]  # make sure the remaining knots get transferred
            _break = True
            if i > len(updated_knots):
                break
        # print change to board
        if print_atomic_moves:
            print(_move.transform)
            print_knots = updated_knots + knots[len(updated_knots):]
            print_current_grid_state(knots=print_knots, grid=grid, start_point=start_point, color_indices=[i+1])
            if animation_framedelay and not _break:
                os.system('clear') # linux only :/
            print_current_grid_state(knots=print_knots, grid=grid, start_point=start_point, color_indices=[i+1], animation_framedelay=animation_framedelay)
            if animation_framedelay and not _break:
                time.sleep(animation_framedelay)
        
        # want to print the first move that doesn't move, then break.
        if _break:
            break
    return updated_knots

def simulate_rope(
        move_list, fixed_grid=None, start_point=Point_2D(x=0, y=0), num_knots=10,
        print_after_move=False, print_after_full_rope_update=False, print_atomic_moves=False,
        color_start_point=False, animation_framedelay=None):
    '''Start point will be the bottom left corner of the grid.'''

    _print = print_after_move or print_after_full_rope_update or print_atomic_moves

    # initial condition
    if fixed_grid:
        # the grid will not grow.
        # I won't check whether moves will send H/T outside of the grid, though,
        #   I'm assuming that the moves account for this  (like example.txt -- that's why I'm doing this.)
        grid = fixed_grid
    else:
        # the grid will grow dynamically from a 1x1 square.
        grid = Grid.create_grid_with_dimensions(width=1, height=1)
    knots = [Point_2D(x=start_point.x, y=start_point.y) for _ in range(num_knots)]  # the numbering is done in the print function.

    t_move_set = {start_point}

    if _print:
        print('Initial state:')
        print_current_grid_state(knots, grid, start_point, animation_framedelay)
    for move in move_list:
        if _print:
            print(f"{'='*(grid.botr.x + 15) if print_atomic_moves else ''}== {move.name} {move.repetitions} ==\n")
        for rep in range(move.repetitions):           
            knots = update_all_knot_pos(knots, move, grid, start_point, rep, print_atomic_moves, animation_framedelay)
            # head = first knot, tail = last knot
            if not fixed_grid:
                grid = update_dynamic_grid(knots[0], grid)
            t_move_set.add(knots[-1])

            if print_after_full_rope_update:
                if animation_framedelay:
                        os.system('clear') # linux only :/
                print_current_grid_state(knots, grid, start_point, animation_framedelay)
                if animation_framedelay:
                        time.sleep(animation_framedelay)
        if print_after_move:
            print_current_grid_state(knots=knots, grid=grid, start_point=start_point)

    return t_move_set, generate_unique_t_locations_string(t_move_set, grid, start_point, color_start_point)

def update_dynamic_grid(h, grid):
    grid.botr.x = max(grid.botr.x, h.x)  # +x
    grid.topl.x = min(grid.topl.x, h.x)  # -x
    grid.topl.y = max(grid.topl.y, h.y)  # +y
    grid.botr.y = min(grid.botr.y, h.y)  # -y
    return grid


if __name__ == '__main__':

    fixed_grid_example    = Grid.create_grid_with_dimensions(width=  6, height=  5)
    fixed_grid_exampletwo = Grid.create_grid_with_dimensions(width= 26, height= 21)
    fixed_grid_input      = Grid.create_grid_with_dimensions(width=364, height=268)

    # for inputfile, num_knots in [
    #         ('example.txt',  2),                          ('input.txt',  2),   # part one
    #         ('example.txt', 10), ('example_two.txt', 10), ('input.txt', 10)]:  # part two

    #     if num_knots == 2:
    #         print('-'*90, 'PART ONE')
    #     elif num_knots == 10:
    #         print('-'*90, 'PART TWO')

    #     exampleone = inputfile == 'example.txt'
    #     exampletwo = inputfile == 'example_two.txt'
    #     example = exampleone or exampletwo
        
    #     if exampleone:
    #         fixed_grid = fixed_grid_example
    #         start_point = Point_2D(x=0, y=0)
    #     elif exampletwo:
    #         fixed_grid = fixed_grid_exampletwo
    #         start_point = Point_2D(x=11, y=5)
    #     else:
    #         fixed_grid = None

    #     move_list = read_input_file_into_move_list(inputfile)

    #     t_move_set, t_move_str = simulate_rope(
    #         move_list,
    #         fixed_grid=fixed_grid,
    #         start_point=start_point,
    #         num_knots=num_knots,
    #         print_after_move=exampletwo,
    #         print_after_full_rope_update=exampleone,
    #         print_atomic_moves=False,
    #         color_start_point=True
    #     )

    #     print(f'Number of unique spots T has visited: {len(t_move_set)}')
    #     print(t_move_str, end='\n\n')


    # # animation
    # '''TODO
    # create GIF out of individual frames for example / input.txt

    # especially input, bc it's too large to render properly in terminal.
    # https://stackoverflow.com/questions/753190/programmatically-generate-video-or-animated-gif-in-python
    # '''
    # for inputfile in ['example.txt']: #, 'input.txt']:  # input is too large for the terminal animation.  perhaps create GIF?
    #     example = inputfile == 'example.txt'

    #     move_list = read_input_file_into_move_list(inputfile)
    #     t_move_set, t_move_str = simulate_rope(
    #         move_list,
    #         fixed_grid=fixed_grid_example if example else fixed_grid_input,
    #         start_point=Point_2D(0, 0) if example else Point_2D(299, 220),
    #         _print=True,
    #         print_atomic_moves=True,
    #         color_start_point=True,
    #         animation_framedelay=True
    #     )

    #     # print('.'*364)
    #     # _ = input('change your resolution.  ENTER when done.')

    # part two animation
    for inputfile in ['example.txt', 'example_two.txt']:
        exampleone = inputfile == 'example.txt'
        exampletwo = inputfile == 'example_two.txt'
        example = exampleone or exampletwo

        move_list = read_input_file_into_move_list(inputfile)

        if exampleone:
            fixed_grid = fixed_grid_example
            start_pt = Point_2D(x=0, y=0)
        elif exampletwo:
            fixed_grid = fixed_grid_exampletwo
            start_pt = Point_2D(x=11, y=5)

        _, _ = simulate_rope(
            move_list,
            fixed_grid=fixed_grid,
            start_point=start_pt,
            num_knots=10,
            print_atomic_moves=True,
            animation_framedelay=0.1
        )



'''
Big takeaway from Day09:

I read over the specification text and implemented my rope-knot-movement simulation rules.
However, seeing the worked examples vs the output of my sim contradicted my understanding of the spec several times!

The worked examples (especially watching adjacent knots move one-by-one) helped my enhance my
    understanding of the spec and arrive at the correct answer.
'''