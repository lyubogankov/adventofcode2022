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
        color = None
        if self.visible_from_top:
            color = RED
        elif self.visible_from_left:
            color = YELLOW
        elif self.visible_from_right:
            color = MAGENTA
        elif self.visible_from_bot:
            color = GREEN
        return f'{color}{self.height}{RESET}' if color else f'{self.height}'

def print_tree_grid(tree_grid):
    for tree_row in tree_grid:
        for tree in tree_row:
            print(str(tree), end='')
        print('\n', end='')

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
def count_visible_trees(tree_grid):
    
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

if __name__ == '__main__':
    for inputfile in ['example.txt', 'input.txt']:
        print(f'--- {inputfile}', '-'*(90-len(inputfile)))
        tree_grid = parse_file_into_tree_grid(inputfile)
        
        print('\nOriginal grid:')
        print_tree_grid(tree_grid)

        num_visible_trees, modified_tree_grid = count_visible_trees(copy.deepcopy(tree_grid)) # part one
        print('\nAnnotated grid:')
        print_tree_grid(modified_tree_grid)

        print(f'\nPart one: visible trees = {num_visible_trees} / {len(modified_tree_grid)*len(modified_tree_grid[0])}')