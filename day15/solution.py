"""
We're working with manhattan distances.  Seems like I'll need to identify where the beacon CANNOT be, per-row.

Each sensor identifies the precise location of the one closest beacon to it, as determined by manhattan distance.

Instead of enumerating all integer coordinates within the exclusion-range for each sensor, I should instead
    just do per-row `range`s for each sensor.  Then, if I need to query a specific row,
    I can enumerate and find the union of the `range`s to answer the question.

Each sensor can first calculate the manhattan distance to the closest beacon.
    Then, it can calculate the "perimiter" of exclusion: picture a cross / dimond shape.
    The straight lines are like the axes - we know that at the tips, there is just one point 
    and that in the middle the entire row-portion is filled. (minimal example below)

         #
        ###
         #

I also want to generate an image with all of the exclusion zones - maybe they make a cool shape!
Give them different / random colors and each with some opacity!
"""
import copy
import math
import re
from collections import namedtuple

# coord system:
#      -y |
#         |
# -x -----+----- +x
#         |
#      +y |
#
CoordPair = namedtuple('CoordPair', field_names=['x', 'y'])

def diamond_to_square_coords(coordpair):
    return CoordPair(
        x = coordpair.x - coordpair.y,
        y = coordpair.x + coordpair.y
    )
def diamond_to_square(center: CoordPair, radius: int):
    """Returns representation of square: (topl point, botr point)"""
    d_top   = CoordPair(center.x, center.y - radius)  # -y
    d_bot   = CoordPair(center.x, center.y + radius)  # +y
    # d_left  = CoordPair(center.x - radius, center.y)  # -x
    # d_right = CoordPair(center.x + radius, center.y)  # +x
    p1 = diamond_to_square_coords(d_top)
    p2 = diamond_to_square_coords(d_bot)
    smallest_x, largest_x = int(min(p1.x, p2.x)), int(max(p1.x, p2.x))
    smallest_y, largest_y = int(min(p1.y, p2.y)), int(max(p1.y, p2.y))
    topl = CoordPair(smallest_x, smallest_y)
    botr = CoordPair(largest_x, largest_y)
    return topl, botr

def square_to_diamond_coords(coordpair):
    """Need to divide by two bc I left out factor of sqrt(2)/2 from d->s,
    so instead we're dividing by power(sqrt(2)/2, 2) = 1/2 here!"""
    return CoordPair(
        x = (coordpair.y + coordpair.x)/2,
        y = (coordpair.y - coordpair.x)/2
    )
def square_to_diamond(topl: CoordPair, botr: CoordPair):
    """Returns representation of diamond: (center point, radius)"""
    d_top = square_to_diamond_coords(topl)
    d_bot = square_to_diamond_coords(botr)
    radius = (d_bot.y - d_top.y)/2
    return CoordPair(d_top.x, d_top.y + radius), radius

class BoundingBox:
    def __init__(self, topl: CoordPair, botr: CoordPair):
        # square coords boundingbox /  diamond-excl range coords
        self.topl = topl
        self.botr = botr
        # diamond coords boundingbox / square-excl range coords
        s_topl = diamond_to_square_coords(topl)
        s_botr = diamond_to_square_coords(botr)
        self.center = diamond_to_square_coords(
            CoordPair(
                x=topl.x + (botr.x - topl.x)//2,
                y=topl.y + (botr.y - topl.y)//2
            )
        )
        self.radius = abs(s_topl.y - s_botr.y) // 2
        def xrange_at_row(y):
            x_len = self.radius - abs(self.center.y - y)
            return range(self.center.x - x_len, self.center.x + x_len + 1)
        self.xrange_at_row = xrange_at_row
        self.yrange = range(self.center.y - self.radius, self.center.y + self.radius + 1)

    def edge_contains(self, point: CoordPair, square_coords=True):
        # diamond excl ranges / square boundingbox - check perimeter based on topl, botr
        if not square_coords:
            return ((point.x == self.topl.x or point.x == self.botr.x) and self.topl.y <= point.y <= self.botr.y) \
                or ((point.y == self.topl.y or point.y == self.botr.y) and self.topl.x <= point.x <= self.botr.x) 
        # square excl ranges / diamond boundingbox - check perimeter based on manhattan dist
        return abs(self.center.x - point.x) + abs(self.center.y - point.y) == self.radius

class Sensor:
    def __init__(self, coords: CoordPair, nearest_beacon_coords: CoordPair):
        # diamond coord system
        self.coords = coords
        self.nearest_beacon_coords = nearest_beacon_coords
        self.radius = abs(coords.x - nearest_beacon_coords.x) + abs(coords.y - nearest_beacon_coords.y)
        # previously stored y -> xrange mapping in a dict... but this involved looping over ALL points.
        def excluded_x_range(y):
            x_len = self.radius - abs(self.coords.y - y)
            return range(self.coords.x - x_len, self.coords.x + x_len + 1)
        def excluded_y_range(x):
            y_len = self.radius - abs(self.coords.x - x)
            return range(self.coords.y - y_len, self.coords.y + y_len + 1)
        self.excluded_x_range = excluded_x_range
        self.excluded_y_range = excluded_y_range
        # square coord system
        self.s_topl, self.s_botr = diamond_to_square(self.coords, self.radius)
        self.s_coords = diamond_to_square_coords(self.coords)
        self.s_nearest_beacon_coords = diamond_to_square_coords(self.nearest_beacon_coords)
        self.s_xrange = range(self.s_topl.x, self.s_botr.x + 1)
        self.s_yrange = range(self.s_topl.y, self.s_botr.y + 1)

    def is_within_exclusion_zone(self, point: CoordPair, square_coords=False) -> bool:
        if square_coords:
            return self.s_topl.x <= point.x <= self.s_botr.x and self.s_topl.y <= point.y <= self.s_botr.y
        # otherwise, diamond coords (default)
        if point.x > self.coords.x + self.radius or point.x < self.coords.x - self.radius:
            return False
        return point.x in self.excluded_x_range(point.y)

    def __repr__(self):
        return f'Sensor(coords={self.coords}, nearest_beacon_coords={self.nearest_beacon_coords})'
        
def parse_input_file_into_sensors_and_beacons(inputfile): # -> List[Sensor]:
    sensors = []
    with open(inputfile, 'r') as f:
        lines = f.readlines()
    pattern = re.compile(r"Sensor at x=([-\d]+), y=([-\d]+): closest beacon is at x=([-\d]+), y=([-\d]+)")
    for line in lines:
        sx, sy, bx, by = map(int, pattern.search(line).groups())
        sensors.append(Sensor(coords=CoordPair(sx, sy), nearest_beacon_coords=CoordPair(bx, by)))
    return sensors

def calculate_map_bounds(sensors, show_excl_sensor_coords=[]):
    smallest_x = smallest_y = math.inf
    largest_x = largest_y = -math.inf
    for s in sensors:
        smallest_x = min(smallest_x, s.coords.x, s.nearest_beacon_coords.x, s.coords.x - s.radius if s.coords in show_excl_sensor_coords else  math.inf)
        smallest_y = min(smallest_y, s.coords.y, s.nearest_beacon_coords.y, s.coords.y - s.radius if s.coords in show_excl_sensor_coords else  math.inf)
        largest_x  = max(largest_x,  s.coords.x, s.nearest_beacon_coords.x, s.coords.x + s.radius if s.coords in show_excl_sensor_coords else -math.inf)
        largest_y  = max(largest_y,  s.coords.y, s.nearest_beacon_coords.y, s.coords.y + s.radius if s.coords in show_excl_sensor_coords else -math.inf)
    return smallest_x, smallest_y, largest_x, largest_y

def attempt_range_unification(r1, r2):
    """Assuming all ranges have step=1.  1D function, therefore independent of 2D coord system."""
    # unify
    if r1.start in r2 or (r1.stop - r1.step) in r2 \
            or r2.start in r1 or (r2.stop - r2.step) in r1 \
            or r1.stop == r2.start or r1.start == r2.stop:
        return range(min(r1.start, r2.start), max(r1.stop, r2.stop))
    # no unification possible
    return None

def reduce_to_min_number_of_ranges(ranges):
    """This function takes a collection of N ranges and attempts to consolidate the ranges.
    
    A collection of up to N ranges will be returned (N meaning no unification was possible).

    1D function, therefore independent of 2D coord system.
    """

    # try all unique combinations of range pairs from the input collection
    # and note which can be combined.
    unification_mapping = {}
    merged_indices = set()
    for a, r1 in enumerate(ranges):
        bstart = a + 1
        for _b, r2 in enumerate(ranges[bstart:]):
            b = _b + bstart
            # write down whether the combo of r1, r2 was unified (either unified range or None)
            unification_mapping[frozenset((a, b))] = attempt_range_unification(r1, r2)
            # if so, we know that both of these indices were unified
            if unification_mapping[frozenset((a, b))]:
                merged_indices.add(a)
                merged_indices.add(b)

    # if we can't merge anything, return the ranges as-is
    if not merged_indices:
        return ranges

    # now we know which indices are unmergable
    unmerged_indices = [i for i in range(len(ranges)) if i not in merged_indices]
    output_ranges = [ranges[i] for i in unmerged_indices]  # initialize with ranges that we know are unmerged

    # the rest are merged.  our task is now to try to unify them based on our mapping table.
    next_idx_stack = []
    while merged_indices:
        # obtain next idx to consider
        if not next_idx_stack:
            current_idx = merged_indices.pop()
            # append the current idx range to the output list -- it's merged with at least one other range
            output_ranges.append(ranges[current_idx])
        else:
            current_idx = next_idx_stack.pop()
        # look at all remaining combos between current / merged to see which are merged
        for remaining_idx in merged_indices:
            # if the current index and one of the remaining indices can be merged:
            # - log the merged range to the output list
            # - note the index to be explored!
            if unified_range := unification_mapping[frozenset((current_idx, remaining_idx))]:
                output_ranges[-1] = attempt_range_unification(output_ranges[-1], unified_range)
                next_idx_stack.append(remaining_idx)
        # make sure that all indices within the next_idx_stack are no longer present in merged_indices set
        for idx in next_idx_stack:
            if idx in merged_indices:
                merged_indices.remove(idx)
    return output_ranges

# part one question
def count_excluded_points_within_row(sensors, y: int) -> int:
    sensor_coords = set(s.coords for s in sensors)
    smallest_x, smallest_y, largest_x, largest_y = calculate_map_bounds(sensors, show_excl_sensor_coords=sensor_coords)
    # if target row is outside of all exclusion bounds, no point in counting anything
    if y > largest_y or y < smallest_y:
        return 0
    # obtain list of ranges from sensors whose excl. range contains row (y) of interest
    valid_sensor_excl_ranges = []
    for s in sensors:        
        # exclude sensors whose exclusion area doesn't include our current row of interest
        if not s.coords.y - s.radius <= y <= s.coords.y + s.radius:
            continue
        # since this sensor's exclusion zone contains the desired row, look up the range of excluded x-values
        valid_sensor_excl_ranges.append(s.excluded_x_range(y))
    # now, unify all of these ranges
    ranges = reduce_to_min_number_of_ranges(valid_sensor_excl_ranges)
    # exclude sensors and beacons in row
    num_sensors_in_row = sum(s.coords.y == y for s in sensors)
    beacon_coords = set(s.nearest_beacon_coords for s in sensors)  # more than one sensor can point to the same beacon!
    num_beacons_in_row = sum(bcoords.y == y for bcoords in beacon_coords)
    # finally, return the count!
    return sum(len(r) for r in ranges) - num_beacons_in_row - num_sensors_in_row

# part two
def find_single_excluded_point_within_row(sensors, boundary: BoundingBox, y_row: int, printout=False):
    """Helper function.  Either returns the excluded point, or None."""
    boundary_yrow_xrange = boundary.xrange_at_row(y_row)
    row_xranges = []
    if printout:
        print('boundary row y:', y_row)
        print('boundary row xrange:', boundary_yrow_xrange)
    for s in sensors:
        if printout:
            print(f'    sensor: {s.s_coords},    beacon: {s.s_nearest_beacon_coords},    xrange: {s.s_xrange},    yrange: {s.s_yrange}')
        # # skip sensors whose excl range doesn't overlap with current row's range
        # if s.s_topl.x not in boundary_yrow_xrange and s.s_botr.x not in boundary_yrow_xrange:
        #     if printout:
        #         print('        skipped - not in boundary_yrow_xrange')
        #     continue
        # special cases - ranges of 1 to account for sensors / beacons
        if s.s_coords.y == y_row:
            x = s.s_coords.x
            row_xranges.append(range(x, x + 1))
            if printout:
                print('        adding sensor coordinate to row_xranges')
        if s.s_nearest_beacon_coords.y == y_row:
            x = s.s_nearest_beacon_coords.x
            row_xranges.append(range(x, x + 1))
            if printout:
                print('        adding beacon coordinate to row_xranges')
        # typical case: the y-range intersects with the boundary centerline
        if y_row in s.s_yrange:
            row_xranges.append(s.s_xrange)
            if printout:
                print("        adding sensor xrange since the sensor's exclusion yrange includes boundary center y")
    
    unified_xranges = reduce_to_min_number_of_ranges(row_xranges)
    for unified_xrange in unified_xranges:
        # the current unified range contains the entire boundary y-row of interest -- doesn't contain sole point
        if boundary_yrow_xrange.start in unified_xrange \
                and boundary_yrow_xrange.stop - 1 in unified_xrange:
            break
        # neither start nor stop are contained within, so don't care
        elif boundary_yrow_xrange.start not in unified_xrange \
                and boundary_yrow_xrange.stop - 1 not in unified_xrange:
            continue
        # otherwise -- we have a partial match!  only start OR stop is present.
        if boundary_yrow_xrange.start in unified_xrange:
            return CoordPair(unified_xrange.stop, y_row)
        else:
            return CoordPair(unified_xrange.start - 1, y_row)

def find_single_point_not_within_sensor_exclusion_range_squarecoords(sensors, boundary: BoundingBox, printout=False) -> CoordPair:
    # check the middle row
    if result := find_single_excluded_point_within_row(sensors, boundary, y_row=boundary.center.y, printout=printout):
        return result

    # look "up" from middle (bigger y -> smaller y) -- care about rows where sensor ranges end
    y_rows_of_interest_looking_up = sorted(set( \
        [s.s_yrange.start - 1 for s in sensors if boundary.yrange.start <= s.s_yrange.start - 1 <= boundary.center.y]), reverse=True)
    for y in y_rows_of_interest_looking_up:
        if result := find_single_excluded_point_within_row(sensors, boundary, y, printout):
            return result
    
    # look "down" from middle (smaller y -> bigger y) -- care about rows where sensor ranges end
    y_rows_of_interest_looking_down =  sorted(set( \
        [s.s_yrange.stop for s in sensors if boundary.center.y <= s.s_yrange.stop <= boundary.yrange.stop]))
    for y in y_rows_of_interest_looking_down:
        if result := find_single_excluded_point_within_row(sensors, boundary, y, printout):
            return result

def calculate_tuning_freq(point: CoordPair) -> int:
    return int(point.x * 4_000_000 + point.y)

def part_two(sensors, boundary: BoundingBox) -> int:
    sole_point = square_to_diamond_coords(
        find_single_point_not_within_sensor_exclusion_range_squarecoords(sensors, boundary)
    )
    if sole_point:''
        return calculate_tuning_freq(sole_point)
    else:
        raise Exception("Didn't find any points...")

"""
Most naiive approach: O(x*y*s) -> big for puzzle input. 4_000_000^2 * 29
- loop over all x, y points (O n^2)
- for each x, y point, loop over all sensors:
    if the x, y point is in none of the sensors' excl ranges, it is the point of interest.

```python
def p2(sensors, xrange, yrange)
    for x in xrange:
        for y in yrange:
            if any((x, y) == s.coords or (x, y) == s.nearest_beacon_coords for s in sensors):
                continue
            if all(x not in s.excluded_x_range(y) for s in sensors):
                return (x, y)
```

Sliiiightly better approach, based off part 1 work -> O(min(x, y) * s^2)
- loop over y, so O(y); for each y
    - consider all sensors, so O(s)
    - reduce to minimum number of ranges, which is O(s^2)?

```python
def p2(sensors, xrange, yrange):
    for y in yrange:
        unified_excl_ranges = reduce_to_min_number_of_ranges([s.excluded_x_range(y) for s in sensors])
        if len(unified_excl_ranges) == 1:
            unified_excl_ranges.sort(key=lambda r: r.start)
            x = unified_excl_ranges[0].stop
            return (x, y)
```

Part 2 brainstorming.

According to profiling, p1 completed w 1767 function calls, spread out primarily over builtins.
According to `time` (linux utility), program took:
    real	0m0.034s
    user	0m0.030s
    sys	    0m0.004s

So, if I use the "naiive" approach and minimally change my code from part 1 to iterate over every
single row from 0 -> 4.000.000, it would take 0.034s * 4.000.000 = 37 hours to complete.

What made part one fast was removing all iteration - calculating x-exclusion-range from y coord only when
needed (with a function), and calculating intersections between ranges instead of iterating over x coords.

What information do I have?
- per-sensor coords + nearest beacon
+ this allows me to calculate each sensor's exclusion radius (manhattan coords)
+ this allows me to calculate each sensor's exclusion zone (for all possible x, y coords)

* also, the puzzle is set up so that there is ONE x, y pair that is not within an exclusion zone.

What I'd like is a way to eliminate coords to search based on each sensor's exclusion boundary.

Before I do that, I want to make a visualization of the space.
Not sure if that'll help or not as I need to solve the problem generally...


2 thoughts:
- If I can come up with a very fast way to determine whether a row/col is "full" (start, stop) are fully contained within the exclusion range, then looping might not be a bad solution.
- However, that's v similar to question for P1 and my solution isn't super fast.
    So, option 2 is to avoid iterating (either totally, or at least over the full range.)
"""


if __name__ == '__main__':
    # sensors = parse_input_file_into_sensors_and_beacons(inputfile='example.txt')
    # print('part one:', count_excluded_points_within_row(sensors, y=10))
    # print('part two:', part_two(sensors, boundary=BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(20, 20))))

    sensors = parse_input_file_into_sensors_and_beacons(inputfile='input.txt')
    print('part one:', count_excluded_points_within_row(sensors, y=2_000_000))
    print('part two:', part_two(sensors, boundary=BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(4_000_000, 4_000_000))))

    # result = find_single_point_not_within_sensor_exclusion_range_squarecoords(
    #     sensors, 
    #     boundary=BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(20, 20)),
    #     printout=True
    # )
    # print('-'*100)
    # print('square coords:', result)
    # print('original, diamond coords:', square_to_diamond_coords(result))

    # import cProfile
    # cProfile.run("count_excluded_points_within_row(sensors=parse_input_file_into_sensors_and_beacons(inputfile='input.txt'), y=2000000)", 'sim_stats')
    # import pstats
    # p = pstats.Stats('sim_stats')
    # p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()