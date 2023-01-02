# Advent of Code 2022 ([website link](https://adventofcode.com/2022/))

I read about Advent of Code earlier this year and was excited to participate once December rolled around!

The advent calendar consists of daily programming puzzles, starting on Dec 1st and ending on the 25th - the puzzles get progressively more difficult!  The inputs are text files, and the question answers are entered into the puzzle webpage for grading, so any programming language can be used.

Each puzzle consists of two related parts, but the description for the second part is only available once a correct solution to the first part has been found and entered into the puzzle page.  The descriptions outline the problem and contain a small worked example to demonstrate the puzzle mechanics.

## My goals

- **Have fun!**  I used Python, a language with which I'm already comfortable, so that I could focus on higher-level solution aspects like extensibility, algorithms and data structures without the friction of worrying about syntax.

- **Write extensible solutions:**  After completing the first several puzzles, I began noticing that each puzzle's two parts were somehow related.
    - My goal from Day 05 onwards was to implement one solution that can answer both parts of the puzzle with as much shared code as possible.  This usually involves refactoring once I finish part one and read over the second part's puzzle description.
    - From Day 10 onwards, I began trying to predict which elements could change from parts one -> two.  I write a list of what might change and try to write my code such that these changes won't be painful to make.  While I haven't correctly guessed the change yet, this has been a useful thought exercise and has resulted in more modular code!

- **Practice writing unit tests:**  I've been strongly advised by two mentors to write unit tests for my code.  As the puzzles became more complicated, matching my solution's console printout to the worked example became time-consuming.
    - Starting with Day 09, I began implementing unit tests that directly leverage the problem description's worked example printouts ([example](#unit-testing)), which has sped up my problem solving and gives me assurance that I'm on the right track.

## I'm particularly proud of several solutions!

- [Day 08 (Treetop Tree House)](/day08/)
    - In addition to solving parts one/two, I also created command-prompt animation to visualize a related question.
- [Day 09 (Rope Bridge)](/day09/)
    - First started implementing unit testing (using Python's `unittest` module), which ended up being a huge help in understanding the puzzle.  Implemented command-prompt animation to view the rope moving!
- [Day 11 (Monkey in the Middle)](/day11/)
    - Learned some basic `numpy` for optimization and modular arithmetic for solving the problem - part two was hard!

## General problem structure & my problem solving strategies

### Input text file -> internal program state

Each of the puzzle inputs is a plaintext file, which needs to be parsed into some kind of data structure before I can perform the simulation and calculate the answer.

**regular expressions**

I used regular expressions for several of my input file parsing functions.  Example from Day 11 (Monkey in the Middle):

The input text consists of blocks of text describing the different monkeys playing the game.

```
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  ...
```

Each monkey has a list of one or more starting items, an operation (* constant, + constant, * old), and two targets to whom to throw items based on a divisibility check.

In order to extract all of this information, I used a pre-compiled verbose regular expression with named matching groups.

I recently learned about the verbose mode of Python's regular expression module from a [Stack Overflow answer by Raymond Hettinger](https://stackoverflow.com/a/72538070), and I quite like its readability!  The only gotcha is that verbose mode ignores all whitespace, so in order to match spaces I have to use brackets (`[ ]`), though in my opinion it doesn't detract too much from readability.

```python
pattern = re.compile(r"""
          Monkey[ ](?P<monkey_idx>[\d]+):
        | Starting[ ]items:(?P<items_csv>[\d,\s]*)
        | Operation:[ ]new[ ]=[ ]old[ ](?P<operation>.+)
        | Test:[ ]divisible[ ]by[ ](?P<divis_const>\d+)
        | If[ ] true:[ ]throw[ ]to[ ]monkey[ ](?P<divis_throw_target>\d+)
        | If[ ]false:[ ]throw[ ]to[ ]monkey[ ](?P<nondivis_throw_target>\d+)
    """, re.VERBOSE)
```

Then, as I loop over the lines in the input file, I can either use an `if`/`elif` block or a `match` statement to check the different cases.  Regardless of the method, I need to check the name of the matching group, if any:

```python
for line in inputfile.read():
    mo = pattern.fullmatch(line)
    if mo is None:
        continue
    match mo.lastgroup:
        case 'monkey_idx':            # ...
        case 'items_csv':             # ...
        case 'operation':             # ...
        case 'divis_const':           # ...
        case 'divis_throw_target':    # ...
        case 'nondivis_throw_target': # ...
```

**classes and namedtuples**

I often use classes and `namedtuples` to represent different elements within each puzzle solution.

`namedtuples` are useful for representing simpler collections of attributes, whereas classes are useful when I need more control over how the object is printed out and when I want to bundle additional functionality with the class as member functions.

To achieve control over object printing, I defined my own double-underscore (dunder / magic) methods `__str__` and `__repr__`.  The `__str__` method was especially useful for formatting the printout to match the problem description, which allowed me to easily write unit tests!

Additionally, I defined sometimes defined dunder methods for some mathematical operations, like `__add__` and `__sub__` for a 2D Cartesian-coordinate Point class for [Day 09](/day09/).

**data structures**

So far, I've used:
- lists & lists-of-lists
- dictionaries & sets
- a `deque` (double-ended queue, from `collections` module)
- a 1-D `numpy` `nd-array`

### Simulation and calculation

This is the meat of the puzzle solution - after reading the input text file and parsing it into a more useful form (with data structures and classes/namedtuples), the input needs to be transformed in some way to arrive at the output.

I've tried to write modular solutions, where as much code as possible is shared between parts one/two.

**Ex: When I need to calculate a summary statistic, write a separate function to generate the collection**

[Day 07](/day07/) was a puzzle involving a directory tree of files/directories.  The two parts asked different questions about the tree - after completing part one and starting on part two, I refactored my solution to have a generic function that takes a file (sub)tree and applies a criteria function to decide which directories meet the criteria.

```python
def make_list_of_dir_meeting_criteria(current_dir, criteria_fn):
    dirs_meeting_criteria = []
    if criteria_fn(current_dir):
        dirs_meeting_criteria.append(current_dir)
    # current directory can contain other Directories and/or Files
    for item in current_dir.contents:
        if type(item) == Directory:
            # recursively traverse directory tree into sub-directories
            dirs_meeting_criteria += make_list_of_dir_meeting_criteria(item, criteria_fn)
    return dirs_meeting_criteria
```

The functions of part one/two call this function in order to answer their respective questions:

```python
def part_one(root):
    '''Need to find all directories that contain <= 100000, and print their sum.'''
    dirs_below_size = make_list_of_dir_meeting_criteria(current_dir=root, criteria_fn=lambda dir: dir.contained_size <= 100_000)
    return sum(dir.contained_size for dir in dirs_below_size)

def part_two(root):
    '''What is the smallest directory we can delete to free up enough space for update?
    Total disk space = 70_000_000, size needed for update = 30_000_000.
    '''
    current_disk_usage = root.contained_size
    current_free_space = 70_000_000 - current_disk_usage
    space_to_free_for_update = 30_000_000 - current_free_space

    dirs_above_size = make_list_of_dir_meeting_criteria(current_dir=root, criteria_fn=lambda dir: dir.contained_size >= space_to_free_for_update)
    return min(dir.contained_size for dir in dirs_above_size)
```

The underlying pattern for generalization I took away from Day 07 is that when faced with a problem that requires me to find a sum, max, min, or perform some other calculation that requires knowledge of all collection elements, I can break up the problem into two parts:
1. Function that comes up with list of all items  (in example, `make_list_of_dir_meeting_criteria()`)
2. Function(s) that call the more general list-making function and apply needed operation.

**Ex: When I need to simulate multiple rounds, write a function that can simulate a single round**

[Day 10](/day10/) involved simulating a very simple processor with a single register and two instructions (no-ops, which do nothing, and addition, which adds pos/neg integers to X register).  I wrote a function that simulates the CPU, both per-cycle and on clock edges (between instructions).

```python
def run_instructions_and_return_cpustate(instr_list, instr_start_idx=0, start_cycle=0, num_cycles=None, mid_instr_start_cycles=0, cpu_state={'register_x' : 1}):

    if num_cycles is not None:
        end_cycle = start_cycle + num_cycles
    cycle_count = start_cycle

    for instr_num, instruction in enumerate(instr_list[instr_start_idx:], start=1):
        # instructions have different execution times, measured in number of cycles
        for instr_cycle in range(mid_instr_start_cycles if instr_num == 1 else 0, instruction.num_cycles):
            cycle_count += 1
            if cycle_count == end_cycle:
                return cpu_state, instr_num, instr_cycle+1
        # apply operation, if needed
        if instruction.operation:
            cpu_state['register_x'] = instruction.operation(instruction.arg, cpu_state['register_x'])
        # Added clause -- if we are trying to simulate clock boundary between cycles (num_cycles=0),
        #                 need to end after instruction is applied.
        if cycle_count == end_cycle:
            return cpu_state, instr_num, 0
    # if we weren't given an end cycle, we'll run out of instructions.  still want to return cpu state!
    return cpu_state, instr_num, None
```

This turned out to be very useful, as the second part required me to sample the X register at precise moments (during each instruction execution) for output to a simulated CRT display!

### Unit testing

As the puzzles became harder, the simulations required to answer them got more complicated.  Prior to [Day 09](/day09/), I tried to match the worked example printout formatting within my own code and printed to the console and manually compared my output to the worked example to ensure I was on the right track.

This became very difficult for Day 09, so I started writing unit tests.  I used a similar approach to my manual method, but instead of printing the strings to the console, I wrote a function to generate those strings and compared them to the worked example printouts (I copied them and put them into my unit test script).

For instance, Day 09 involved simulating a knotted rope (at first 2, then 10 total knots) as the first knot (the head) is moved around.  A series of motions are given in the worked example, and a motion-by-motion printout is provided.  I used this within my unit test directly!

Generating print string with format matching worked example printouts, within `solution.py`:

```python
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
            nextchar = '.'
            while curr_item < len(items) and items[curr_item].point.x == col_idx and items[curr_item].point.y == row_idx:
                nextchar = items[curr_item].printchar
                curr_item += 1
            print_grid_string += nextchar
        if row_idx > grid.botr.y:
            print_grid_string += '\n'
    return print_grid_string
```

Test code, within `test_solution.py`.  Note that `verify_atomic_move_rope_sim_n_knots()` is a separate, generic testing function I wrote during part two and is not shown here.

```python
def test_atomic_move_rope_simulation_2knots(self):
        atomic_move_outcomes = [
# R 4
'''......
......
......
......
TH....''',

'''......
......
......
......
sTH...''',

'''......
......
......
......
s.TH..''',

'''......
......
......
......
s..TH.''',

# U 4
...

# R 2
'''......
......
.H....
......
s.....''',

'''......
......
.TH...
......
s.....'''
        ]
        # initial condition
        grid = Grid.create_grid_with_dimensions(width=6, height=5)
        # run the sim!
        self.verify_atomic_move_rope_sim_n_knots(
            grid=grid, exfile=self.examplefile, per_move_outcomes=atomic_move_outcomes, num_knots=2, mode='atomic')
```

This unit testing was very useful during the second part of the puzzle, when the number of knots to simulate was increased to 10!  The movement of the rope became more complicated, and I discovered that my understanding the the *written* rope movement rules (which I implemented into my simulation function) did not match the worked example.

Setting `self.maxDiff = None` within the `unittest` framework allowed me to see the differences in my printed string versus the worked example and debug much more quickly!  (By default, differences above a certain number of characters are truncated, but `None` means there isn't a limit).

## Reflections

**[2023-Jan-01]**

I've solved the first 11 puzzles so far.  It's been quite fun!
- After solving several of the puzzles, I noticed that parts one and two were related and began thinking about what elements might change from parts one -> two when writing my solution to part one.  This has made my code more modular!
- I've incorporated unit testing into my solutions, which speeds up debug and gives me confidence that my solution still works when I make changes or refactor.
- This is the first project that I'm thoroughly documenting on GitHub - it's been fun learning GH-flavored Markdown and getting my thoughts out on the keyboard.
    - In a [recent blog post](https://nedbatchelder.com/blog/202212/talk_python_to_me_tools_for_readme.html), Ned Batchelder shared some of his principles about writing READMEs, and the first one inspired me:

> Writing about your work helps you understand your work.

- It's also been fun to animate two of my solutions - Days [08 (Treetop Tree House)](/day08/) and [09 (Rope Bridge)](/day09/).  It wasn't part of the puzzle requirements, but I found that visualizing and animating the simulation state improved my understanding of the puzzle and was pretty to look at!