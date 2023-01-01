# Advent of Code 2022
[adventofcode.com/2022/](https://adventofcode.com/2022/)

I read about Advent of Code earlier this year and was excited to participate once December rolled around!

The advent calendar consists of daily programming puzzles, starting on Dec 1st and ending on the 25th - the puzzles get progressively more difficult!  The inputs are text files, and the question answers are entered into the puzzle webpage for grading, so any programming language can be used.

Each puzzle consists of two related parts, but the description for the second part is only available once a correct solution to the first part has been found and entered into the puzzle page.  The descriptions outline the problem and contain a small worked example to demonstrate the puzzle mechanics.

## My goals

- **Have fun!**  I used Python, a language with which I'm already comfortable, so that I could focus on higher-level solution aspects like extensibility, algorithms and data structures without the friction of worrying about syntax.

- **Write extensible solutions**  After completing the first several puzzles, I began noticing that each puzzle's two parts were somehow related.
    - My goal from Day 05 onwards was to implement one solution that can answer both parts of the puzzle with as much shared code as possible.  This usually involves refactoring once I finish part one and read over the second part's puzzle description.
    - From Day 10 onwards, I began trying to predict which elements could change from parts one -> two.  I write a list of what might change and try to write my code such that these changes won't be painful to make.  While I haven't correctly guessed the change yet, this has been a useful thought exercise and has resulted in more modular code!

- **Practice writing unit tests**  I've been strongly advised by two different mentors to write unit tests for my code.  As the puzzles became more complicated, matching my solution's console printout to the worked example became time-consuming.
    - Starting with Day 09, I have begun implementing unit tests that directly leverage the problem description's worked example printouts ([example](#unit-testing)), which has sped up my problem solving and gives me assurance that I'm on the right track.

## I'm particularly proud of several solutions!

- [Day 08 (Treetop Tree House)](/day08/)
    - In addition to solving parts one/two, I also created command-prompt animation to visualize a related question.
- [Day 09 (Rope Bridge)](/day09/)
    - First started implementing unit testing (using Python's `unittest` module), which ended up being a huge help in understanding the puzzle.  Implemented command-prompt animation to view the rope moving!
- [Day 11 (Monkey in the Middle)](/day11/)
    - Learned some basic `numpy` for optimization and modular arithmetic for solving the problem - part two was hard!

---

## General problem structure & my problem solving strategies

### Input text file -> internal program state

Each of the puzzle inputs is a plaintext file, which needs to be parsed into some kind of data structure before I can perform the simulation and calculate the answer.

**regular expressions**

I used regular expressions for several of my input file parsing functions.  Example from Day 11 (Monkey in the Middle):

The input text consists of blocks of text describing the different monkeys playing the game:

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

I recently learned about the verbose mode of Python's regular expression module from a [Stack Overflow answer by Raymond Hettinger](https://stackoverflow.com/a/72538070), and I quite like it's readability!  The only gotcha is that verbose mode ignores all whitespace, so in order to match spaces I have to use brackets (`[ ]`), though in my opinion it doesn't detract too much from readability.

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

**simple classes and namedtuples**

I wrote simple classes to group related variables and functions, and defined my own double-underscore (dunder / magic) methods to control how each object gets printed (`__str__` and `__repr__`), as well as some mathematical operations (like `__add__` and `__sub__` for a 2D Cartesian-coordinate Point class for [Day 09](/day09/)).

The `__str__` method was especially useful for formatting the printout to match the problem description, which allowed me to easily write unit tests!

**data structures**

So far, I've used:
- lists & lists-of-lists
- dictionaries & sets
- a `deque` (double-ended queue)
- a 1-D `numpy` nd-array

### Simulation and calculation
. simulate change(s), calculate something
    . Predicting what'll change from parts 1 -> 2
        . if multiple rounds of simulation are involved - try to make function that simulates a single cycle (or n cycles) given input state and outputs final state
    . making parameterized functions

### Unit testing
. unit testing to validate against example(s) given in problem description
    . give specific example -- day09 rope simulation!