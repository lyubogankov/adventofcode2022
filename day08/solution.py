'''
Core data structure -- "tree grid", aka 2-dimensional list of lists
    Outside list indices = rows.  At each index is a list.
    Inner list indices = cols.  At each index is a Tree object.

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
            visible_from_right=False,
            visible_from_max_scenic_score_tree=False):
        self.height = height
        # for part 1
        self.visible_from_top   = visible_from_top
        self.visible_from_bot   = visible_from_bot
        self.visible_from_left  = visible_from_left
        self.visible_from_right = visible_from_right
        # for part 2
        self.visible_from_max_scenic_score_tree = visible_from_max_scenic_score_tree
    
    def __str__(self):
        return f'{self.height}'

    def is_visible_from_outside(self):
        return self.visible_from_top \
                or self.visible_from_bot \
                or self.visible_from_left \
                or self.visible_from_right

def print_tree_grid(tree_grid, color_top_vis=False, color_bot_vis=False, color_l_vis=False, color_r_vis=False, hide_invisible=False):
    for tree_row in tree_grid:
        for tree in tree_row:
            tree_str = str(tree)

            color = None
            # part one
            if color_top_vis and tree.visible_from_top:
                color = RED
            elif color_bot_vis and tree.visible_from_bot:
                color = RED   # GREEN
            elif color_l_vis and tree.visible_from_left:
                color = RED   # YELLOW
            elif color_r_vis and tree.visible_from_right:
                color = RED   # MAGENTA
            # part two
            elif tree.visible_from_max_scenic_score_tree:
                color = RED
            # general
            elif hide_invisible and not tree.is_visible_from_outside():
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
    
    print_tree_grid_visibility_total(tree_grid, hide_invisible)  # print overlay of all sides
    print('')

def print_tree_grid_visibility_total(tree_grid, hide_invisible):
    print('\nAll sides:')
    print_tree_grid(tree_grid, color_top_vis=True, color_l_vis=True, color_r_vis=True, color_bot_vis=True, hide_invisible=hide_invisible)

def parse_file_into_tree_grid(inputfile):
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()
    tree_rows = contents.split('\n')[:-1]
    
    tree_grid = []
    for raw_tree_row in tree_rows:
        tree_row = []
        for tree_height in raw_tree_row:
            tree_row.append(Tree(height=tree_height))
        tree_grid.append(tree_row)
    return tree_grid

# part one
def count_visible_trees(tree_grid):
    '''TODO: combine x4 annotation passes into one loop!'''

    # assumption - all rows have same len (it's a perfect rectangle)
    num_rows = len(tree_grid)
    num_cols = len(tree_grid[0])

    # annotate all outside trees
    for tree in tree_grid[ 0]: tree.visible_from_top = True
    for tree in tree_grid[-1]: tree.visible_from_bot = True
    for tree_row in tree_grid:
        tree_row[ 0].visible_from_left = True
        tree_row[-1].visible_from_right = True

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

# part two
def calculate_scenic_score(tree_grid, row_idx, col_idx, annotate_visibility=False, print=False):
    '''
    
    Originally had two loops - one for north/south iteration (iterate rows, constant col),
        and another for east/west iteration (constant row, iterate cols).
    I managed to combine these two loops into a single loop!
    The two changes were 1) having nested for loops for the potential row/col iteration, and using row/col slices
                         2) having a breakout variable to ensure that we break from both inner and outer for loops.
    '''

    num_rows = len(tree_grid)
    num_cols = len(tree_grid[0])  # assuming rectangular grid, aka all rows have same len
    
    # this is the tree from which we want to calculate the visibility score
    tree = tree_grid[row_idx][col_idx]

    scenic_score = 1

    directional_passes = [
        ('north', row_idx > 0,          slice(row_idx-1, None, -1), slice(col_idx, col_idx+1)),
        ('south', row_idx < num_rows-1, slice(row_idx+1, None,  1), slice(col_idx, col_idx+1)),
        ('east',  col_idx < num_cols-1, slice(row_idx, row_idx+1),  slice(col_idx+1, None,  1)),
        ('west',  col_idx > 0,          slice(row_idx, row_idx+1),  slice(col_idx-1, None, -1))
    ]

    for look_dir, not_border_tree_condition, row_slice, col_slice in directional_passes:
        if print: print(f'        looking {look_dir}: ', end='')
        visible_trees = 0
        if not_border_tree_condition:
            breakout = False
            for tree_row in tree_grid[row_slice]:
                for comp_tree in tree_row[col_slice]:
                    visible_trees += 1
                    if print: print(f'{comp_tree.height} ', end='')
                    if annotate_visibility:
                        comp_tree.visible_from_max_scenic_score_tree = True
                    if comp_tree.height >= tree.height:
                        breakout = True
                        break
                if breakout:
                    break
        scenic_score *= visible_trees   
        if print: print(f' vt {visible_trees}')
        if scenic_score == 0:
            return scenic_score

    return scenic_score

def find_tree_with_highest_scenic_score(tree_grid, print=False):
    
    num_rows = len(tree_grid)
    num_cols = len(tree_grid[0])  # assuming rectangular grid, aka all rows have same len

    # find tree with highest scenic score
    max_scenic_score = 0
    max_scenic_score_tree_row = max_scenic_score_tree_col = -1
    for row_idx in range(num_rows):
        for col_idx in range(num_cols):
            if print: print(f'    ({row_idx}, {col_idx}) {tree_grid[row_idx][col_idx].height}')
            score = calculate_scenic_score(tree_grid, row_idx, col_idx, print=print)
            if print: print(f'        scenic score: {score}')
            if score > max_scenic_score:
                max_scenic_score = score
                max_scenic_score_tree_row = row_idx
                max_scenic_score_tree_col = col_idx

    # after we're done -- do some coloring for printout!  Toggle visibility value for printout.
    _ = calculate_scenic_score(tree_grid, max_scenic_score_tree_row, max_scenic_score_tree_col, annotate_visibility=True, print=print)
            
    return max_scenic_score, tree_grid

if __name__ == '__main__':
    for inputfile in ['example.txt', 'input.txt']:
        print(f'--- {inputfile}', '-'*(90-len(inputfile)))
        tree_grid = parse_file_into_tree_grid(inputfile)
        
        print('\nOriginal grid:')
        print_tree_grid(tree_grid)

        # part one
        num_visible_trees, modified_tree_grid_p1 = count_visible_trees(copy.deepcopy(tree_grid))
        print('\nAnnotated grid:')
        print_tree_grid_visibility_from_all_sides(modified_tree_grid_p1, hide_invisible=inputfile=='input.txt')
        print(f'\nPart one: visible trees = {num_visible_trees} / {len(modified_tree_grid_p1)*len(modified_tree_grid_p1[0])}')

        # part two
        max_scenic_score, modified_tree_grid_p2 = find_tree_with_highest_scenic_score(copy.deepcopy(tree_grid))
        print('\nAnnotated grid:')
        print_tree_grid_visibility_total(modified_tree_grid_p2, hide_invisible=False)
        print(f'\nPart two: max scenic score = {max_scenic_score}')