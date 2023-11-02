# Day 14: Regolith Reservoir

## [Part one description](https://adventofcode.com/2022/day/14) (adventofcode.com)

**tl;dr**


## Part One

### Problem Breakdown

### Solution


## Part Two

### Problem Breakdown

### Solution

#### initial attempt - too slow!

I tried minimally modifying my solution for Part One , and while this worked for the example the computation time went through the roof for the full input.

I didn't have a good sense of where the slowdown in my code was (unlike in prior puzzles), so I tried using the Python standard library's `cProfile` for the first time!  Their [quickstart guide](https://docs.python.org/3/library/profile.html) was straightforward, and I was quickly able to isolate which function was causing the issue.

Setting up the profiler:

```Python
import cProfile
# run the simulation.  Here, I am "raising" the sand origin point by 35 tiles
# this causes many more sand units to be dropped, giving a longer and more representative simulation for profiling
cProfile.run("obtain_part_two_simulated_board(inputfile='example.txt', sand_origin=Point(500, -35))", 'sim_stats')
# format the output!  sort by total time
import pstats
p = pstats.Stats('sim_stats')
p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()
```

Output:

```
10203670 function calls in 9.240 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   117482    4.376    0.000    7.114    0.000 {method 'union' of 'set' objects}
  4562810    2.300    0.000    2.779    0.000 point.py:34(__eq__)
   117482    1.274    0.000    8.598    0.000 solution.py:47(is_tile_occupied)
  4562810    0.479    0.000    0.479    0.000 {built-in method builtins.isinstance}
    64714    0.319    0.000    9.114    0.000 solution.py:67(fall_step)
   117533    0.103    0.000    0.142    0.000 point.py:13(__add__)
   235074    0.091    0.000    0.091    0.000 point.py:3(__init__)
   117482    0.077    0.000    7.190    0.000 solution.py:44(occupied_tiles)
    64714    0.068    0.000    9.181    0.000 solution.py:104(simulate_time_step)
   119593    0.063    0.000    0.095    0.000 point.py:42(__hash__)
```

Takeaway: `set.union()` is taking way more time than I expected, about 47% based on the `tottime` (4.276s) vs overall runtime (9.240s) numbers.

I wrote the `Board` class, which is a live representation of the current 2D-cave-slice during simulation, in the following manner (below) - every check as to whether a tile is occupied invokes `set.union`, since I am working with two sets for tracking - one for rocks and the other for settled sand units.

```Python
class Board:
    def __init__(self, sand_origin: Point):
        self.rocks = set()
        self.settled_sand = set()
        # ...
    def add_rock(self, coords: Point) -> None:
        self.rocks.add(coords)
        # ...
    def occupied_tiles(self):
        return self.rocks.union(self.settled_sand)
    def is_tile_occupied(self, tile: Point):
        return tile in self.occupied_tiles() or tile.y == self.cave_floor_y
    # ...
```

#### attempt 2 - removing `set.union` operation for speedup

Cleaning up the `Board` class:

```Python
class Board:
    # ...
    def is_tile_occupied(self, tile: Point):
        return tile in self.rocks \
            or tile in self.settled_sand \
            or tile.y == self.cave_floor_y
    # ...
```

Rerunning the same profiled setup as before (with origin point 35 units above typical for the example), we get the following printout:

```
1196036 function calls in 0.671 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    64714    0.179    0.000    0.589    0.000 solution.py:66(fall_step)
   117482    0.113    0.000    0.266    0.000 solution.py:44(is_tile_occupied)
   236913    0.083    0.000    0.118    0.000 point.py:42(__hash__)
   117533    0.079    0.000    0.109    0.000 point.py:13(__add__)
   235074    0.063    0.000    0.063    0.000 point.py:3(__init__)
```

This is an overall, profiled speedup of ~13.7x!

With this result, I was confident to re-run the sim for Part Two.  It ran in less than 30s, a much more reasonable amount of time!