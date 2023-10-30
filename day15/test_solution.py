# std library
import unittest
# local
import solution
from solution import CoordPair
import string_visualizer

class TestDay15(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    def test_inputfile_parsing(self):
        expected = """"""
        parsed_map = string_visualizer.visualize_sensor_beacon_map(
            sensors=solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        )
        self.assertEqual(expected, parsed_map)

    def test_exclusion_zone_calculation(self):
        expected = """"""
        exclusion_printout = string_visualizer.visualize_sensor_beacon_map(
            sensors=solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE),
            show_excl_sensor_coords=[CoordPair(8, 7)]
        )
        self.assertEqual(expected, exclusion_printout)

    def test_part_one_row_exclusion_count(self):
        sensors = solution.parse_input_file_into_sensors_and_beacons(inputfile=self.EXAMPLE)
        count = solution.count_excluded_points_within_row(sensors, y=10)
        self.assertEqual(count, 26)

if __name__ == '__main__':
    unittest.main()