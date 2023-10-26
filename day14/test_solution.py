# std library
import unittest
# local
import solution
import string_visualizer

Point = solution.Point

class TestDay14(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    def test_file_parsing(self):
        board = solution.create_board(filepath=self.EXAMPLE, sand_origin=Point(500, 0))
        self.assertEqual(len(board.rocks), 20)
        self.assertEqual(len(board.settled_sand), 0)

    def test_string_visualization_initial_state(self):
        board = solution.create_board(filepath=self.EXAMPLE, sand_origin=Point(500, 0))
        board_str = string_visualizer.board_as_string(board, sandunit=None, viewbounds=(Point(494, 0), Point(503, 9)))
        example_output = \
"""......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
........#.
........#.
#########."""
        self.assertEqual(example_output, board_str)

if __name__ == '__main__':
    unittest.main()