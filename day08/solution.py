'''
Core data structure -- "tree grid", aka 2-dimensional list of lists
    Outside list indices = columns.  At each index is a list.
    Inner list indices = rows.  At each index is a Tree object.

    tree_grid = [
        [Tree(r0 c0), Tree(r0 c1), Tree(r0 c2), ... Tree(r0 cN)],
        [Tree(r1 c0), Tree(r1 c1), Tree(r1 c2), ... Tree(r1 cN)],
        [Tree(r2 c0), Tree(r2 c1), Tree(r2 c2), ... Tree(r1 cN)],
        ...
        [Tree(rM c0), Tree(rM c1), Tree(rM c2), ... Tree(rM cN)]
    ]
'''
import copy

# color codes for printing in terminal (https://stackoverflow.com/a/54955094)
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'

class Tree:
    def __init__(
            self,
            height,
            visible_from_top=False,
            visible_from_bot=False,
            visible_from_left=False,
            visible_from_right=False):
        self.height             = height
        self.visible_from_top   = visible_from_top
        self.visible_from_bot   = visible_from_bot
        self.visible_from_left  = visible_from_left
        self.visible_from_right = visible_from_right
    
    def __str__(self):
        return f'{self.height}'

def print_tree_grid(tree_grid, color_top_vis=False, color_bot_vis=False, color_l_vis=False, color_r_vis=False, hide_invisible=False):
    for tree_row in tree_grid:
        for tree in tree_row:
            tree_str = str(tree)

            color = None
            if color_top_vis and tree.visible_from_top:
                color = RED
            elif color_bot_vis and tree.visible_from_bot:
                color = RED   # GREEN
            elif color_l_vis and tree.visible_from_left:
                color = RED   # YELLOW
            elif color_r_vis and tree.visible_from_right:
                color = RED   # MAGENTA
            elif hide_invisible \
                    and not tree.visible_from_top \
                    and not tree.visible_from_bot \
                    and not tree.visible_from_left \
                    and not tree.visible_from_right:
                color = BLACK
            if color:
                tree_str = f'{color}{tree_str}{RESET}'

            print(tree_str, end='')
        print('\n', end='')

def print_tree_grid_visibility_from_all_sides(tree_grid, hide_invisible):
    print('\nFrom top:')
    print_tree_grid(tree_grid, color_top_vis=True)
    print('\nFrom left:')
    print_tree_grid(tree_grid, color_l_vis=True)
    print('\nFrom right:')
    print_tree_grid(tree_grid, color_r_vis=True)
    print('\nFrom bottom:')
    print_tree_grid(tree_grid, color_bot_vis=True)
    print('\nAll sides:')
    print_tree_grid(tree_grid, color_top_vis=True, color_l_vis=True, color_r_vis=True, color_bot_vis=True, hide_invisible=hide_invisible)
    print('')

def parse_file_into_tree_grid(inputfile):
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()

    tree_rows = contents.split('\n')[:-1]
    num_rows = len(tree_rows)
    num_cols = len(tree_rows[0])
    
    tree_grid = []
    for row, raw_tree_row in enumerate(tree_rows):
        tree_row = []
        for col, tree_height in enumerate(raw_tree_row):
            # initialize tree -- set outside edges as visible already
            tree_row.append(
                Tree(
                    height = tree_height,
                    visible_from_top=(row == 0),
                    visible_from_bot=(row == num_rows-1),
                    visible_from_left=(col == 0),
                    visible_from_right=(col == num_cols-1)
                )
            )
        tree_grid.append(tree_row)
    return tree_grid

# part one
def count_visible_trees_old(tree_grid):
    
    # first, iterate over the inner trees in the grid to see which ones are visible and which aren't.
    
    # will do x4 passes: t->b, b->t, l->r, r->l and mark trees as visible or not.
    exclude_outer_cols = exclude_outer_rows = slice(1, -1)

    # t <-> b
    TOP_TO_BOT = 1
    BOT_TO_TOP = 0
    for direction in [TOP_TO_BOT, BOT_TO_TOP]:
        # initialize starting row of heights based on outermost trees
        outside_row = tree_grid[0 if direction else -1]
        min_visible_heights_from_dir = [tree.height for tree in outside_row[exclude_outer_cols]]

        # create list of trees that we need to check
        if direction:
            trees_for_visibility_check = tree_grid[1:]  # skip first row, take all other rows
        else:
            trees_for_visibility_check = reversed(tree_grid[:-1]) # skip last row, and go back -> front

        for tree_row in trees_for_visibility_check:
            for col, tree in enumerate(tree_row[exclude_outer_cols]):
                if tree.height > min_visible_heights_from_dir[col]:
                    min_visible_heights_from_dir[col] = tree.height
                    if direction:
                        tree.visible_from_top = True
                    else:
                        tree.visible_from_bot = True
    # l <-> r
    L_TO_R = 1
    R_TO_L = 0
    for direction in [L_TO_R, R_TO_L]:
        outside_col_idx = 0 if direction else len(tree_grid[0])-1
        min_visible_heights_from_dir = [tree_row[outside_col_idx].height for tree_row in tree_grid[exclude_outer_rows]]

        for row, tree_row in enumerate(tree_grid[exclude_outer_rows]):
            for col in range(1, len(tree_grid)-1) if direction else reversed(range(0, len(tree_grid)-2)):
                tree = tree_row[col]

                if tree.height > min_visible_heights_from_dir[row]:
                    min_visible_heights_from_dir[row] = tree.height
                    if direction:
                        tree.visible_from_left = True
                    else:
                        tree.visible_from_right = True

    # then, loop over all the trees and see whether they are visible or not!
    visible = 0
    for tree_row in tree_grid:
        for tree in tree_row:
            if tree.visible_from_top or tree.visible_from_bot or tree.visible_from_left or tree.visible_from_right:
                visible += 1

    return visible, tree_grid

def count_visible_trees(tree_grid):

    # assumption - all rows have same len (it's a perfect rectangle)
    num_rows = len(tree_grid)
    num_cols = len(tree_grid[0])

    # top -> bottom annotation
    top_row = tree_grid[0]
    trees_to_check = tree_grid[1:]
    min_visible_heights_from_top = [tree.height for tree in top_row]
    for tree_row in trees_to_check:
        for col, tree in enumerate(tree_row):
            if tree.height > min_visible_heights_from_top[col]:
                min_visible_heights_from_top[col] = tree.height
                tree.visible_from_top = True

    # bottom -> top annotation
    bot_row = tree_grid[-1]
    trees_to_check = tree_grid[num_rows-2::-1]  # iterating in reverse, skipping bottom row
    min_visible_heights_from_bot = [tree.height for tree in bot_row]
    for tree_row in trees_to_check:
        for col, tree in enumerate(tree_row):
            if tree.height > min_visible_heights_from_bot[col]:
                min_visible_heights_from_bot[col] = tree.height
                tree.visible_from_bot = True

    # left -> right annotation
    min_visible_heights_from_left = [tree_row[0].height for tree_row in tree_grid]  # iterate rows, take col 0 (leftmost)
    for row, tree_row in enumerate(tree_grid):
        # skip the first column, since that's the leftmost
        for tree in tree_row[1:]:
            if tree.height > min_visible_heights_from_left[row]:
                min_visible_heights_from_left[row] = tree.height
                tree.visible_from_left = True

    # right -> left annotation
    min_visible_heights_from_right = [tree_row[-1].height for tree_row in tree_grid]  # iterate rows, take rightmost col
    for row, tree_row in enumerate(tree_grid):
        for tree in tree_row[num_cols-2::-1]:
            if tree.height > min_visible_heights_from_right[row]:
                min_visible_heights_from_right[row] = tree.height
                tree.visible_from_right = True

    # now, count how many trees are visible from any angle!
    visible = 0
    for tree_row in tree_grid:
        for tree in tree_row:
            if tree.visible_from_top or tree.visible_from_bot or tree.visible_from_left or tree.visible_from_right:
                visible += 1

    return visible, tree_grid

if __name__ == '__main__':
    for inputfile in ['example.txt', 'input.txt']:
        print(f'--- {inputfile}', '-'*(90-len(inputfile)))
        tree_grid = parse_file_into_tree_grid(inputfile)
        
        print('\nOriginal grid:')
        print_tree_grid(tree_grid)

        _num_v_trees, _mod_tree_grid          = count_visible_trees_old(copy.deepcopy(tree_grid))
        # print('\nAnnotated grid:')
        # print_tree_grid_visibility_from_all_sides(_mod_tree_grid)

        num_visible_trees, modified_tree_grid = count_visible_trees(copy.deepcopy(tree_grid)) # part one
        print('\nAnnotated grid:')
        print_tree_grid_visibility_from_all_sides(modified_tree_grid, hide_invisible=inputfile=='input.txt')

        print(f'\nPart one: visible trees = {num_visible_trees} / {len(modified_tree_grid)*len(modified_tree_grid[0])}')
        print(f'Part one old v trees =    {_num_v_trees} / {len(modified_tree_grid)*len(modified_tree_grid[0])}')