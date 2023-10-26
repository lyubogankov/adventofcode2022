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
        board_str = string_visualizer.board_as_string(board, sand_unit=None, viewbounds=(Point(494, 0), Point(503, 9)))
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

    def test_simulation(self):
        board = solution.create_board(filepath=self.EXAMPLE, sand_origin=Point(500, 0))
        expected_printouts = [
"""......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
........#.
......o.#.
#########.""",

"""......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
........#.
.....oo.#.
#########.""",

"""......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
......o.#.
....oooo#.
#########.""",

"""......+...
..........
......o...
.....ooo..
....#ooo##
....#ooo#.
..###ooo#.
....oooo#.
...ooooo#.
#########.""",

"""......+...
..........
......o...
.....ooo..
....#ooo##
...o#ooo#.
..###ooo#.
....oooo#.
.o.ooooo#.
#########.""",
        ]
        for expected_printout, number_of_grains_fallen in zip(expected_printouts, [1, 2, 5, 22, 24]):
            # simulate board state up to current point, then compare expected printout vs generated!

if __name__ == '__main__':
    unittest.main()