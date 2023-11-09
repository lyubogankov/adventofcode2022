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

class Sensor:
    def __init__(self, coords: CoordPair, nearest_beacon_coords: CoordPair):
        self.coords = coords
        self.nearest_beacon_coords = nearest_beacon_coords
        self.radius = abs(coords.x - nearest_beacon_coords.x) + abs(coords.y - nearest_beacon_coords.y)
        # previously stored y -> xrange mapping in a dict... but this involved looping over ALL points.
        def excluded_x_range(y):
            x_len = self.radius - abs(self.coords.y - y)
            return range(self.coords.x - x_len, self.coords.x + x_len + 1)
        self.excluded_x_range = excluded_x_range

    def is_within_exclusion_zone(self, point: CoordPair) -> bool:
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
    """Assuming all ranges have step=1"""
    # unify
    if r1.start in r2 or (r1.stop - r1.step) in r2 \
            or r2.start in r1 or (r2.stop - r2.step) in r1:
        return range(min(r1.start, r2.start), max(r1.stop, r2.stop))
    # no unification possible
    return None

def reduce_to_min_number_of_ranges(ranges):
    """This function takes a collection of N ranges and attempts to consolidate the ranges.
    
    A collection of up to N ranges will be returned (N meaning no unification was possible).
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
        row_exclusion_range = s.excluded_x_range(y)
        valid_sensor_excl_ranges.append(row_exclusion_range)
    # now, unify all of these ranges
    ranges = reduce_to_min_number_of_ranges(valid_sensor_excl_ranges)
    # exclude sensors and beacons in row
    num_sensors_in_row = sum(s.coords.y == y for s in sensors)
    beacon_coords = set(s.nearest_beacon_coords for s in sensors)  # more than one sensor can point to the same beacon!
    num_beacons_in_row = sum(bcoords.y == y for bcoords in beacon_coords)
    # finally, return the count!
    return sum(len(r) for r in ranges) - num_beacons_in_row - num_sensors_in_row

if __name__ == '__main__':
    sensors = parse_input_file_into_sensors_and_beacons(inputfile='input.txt')
    print('part one:', count_excluded_points_within_row(sensors, y=2000000))

    # import cProfile
    # cProfile.run("count_excluded_points_within_row(sensors=parse_input_file_into_sensors_and_beacons(inputfile='input_edited.txt'), y=10)", 'sim_stats')
    # import pstats
    # p = pstats.Stats('sim_stats')
    # p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()