# Day 09: Rope Bridge

## [Part one description](https://adventofcode.com/2022/day/9) (adventofcode.com)

**tl;dr**:

.


## Part One

### Problem Breakdown

This puzzle involves simulating a simplified rope with two knots.  The input contains the series of relative movements applied to the *head*  (H) knot (moving it up/down/left/right by a specified number of grid spaces), and I must simulate what happens to the *tail* (T) knot in response.

Simulation rules provided:

0. The knots must always be adjacent after a move is applied to H and T's reaction is simulated- either in same row/col or diagonal.

1. If H and T are in the same grid space, H is above T.  If this is the result of moving H, T does not need to move because Rule 0 is not violated.

2. If H and T are in adjacent in same row or col prior to moving, and H is moved one step away from T in the row or col of adjacency, T must make the same move to remain close enough to H and satisfy Rule 0. 

3. Otherwise, if H and T are diagonally adjacent prior to moving H, T must move diagonally to keep up and ends up in the same row or col as H.

During the simulation, I need to keep track of the grid positions that T visits and count the number of unique positions visited.


### Solution

**Setup - defining data structures**

I put a lot of time into defining data structures to express puzzle components (listed here in their Part One versions):

- `Point_2D`: a `class` to represent an (x, y) point on the grid.   Wrote `__repr/str__`, `__add/iadd/sub__`, and `__eq/hash__`, dunder/magic methods for convinience

- `Move`: a `namedtuple` containing the atomic transformation (up/down/left/right one grid space, as a `Point_2D` object), number of repetitions, and name (string representation of move direction)

- `Grid`: a `namedtuple` containing two `Point_2D`s (top left, and bottom right coords) which define the grid boundaries.


**Simulation**

Instead of using a `list`-of-`list`s to keep track of the grid state like in Day08, I realized that each knot could be represented perfectly by a `Point_2D` object, to which I could apply moves (also containing `Point_2D` objects) as needed!  No `lists` needed :grin:

The main simulation loop is quite simple:
1. Initialize all knots to start position
2. Iterate over list of moves (already parsed from input text file).  Apply each move and update the knot positions!

I added two grid options -- fixed and dynamic.
- Fixed grid requires knowledge that the rope will never move outside of the grid coordinates.  I used this for my unit tests during development and for generating animations.
- Dynamic grid starts as a 1x1 which grows as the rope head is moved.  I used this for the puzzle input, because I didn't know in advance how large of a grid would be required to fit the entire move list prior to successfully running the simulation!


**Unit Testing (`test_solution.py`)**

This puzzle was more involved than prior days', and I decided to extend the practice of matching the printout format of the puzzle description and write unit tests to directly compare my simulation output to the description's worked example using Python's builtin `unittest` module.

Writing unit tests forced my code to be more modular - 
1. `simulate_rope` -> `update_all_knot_pos` -> `print_current_grid_state` -> `generate_current_grid_state_string` -> 


## Part Two

### Problem Breakdown

Instead of simulating a rope with two knots (H, T), I must now simulate the movement of a rope with *ten* knots (H, 1, 2, ... , 9) while still keeping track of the number of unique grid positions visited by the last knot (9).


### Solution



## Bonus - rope with 50 knots on a large grid!

- make the characters unique, but it can't just be 1-9.  Need lowercase alphabet + symbols?  Could just do lowercase alphabet - H + 26 chars = len 27

- make it a perfectly looping gif.  Make grid height/width be odd, and start the rope at the very center.  Then, apply a series of moves and have the entire rope and up right back at the center.  Before ending, flash the moves made by the tail, and then loop again!