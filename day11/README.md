### Day 11: Monkey in the Middle
[Part one description](https://adventofcode.com/2022/day/11) (adventofcode.com)

**tl;dr**: Pure-Python solution for part one ended up being too slow for part two.  Learned some `numpy` and modular arithmetic and implemented a more efficient solution!  Wrote unit tests for both parts using Python's `unittest` module.  Also learned about GitHub's README.md formatting features - used code blocks with syntax highlighting and LaTeX equations!


## Part One  (`solution.py`)
Problem breakdown:
- The game consists of multiple rounds.  I need to be able to simulate effects of N rounds
- Each round consists of turns -- one turn per monkey, from 0 -> M
- Each monkey's turn consists of handling each item in its possession, from 0 -> M.I (each monkey has a queue of I items)
- Each item handling consists of inspection (worry about item increases/decreases), and throwing to another monkey

I decided to create classes to represent monkeys and items.

**The `Monkey` class**

Has member variables with information from input text file:
- List of Item objects (more on this in a sec)
- Inspection-related: worry increase operation function / constant
- Throwing-related: divisibility constant, two potential targets
    - If the current item's worry level is divisible by monkey's divis constant, throw to first target; otherwise, to second.
- Number of items inspected, a counter that's incremented during per-round simulation

Additionally, I wrote a `__str__` method so that I could match the per-monkey printout shown in the problem description and input text file (for unit testing).  I did not write a `__repr__` method, because I could not find a way to properly print the worry-increase operation function name.

**The `Item` class**

The only per-item value to keep track of is its current worry level (quantified amount of worry viewer has for the item).

I defined several dunder methods for use with the per-monkey worry-increase operation: `__add__`, `__mul__`, and `__pow__`.  Additionally, I wrote `__str__` and `__repr__` methods for useful printouts.

**Reading from input file**

I used a verbose regular expression string with named groups to process the input file into `Monkey` objects.  I recently read about this method of using regex ([Raymond Hettinger, StackOverFlow](https://stackoverflow.com/a/72538070)) and I like its readability!  The one thing I dislike is that verbose mode ignores all whitespace, so in order to match spaces I have to use brackets (`[ ]`) - though it doesn't detract too much, imo.

```python
    # ...

    pattern = re.compile(r"""
          Monkey[ ](?P<monkey_idx>[\d]+):
        | Starting[ ]items:(?P<items_csv>[\d,\s]*)
        | Operation:[ ]new[ ]=[ ]old[ ](?P<operation>.+)
        | Test:[ ]divisible[ ]by[ ](?P<divis_const>\d+)
        | If[ ] true:[ ]throw[ ]to[ ]monkey[ ](?P<divis_throw_target>\d+)
        | If[ ]false:[ ]throw[ ]to[ ]monkey[ ](?P<nondivis_throw_target>\d+)
    """, re.VERBOSE)

    mo = pattern.fullmatch(line)

    if not mo:
        continue
    match mo.lastgroup:
        case 'monkey_idx': # ...
        case 'items_csv':  # ...
        # ...
```

**Unit testing**

I wrote unit tests (`test_solution.py`) so that I could compare the output of my solution to the problem description on the example input.  I wrote my solution to optionally generate strings that match the format of the puzzle description, so that I could use string comparison as the assertion within my unit tests.  I tested everything that was spelled out in the problem description, which was:
- Input file parsing
- Actions performed by each monkey during very first round
- Post-round game state for selected rounds between [1, 20]
- Per-monkey item inspection counts after round 20


## Part Two

### Initial attempt  (`solution.py`)

My solution was sufficiently fast to answer Part One, which required simulating 20 rounds.
Part Two exposed the inefficiency of my code, however - now I needed to simulate *10_000* rounds.  I let my code run for 5-10 minutes, and I saw in the console output that it had not even gotten to 1_000 rounds!

The first thing I did was to analyze the computational complexity of my per-round simulation.  There are three main `for` loops within my solution.  Need to iterate over:
- Game rounds [1, N]
- All monkeys [0, M)
- All items each monkey possesses [0, M.I)
    - This one is especially tricky, because the monkeys throw the items between each other.
    - Per-item worst case: in theory, an item can begin with Monkey 0 at the beginning of the round and be thrown to Monkey 1, then 2, and so forth until the very last monkey.
    - Overall worst case: all items start with Monkey 0 and are handled by every single monkey.

The worst case computational complexity is O(N * M * I), but in practice is better than that.  Still - 10_000 rounds, 4 monkeys, and 10 items proved too much for my method.

**Initial attempt (with different data structure)**

I noticed that I was using a Python `list` to store each Monkey's queue of items.  However, `lists`s have O(n) computational complexity when popping from the front of the `list` (as is required for a queue).

I replaced the `list` with the standard library's `collections.deque` ("double ended queue").  It has O(1) pops/appends to either side!  However, this improvement did not have a meaningful impact to my simulation's run time.

### Starting over from scratch (`solution_np.py`)

I thought for a while about how I could better utilize data structures to approach the problem.  Fresh off upgrading `solution.py` from `list`s -> `collections.deque`s, I wondered whether I could extend this idea and remove the queue of items from the `Monkey` class entierly.

Instead, I thought that having a separate collection of items that gets modified per-handling without ever being popped/appended could speed things up.  In addition, I wondered whether I could use matrix-like operations on slices of the item collection to speed up the computation of the per-item worry changes.

To this end, I investigated the popular Python library `numpy`!

**`numpy` investigation and implementation**

I read about various facets of the package:
- I was drawn to the purported speed ([What is Numpy - Why is NumPy Fast? (numpy.org)](https://numpy.org/doc/stable/user/whatisnumpy.html#why-is-numpy-fast))
- Its core data structure, `ndarrays`, support [broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html), which allows operations to be performed on `ndarrays`, even when the two arguments do not have the same shape.
    - For my use-case, I used it to implement the per-monkey operations (+ constant, * constant, ^2)
- I was also drawn to [structured arrays](https://numpy.org/doc/stable/user/basics.rec.html)
    - Instead of having a separate `Item` class, I represented each item with three integers:
        - owner Monkey number
        - item's index within the owner Monkey's queue
        - item's current worry level

However -- one thing that stood out to me after reading the docs is that the computational complexity of my problem would remain the same.  I still needed to simulate N rounds, iterating over each monkey per round (M monkeys), and operating on all items per monkey.  However, the combination of in-place operations and numpy's fast pre-compiled C loops vs Python's slow `for` loops is what decreases the test time (this ended up being my solution!).

Partway through my experimentation with structured arrays, I got stuck on how to broadcast each Monkey's operation onto the item worry levels.  If the items were represented using a 1D array of worry levels, I could directly operate on the array (`array *= c, += c, **=2`).  However, this notation does not work with structured arrays!

I then read about, and ended up using, `numpy.ndarray.view`s.  From the [docs](https://numpy.org/doc/stable/user/basics.copies.html), `view`s allow

> ... access (to) the internal data buffer directly... without copying data around.

Furthermore,

> It is possible to access the array differently by just changing certain metadata like stride and dtype without changing the data buffer.  This creates a new way of looking at the data and these new arrays are called views.

After also reading about [dtypes]() to solidify my understanding, this is how I implemented the overall items structured array:

```python
import numpy as np
# ...
# each item is represented by a 3-tuple when read in from the .txt file (owneridx, queueidx, worrylevel)
# item_values is a list of such tuples.
items = np.array(item_values, dtype=[('owneridx', np.uint64), ('queueidx', np.uint64), ('worrylevel', np.uint64)])
```

And this is how I was able to access just the per-item worry values as an `ndarray.view`, to which I was able to broadcast the per-Monkey operations.  The `view` method allowed me to "remap" my data structure from a structured array with three `np.uint64` values per element to a 1-D, normal `ndarray` with three times the number of elements (essentially unpacking the structured array, element-wise).  A very nice property of `view`s is they directly point to the array from which they were created - they are not a copy, and so any modifications I perform on the `view` are applied back to my original structured array!

```python
for i, monkey in enumerate(monkeys):
    _start = 0 if i == 0 else sum(m.num_items_held for m in monkeys[:i])
    _end   = _start + monkeys[i].num_items_held
    # assumption - items array is sorted
    current_items = items[_start:_end]
    # slice starts at idx 2 because of the structured array format (see prev code block - worrylevel is last)
    current_item_worrylvls = current_items.view(np.uint64)[2::3] 
```

Note!  In order for this to work, the item array must be sorted by Monkey and per-Monkey queue index (accomplished by calling `items.sort()` at the end of each round).

Using a structured `ndarray` required me to change the per-monkey flow within each round:

| `solution_np.py` (new) | `solution.py` (previous) |
| ----------- | ----------- |
| Slice item array to point to current monkey's items' worry levels | Loop over current Monkey's items.  Per-item: |
| Broadcast monkey's worry-increasing operation to all items        | Apply monkey's worry-increasing operation |
| Calculate divisibility for all items using broadcast              | Pick target based on current item worry level divisibility |
| Loop over items and re-assign owners based on divis array         | Perform throw - pop item from current Monkey's queue, append to target Monkey's queue |
| Re-sort items array | |

### Ever-increasing worry (part two's gotcha)

Once I implented the `numpy` data structure and approach described above, I was very pleased to see that the runtime was a lot faster - ~10s for 10_000 rounds!
However, my unit tests using the example data (running first 20 rounds) failed!

I didn't think much of it when I first read it, but part two has a sneaky gotcha!  While part one had a worry-decrease operation (`worry //= 3`) after the per-monkey worry increase operation (`+= c, *= c, **= 2`), this was *removed* for part two.  In my 20-round printout, I noticed that some of the items had very large worry levels.

I'm using 64-bit unsigned integers, which can store a value in the range `[0, 18_446_744_073_709_551_617]` (2^64^ - 1).  In the 13/20th round, one of the items overflowed!  This definitely affects the divisibility checks down the line and affects how the item gets thrown between monkeys, which affects my final answer.  This is no good!

A more careful read of the problem indicated that running into and eventually dealing with this issue was intended:

> You're worried you might not ever get your items back. So worried, in fact, that your relief that a monkey's inspection didn't damage an item no longer causes your worry level to be divided by three.

> Unfortunately, that relief was all that was keeping your worry levels from reaching **ridiculous levels**. You'll need to **find another way to keep your worry levels manageable**.

**Solution: modular arithmetic**

At first - tried dividing each item by least common multiple of all monkeys' divisors, but that didn't help.  My rationale was that if a number is divisible by the least common multiple of all the monkeys' divisors, it was also by definition divisible by each divisor and it would not change the outcome of the divisibility checks.

As I was mulling over the problem, a lunch conversation with a workplace mentor ([@dnovick](https://github.com/dnovick)) came to mind - he is passionate and deeply knowledgable about cryptography, and was talking about group theory and rings of integers modulo-N.  He mentioned the term "modular arithmetic" several times.  

Remembering this, I read about it on [Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic), and several things immediately jumped out at me:
- Definition: two integers *a* and *b* are congruent modulo *n* ($a \equiv b (mod n)$) if *n* if the following holds: *a - b = kn*
- Properties: if $a \equiv b$ (mod *n*), then
    - $a + k \equiv b + k$ (mod *n*)
    - $ka \equiv kb$ (mod *n*)
    - $a^{k} \equiv b^{k}$ (mod *n*), for any non-negative integer *k*

These properties are the same three types of operations that the monkeys can perform!

I was then stuck on what the *n* should be, and when I should take the modulus of each item's worry level.
I used my initial idea of the least common multiple of all monkeys' divisors and worked out an example on paper and subsequently "proved" the method:

Insert "proof" of my approach here!  Is it possible to insert LaTeX?  [Yessir :)](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)

The only modification to the code is taking the modulus of each item's worry level after each monkey increases the worry level using its operation.  The example unit test passed, and my answer against the input text file was correct!

## Reflection

This second part of this problem was quite difficult!  This is the first AoC puzzle that has required me to optimize my approach to make it faster, and it was a fun challenge.

Until now I've never used `numpy` for a personal project, and I've learned several useful tricks, like broadcasting and using `view`s for manipulation.  And learning how much faster it is than pure-Python `for` loops!

I also had fun dipping my toes into modular arithmetic.  I don't fully understand it (I could not write a mathematical proof establishing its truth across all inputs), but I was able to read about its properties on Wikipedia and use it for my solution, which I consider a win!