# std library
import unittest
# local
import solution
import string_visualizer

class TestDay15(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    def test_inputfile_parsing(self):
        expected = """"""
        parsed_map = string_visualizer.visualize_sensor_beacon_map(inputfile='example.txt')
        self.assertEqual(expected, parsed_map)

    

if __name__ == '__main__':
    unittest.main()