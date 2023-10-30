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
        parsed_map = string_visualizer.visualize_sensor_beacon_map(inputfile='example.txt')
        self.assertEqual(expected, parsed_map)

    def test_exclusion_zone_calculation(self):
        expected = """"""
        exclusion_printout = string_visualizer.visualize_sensor_beacon_map(
            inputfile='example.txt',
            show_excl_sensor_coords=[CoordPair(8, 7)]
        )
        self.assertEqual(expected, exclusion_printout)

if __name__ == '__main__':
    unittest.main()