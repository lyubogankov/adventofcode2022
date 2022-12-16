from collections import namedtuple
from pprint import pprint


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

    def __iadd__(self, point2):
        point1 = self
        point1.x += point2.x
        point1.y += point2.y
        return point1

Grid = namedtuple('Grid', ['topl_point', 'botr_point'])
PrintItem = namedtuple('PrintItem', ['printchar', 'point'])
Move = namedtuple('Move', ['transform', 'repetitions', 'name'])
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

### simulation

# generic printer
def generate_print_grid_string(items, grid):
    '''Creates string to be printed from list of items, note that items are applied FIFO (so they can override each other).
    Wrote separately from print function so I can do unit tests against this function.
    '''
    # sort the items by x (row), then y (col)
    # items.sort(key=lambda item: (item.point.x, item.point.y))
    items.sort(key=lambda item: item.point.x)
    items.sort(key=lambda item: item.point.y, reverse=True)
    
    # print('--- Sorted items:')
    # pprint(items)
    
    curr_item = 0

    # generate each row at a time.  if our current coord matches an item, print its string, and get new item from list, otherwise point = .
    print_grid_string = ''     
    
    for row_idx in reversed(range(grid.botr_point.y, grid.topl_point.y+1)):  # need to reverse bc row 0 is on bottom, n on top...
        for col_idx in range(grid.topl_point.x, grid.botr_point.x+1):
            # print(f'x={col_idx}, y={row_idx}')
            nextchar = '.'
            while curr_item < len(items) and items[curr_item].point.x == col_idx and items[curr_item].point.y == row_idx:
                # print(f'\t{curr_item}, {items[curr_item]}, {items[curr_item].printchar}')
                nextchar = items[curr_item].printchar
                curr_item += 1
            print_grid_string += nextchar
        print_grid_string += '\n'

    return print_grid_string

# convinience function
def print_grid(*args, **kwargs): print(generate_print_grid_string(*args, **kwargs))

# general printer, for showing changes to grid state
def print_current_grid_state(h_point, t_point, grid):
    print_grid(items=[PrintItem('T', t_point), PrintItem('H', h_point)], grid=grid)

# printer for part one
def print_unique_T_locations(t_locations_set, grid):
    print_grid(items=[PrintItem('#', point) for point in t_locations_set], grid=grid)

def simulate_rope(move_list, fixed_grid=None, start_point=Point_2D(x=0, y=0), _print=False):
    '''Start point will be the bottom left corner of the grid.'''

    # initial condition
    h = Point_2D(start_point.x, start_point.y)
    t = Point_2D(start_point.x, start_point.y)
    if fixed_grid:
        # the grid will not grow.
        # I won't check whether moves will send H/T outside of the grid, though,
        #   I'm assuming that the moves account for this
        #   (like example.txt -- that's why I'm doing this.)
        grid = fixed_grid
    else:
        # the grid will grow dynamically from a 1x1 square.
        grid = Grid(
            topl_point=Point_2D(x=start_point.x, y=start_point.y),
            botr_point=Point_2D(x=start_point.x, y=start_point.y)
        )

    if _print:
        print('Initial state:')
        print_current_grid_state(h, t, grid)
    for move in move_list:
        print(f'== {move.name} {move.repetitions} ==')
        for _ in range(move.repetitions):
            # update h
            old_h = Point_2D(x=h.x, y=h.y)
            h += move.transform
            # update t

            if _print:
                print('current h:', str(h))
                print_current_grid_state(h, t, grid)
        # if _print:
        #     print(f'After {move.name} {move.repetitions}')
        #     print('current h:', str(h))
        #     print_current_grid_state(h, t, grid)

if __name__ == '__main__':

    fixed_grid = Grid(
        topl_point=Point_2D(x=0, y=4),
        botr_point=Point_2D(x=5, y=0)
    )

    for inputfile in ['example.txt']: #, 'input.txt']:
        move_list = read_input_file_into_move_list(inputfile)
        simulate_rope(move_list, fixed_grid=fixed_grid, _print=True)