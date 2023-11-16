# std library
import itertools
import unittest
# local
import solution
from solution import CoordPair, BoundingBox
import string_visualizer

class TestDay15(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    EXAMPLE_PT2_BOUNDARY = BoundingBox(topl=CoordPair(0, 0), botr=CoordPair(20, 20))

    def test_inputfile_parsing(self):
        expected = """....S.......................
......................S.....
...............S............
................SB..........
............................
............................
............................
..........S.......S.........
............................
............................
....B.......................
..S.........................
............................
............................
..............S.......S.....
B...........................
...........SB...............
................S..........B
....S.......................
............................
............S......S........
............................
.......................B...."""
        parsed_map = string_visualizer.visualize_sensor_beacon_map(
            sensors=solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        )
        self.assertEqual(expected, parsed_map)

    def test_exclusion_zone_calculation(self):
        expected = """..........#.................
.........###................
....S...#####...............
.......#######........S.....
......#########S............
.....###########SB..........
....#############...........
...###############..........
..#################.........
.#########S#######S#........
..#################.........
...###############..........
....B############...........
..S..###########............
......#########.............
.......#######..............
........#####.S.......S.....
B........###................
..........#SB...............
................S..........B
....S.......................
............................
............S......S........
............................
.......................B...."""
        exclusion_printout = string_visualizer.visualize_sensor_beacon_map(
            sensors=solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE),
            show_excl_sensor_coords=[CoordPair(8, 7)]
        )
        self.assertEqual(expected, exclusion_printout)

    def test_range_unification(self):
        # case 1: partial overlap
        a = range(6)
        b = range(5, 10)
        self.assertEqual(range(10), solution.attempt_range_unification(r1=a, r2=b))
        self.assertEqual(range(10), solution.attempt_range_unification(r1=b, r2=a))
        # case 2: complete overlap
        a = range(10)
        b = range(5, 7)
        self.assertEqual(range(10), solution.attempt_range_unification(r1=a, r2=b))
        self.assertEqual(range(10), solution.attempt_range_unification(r1=b, r2=a))
        # case 3: no overlap
        self.assertEqual(None, solution.attempt_range_unification(r1=range(10), r2=range(15, 20)))

    def test_range_collection_reduction(self):
        r1 = range( 0, 10)   #..........
        r2 = range( 5, 15)   #     ..........
        r3 = range(20, 25)   #                    .....
        r4 = range(17, 23)   #                 ......
        r5 = range(13, 19)   #             ......
        # case 1: some of the ranges can be collapsed, but not all can
        with self.subTest(i="partial_reduction"):
            for permutation in itertools.permutations([r1, r2, r3]):
                self.assertEqual(
                    {range(0, 15), r3},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )
            for permutation in itertools.permutations([r1, r2, r3, r4]):
                self.assertEqual(
                    {range(0, 15), range(17, 25)},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )
            for permutation in itertools.permutations([r1, r3, r4, r5]):
                self.assertEqual(
                    {r1, range(13, 25)},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )
        # case 2: none of the ranges can be collapsed
        with self.subTest(i="no_reduction"):
            for permutation in itertools.permutations([r1, r3, r5]):
                self.assertEqual(
                    {r1, r3, r5},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )
        # case 3: all of the ranges can be collapsed
        with self.subTest(i="complete_reduction"):
            for permutation in itertools.permutations([r1, r2, r3, r4, r5]):
                self.assertEqual(
                    {range(0, 25)},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )
        # corner case -- ranges overlap exactly - start/stop
        ra = range(-23, -8)
        rb = range(-8, 27)
        with self.subTest(i="minimal_overlap"):
            for permutation in itertools.permutations([ra, rb]):
                self.assertEqual(
                    {range(-23, 27)},
                    set(solution.reduce_to_min_number_of_ranges(permutation))
                )

    def test_part_one_row_exclusion_count(self):
        sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        count = solution.count_excluded_points_within_row(sensors, y=10)
        self.assertEqual(count, 26)

    def test_coordinate_transforms(self):
        for x in range(-10, 11):
            for y in range(-10, 11):
                with self.subTest(i=f'({x}, {y}) d_to_s(s_to_d())'):
                    original = CoordPair(x, y)
                    transformed = solution.diamond_to_square_coords(
                        solution.square_to_diamond_coords(
                            original
                        )
                    )
                    self.assertEqual(original, transformed)
                with self.subTest(i=f'({x}, {y}) s_to_d(d_to_s())'):
                    original = CoordPair(x, y)
                    transformed = solution.square_to_diamond_coords(
                        solution.diamond_to_square_coords(
                            original
                        )
                    )
                    self.assertEqual(original, transformed)

    def test_sole_point_location(self):
        sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        self.assertEqual(
            CoordPair(x=14, y=11),
            solution.square_to_diamond_coords(
                solution.find_single_point_not_within_sensor_exclusion_range_squarecoords(
                    sensors, self.EXAMPLE_PT2_BOUNDARY
                )
            )
        )

    def test_part_two_tuning_freq(self):
        sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        self.assertEqual(56_000_011, solution.part_two(sensors, self.EXAMPLE_PT2_BOUNDARY))

if __name__ == '__main__':
    unittest.main()