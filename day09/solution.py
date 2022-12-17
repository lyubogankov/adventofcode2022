from collections import namedtuple
from pprint import pprint
import hashlib


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

Grid = namedtuple('Grid', ['topl', 'botr'])
PrintItem = namedtuple('PrintItem', ['printchar', 'point'])
# Move = namedtuple('Move', ['transform', 'repetitions', 'name'])
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
def generate_print_grid_string(items, grid):
    '''Creates string to be printed from list of items, note that items are applied FIFO (so they can override each other).
    Wrote separately from print function so I can do unit tests against this function.
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
            # print(f'x={col_idx}, y={row_idx}')
            nextchar = '.'
            while curr_item < len(items) and items[curr_item].point.x == col_idx and items[curr_item].point.y == row_idx:
                # print(f'\t{curr_item}, {items[curr_item]}, {items[curr_item].printchar}')
                nextchar = items[curr_item].printchar
                curr_item += 1
            print_grid_string += nextchar
        if row_idx > grid.botr.y:
            print_grid_string += '\n'
    return print_grid_string

# general printer, for showing changes to grid state
def generate_current_grid_state_string(h_point, t_point, grid, start_point):
    return  generate_print_grid_string(
                items=[PrintItem('s', start_point), PrintItem('T', t_point), PrintItem('H', h_point)],
                grid=grid
            )
def print_current_grid_state(h_point, t_point, grid, start_point):
    print(generate_current_grid_state_string(h_point, t_point, grid, start_point), end='\n\n')

# printer for part one
def generate_unique_t_locations_string(t_locations_set, grid, start_point):
    return  generate_print_grid_string(
                items=[PrintItem('#', point) for point in t_locations_set] + [PrintItem('s', start_point)],
                grid=grid
            )
def print_unique_t_locations(t_locations_set, grid, start_point):
    print(generate_unique_t_locations_string(t_locations_set, grid, start_point), end='\n\n')

### rope simulation
def update_h_and_t_pos(h_initial, t_initial, h_atomic_move):

    ### update H
    h_updated = h_initial + h_atomic_move.transform

    ### update T
    # case one: is T within one square of H?  if so, no need to move it.
    if abs(h_updated.x - t_initial.x) <= 1 and abs(h_updated.y - t_initial.y) <= 1:
        t_updated = t_initial
    # case two: H starts in same x (or y) as T (not both) and moves further away in x (or y) dir
    elif (t_initial.x == h_initial.x == h_updated.x) or (t_initial.y == h_initial.y == h_updated.y):
        t_updated = t_initial + h_atomic_move.transform
    # case three: H starts diagonal to T and moves away.  T has to move diagonally to keep up (aka take H's original spot)
    else:
        t_updated = h_initial

    return h_updated, t_updated

def update_dynamic_grid(h, grid):
    grid.botr.x = max(grid.botr.x, h.x)  # +x
    grid.topl.x = min(grid.topl.x, h.x)  # -x
    grid.topl.y = max(grid.topl.y, h.y)  # +y
    grid.botr.y = min(grid.botr.y, h.y)  # -y
    return grid

def simulate_rope(move_list, fixed_grid=None, start_point=Point_2D(x=0, y=0), _print=False, print_atomic_moves=False):
    '''Start point will be the bottom left corner of the grid.'''

    # initial condition
    h = Point_2D(start_point.x, start_point.y)
    t = Point_2D(start_point.x, start_point.y)
    if fixed_grid:
        # the grid will not grow.
        # I won't check whether moves will send H/T outside of the grid, though,
        #   I'm assuming that the moves account for this  (like example.txt -- that's why I'm doing this.)
        grid = fixed_grid
    else:
        # the grid will grow dynamically from a 1x1 square.
        grid = Grid(
            topl=Point_2D(x=start_point.x, y=start_point.y),
            botr=Point_2D(x=start_point.x, y=start_point.y)
        )

    if _print:
        print('Initial state:')
        print_current_grid_state(h, t, grid, start_point)
    for move in move_list:
        if _print:
            print(f'== {move.name} {move.repetitions} ==')
        for _ in range(move.repetitions):
            h, t = update_h_and_t_pos(h_initial=h, t_initial=t, h_atomic_move=move)
            if not fixed_grid:
                grid = update_dynamic_grid(h, grid)
            if _print and print_atomic_moves:
                print_current_grid_state(h, t, grid, start_point)
        if _print and not print_atomic_moves:
            print_current_grid_state(h, t, grid, start_point)

def simulate_rope_partone(move_list, fixed_grid=None, start_point=Point_2D(x=0, y=0), _print=False, print_atomic_moves=False):
    '''Start point will be the bottom left corner of the grid.'''

    # initial condition
    h = Point_2D(start_point.x, start_point.y)
    t = Point_2D(start_point.x, start_point.y)
    if fixed_grid:
        # the grid will not grow.
        # I won't check whether moves will send H/T outside of the grid, though,
        #   I'm assuming that the moves account for this  (like example.txt -- that's why I'm doing this.)
        grid = fixed_grid
    else:
        # the grid will grow dynamically from a 1x1 square.
        grid = Grid(
            topl=Point_2D(x=start_point.x, y=start_point.y),
            botr=Point_2D(x=start_point.x, y=start_point.y)
        )

    # special part one bit
    t_move_set = {start_point}

    if _print:
        print('Initial state:')
        print_current_grid_state(h, t, grid, start_point)
    for move in move_list:
        if _print:
            print(f'== {move.name} {move.repetitions} ==')
        for _ in range(move.repetitions):
            h, t = update_h_and_t_pos(h_initial=h, t_initial=t, h_atomic_move=move)
            if not fixed_grid:
                grid = update_dynamic_grid(h, grid)
            t_move_set.add(t)
            if _print and print_atomic_moves:
                print_current_grid_state(h, t, grid, start_point)
        if _print and not print_atomic_moves:
            print_current_grid_state(h, t, grid, start_point)

    return t_move_set, generate_unique_t_locations_string(t_move_set, grid, start_point)

if __name__ == '__main__':

    fixed_grid = Grid(
        topl=Point_2D(x=0, y=4),
        botr=Point_2D(x=5, y=0)
    )

    for inputfile in ['example.txt']: #, 'input.txt']:
        move_list = read_input_file_into_move_list(inputfile)
        #simulate_rope(move_list, fixed_grid=fixed_grid, _print=True, print_atomic_moves=True)
        #simulate_rope(move_list, fixed_grid=None, _print=True, print_atomic_moves=True)
        t_move_set, t_move_str = simulate_rope_partone(move_list, fixed_grid=fixed_grid, _print=True, print_atomic_moves=True)
        print(f'Number of unique spots T has visited: {len(t_move_set)}')
        print(t_move_str, end='\n\n')
        

'''
TODO
4. create unit tests for generate_print_str based on example.txt
'''