import copy
import re
from collections import namedtuple
from pprint import pprint


def crate_print(string):
    print(string, end='')
def print_crate_board(crate_board):
    max_height = max(len(stack) for stack in crate_board)
    num_stacks = len(crate_board)

    # need to print from top down!  print the crate stack...
    for height in reversed(range(max_height)):
        for stack in range(num_stacks):
            # careful - height is 0-idx, len is 1-idx
            if height > len(crate_board[stack])-1:
                crate_print('   ')  # no crate, 3 spaces
            else:
                crate_print(f'[{crate_board[stack][height]}]')
            crate_print(' ')
        crate_print('\n')
    # ... then print the stack designators
    for stack in range(num_stacks):
        crate_print(f' {stack + 1} ')
        if stack < num_stacks-1:
            crate_print(' ')
    crate_print('\n')

def crate_lines_to_board(crate_lines):
    # Input
    # -----
    # List of strings corresponding to the text file input for the crate stacks.
    # Assumption: all lines are the same length.
    # Assumption: crate names are each 1 character.
    # Note: the stacks are 1-indexed
    #
    # Output
    # ------
    # Crate board data structure
    # List of lists
    #   Outer list -- each idx represents a position in the crate stacks.
    #   Each inner list -- stack of crates.  Each crate is a string  (ex: '[A]')
    #       Order of elements within list acts like a stack!  LIFO.
    
    crate_board = []
    line_width = len(crate_lines[0])

    # for every 4 lines in the file, want to look at the 2nd one
    for idx in range(1, line_width, 4):
        # don't care about the last line
        crate_board.append([])
        # traverse from bottom to top, ignoring the last line
        for line in reversed(crate_lines[:-1]):
            if line[idx] == ' ':
                continue
            crate_board[-1].append(line[idx])

    return crate_board

def read_file(inputfile):
    
    Move = namedtuple('Move', ['num_crates', 'pos_from', 'pos_to'])
    parser_rawmove = re.compile(r"move (\d+) from (\d+) to (\d+)")

    crate_lines = []
    crate_board = []
    move_list = []

    done_with_crate_board = False
    with open(inputfile, 'r') as _inputfile:
        for line in _inputfile.readlines():
            if line == '\n':
                done_with_crate_board = True
                crate_board = crate_lines_to_board(crate_lines)
            elif not done_with_crate_board:
                crate_lines.append(line.replace('\n', ''))
            else:
                _num, _from, _to = map(int, parser_rawmove.search(line).groups())
                move_list.append(Move(_num, _from, _to))

    return crate_board, move_list

def apply_move_list_and_print_solution(crate_board, move_list, crane_move_fn, printmoves):
    if printmoves:
        print('Starting position:')
        print_crate_board(crate_board)
    # make all encoded moves
    for (num_crates, pos_from, pos_to) in move_list:
        idx_from = pos_from - 1
        idx_to   = pos_to   - 1
        crane_move_fn(crate_board, num_crates, idx_from, idx_to)
        if printmoves:
            print(f"--- from {pos_from} to {pos_to}, {num_crates} crate{'s' if num_crates > 1 else ''}")
            print_crate_board(crate_board)
    # finally, read out the top of each stack!
    print(f"Final answer: {''.join(stack[-1] for stack in crate_board)}")

def part_one(crate_board, move_list, printmoves):
    def cratemover_9000(crate_board, num_crates, idx_from, idx_to):
        for _ in range(num_crates):
            crate = crate_board[idx_from].pop()
            crate_board[idx_to].append(crate)
    print('part one')
    apply_move_list_and_print_solution(crate_board, move_list, cratemover_9000, printmoves)

def part_two(crate_board, move_list, printmoves):
    def cratemover_9001(crate_board, num_crates, idx_from, idx_to):
        crane_arm_stack = []
        for _ in range(num_crates):
            crate = crate_board[idx_from].pop()
            crane_arm_stack.append(crate)
        for _ in range(num_crates):
            crate = crane_arm_stack.pop()
            crate_board[idx_to].append(crate)
    print('part two')
    apply_move_list_and_print_solution(crate_board, move_list, cratemover_9001, printmoves)

if __name__ == '__main__':
    # need to open file and parse into crate gameboard and list of moves.
    for inputfile in ['example.txt', 'input.txt']:
        print(f'--- {inputfile}')
        printmoves = inputfile == 'example.txt'
        crate_board, move_list = read_file(inputfile)
        # need to deepcopy bc all the operations rely on mutability of lists (no return values)
        part_one(copy.deepcopy(crate_board), move_list, printmoves)
        part_two(copy.deepcopy(crate_board), move_list, printmoves)

# '''
# Notes  (after finishing part_one and reading over part_two requirements)
# An assumption I made during part 1 needed to be undone!
#     During coding for part one, I interpreted moves that involved multiple crates as a series of individual moves.
#     However, part two changed the move mechanic to allow movement of stacks of crates (FIFO-style) vs individual crates (LIFO-style).

# To undo this, needed to make changes to the Move tuple (re-added num crates field) and left interpretation of moves
#     to each of the parts.

#     Now, the part_one() routine is free to interpret Moves with num_crates > 1 as a series of individual moves,
#     while part_two() can interpret Moves with num_crates > 1 as a single move that preserves order.


# Notes (after finishing both parts)
# I refactored the code to take common operations from parts 1/2 and put them into common function, apply_move_list_and_print_solution().
# The only difference between parts one/two is how the crane works, so I made that its own function to be passed into the common move applier.
# '''