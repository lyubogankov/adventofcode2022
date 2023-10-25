# std library
import unittest
# local
import solution

Point = solution.Point

class TestDay14(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    def test_file_parsing(self):
        board = solution.create_board(filepath='example.txt', sand_origin=Point(500, 0))
        self.assertEqual(len(board.rocks), 20)
        self.assertEqual(len(board.settled_sand), 0)