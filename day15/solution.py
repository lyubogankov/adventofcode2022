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
        self.exclusion_zone = {}
        for y in range(self.coords.y - self.radius, self.coords.y + self.radius + 1):
            x_len = self.radius - abs(self.coords.y - y)
            self.exclusion_zone[y] = range(self.coords.x - x_len, self.coords.x + x_len + 1)

    def is_within_exclusion_zone(self, point: CoordPair) -> bool:
        if point.x > self.coords.x + self.radius or point.x < self.coords.x - self.radius:
            return False
        return point.x in self.exclusion_zone.get(point.y, [])
        
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

"""
r1 = range(start=0, stop=3, step=1) -> [0, 1, 2]
r2 = range(start=1, stop=4, step=1) -> [1, 2, 3]

case 1: partial overlap, r2 past r1 (or vice versa)
xxxx+
 xxxxx+

 xxxxx+
xxxx+

case 3: no intersection
x+
    x+

case 4: complete overlap (r1 subset_eq r2, or vice versa)
xxxxxxxx+
  xx+

  xx+
xxxxxxxx+
"""

def attempt_range_unification(r1, r2):
    """Assuming all ranges have step=1"""
    # unify
    if r1.start <= r2.stop <= r1.stop \
            or r2.start <= r1.stop <= r2.stop:
        return range(min(r1.start, r2.start), max(r1.end, r2.end)), None
    # no unification possible
    return r1, r2

# part one question
def count_excluded_points_within_row(sensors, y: int) -> int:
    sensor_coords = set(s.coords for s in sensors)
    # beacon_coords = set(s.nearest_beacon_coords for s in sensors)
    
    smallest_x, smallest_y, largest_x, largest_y = calculate_map_bounds(sensors, show_excl_sensor_coords=sensor_coords)
    # if target row is outside of all exclusion bounds, no point in counting anything
    if y > largest_y or y < smallest_y:
        print('ruh roh y out of bounds')
        return 0
    
    # now, iterate over the row and count number of points within any sensor's exclusion zone
    # count = 0
    # for x in range(smallest_x, largest_x + 1):
    #     current = CoordPair(x, y)
    #     for s in sensors:
    #         if s.is_within_exclusion_zone(current) and current not in beacon_coords and current not in sensor_coords:
    #             count += 1
    #             break
    # return count
    
    ranges = []
    for s in sensors:
        print(f'looking at sensor {s.coords}')
        # exclude sensors whose exclusion area doesn't include our current row of interest
        if not s.coords.y - s.radius <= y <= s.coords.y + s.radius:
            print('    skipping sensor')
            continue
        row_exclusion_range = s.exclusion_zone[y]
        print(f'    row exclusion range: {row_exclusion_range}')
        print( '    now looping over currently captured ranges...')

        current_iteration_ranges = []
        for r in ranges:
            print(f'        range: {r}')
            r1, r2 = attempt_range_unification(r, row_exclusion_range)
            print(f'        unification worked?  {r1}  vs  {r2}')
            current_iteration_ranges.append(r1)
            # unification succeeded!  otherwise continue
            if r2 is None:
                break
        else:
            current_iteration_ranges.append(row_exclusion_range)
        ranges = current_iteration_ranges
    return sum(len(r) for r in ranges)

if __name__ == '__main__':
    # sensors = parse_input_file_into_sensors_and_beacons(inputfile='input.txt')
    # print('part one:', count_excluded_points_within_row(sensors, y=2000000))

    import cProfile
    cProfile.run("count_excluded_points_within_row(sensors=parse_input_file_into_sensors_and_beacons(inputfile='input_edited.txt'), y=10)", 'sim_stats')
    import pstats
    p = pstats.Stats('sim_stats')
    p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()