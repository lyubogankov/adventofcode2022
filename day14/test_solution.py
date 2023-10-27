# std library
from functools import partial
import unittest
# local
import solution
import string_visualizer

Point = solution.Point
BoundingBox = solution.BoundingBox

class TestDay14(unittest.TestCase):
    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    def test_file_parsing(self):
        board = solution.create_board(filepath=self.EXAMPLE, sand_origin=Point(500, 0))
        self.assertEqual(len(board.rocks), 20)
        self.assertEqual(len(board.settled_sand), 0)

    def test_string_visualization_initial_state(self):
        board = solution.create_board(filepath=self.EXAMPLE, sand_origin=Point(500, 0))
        board_str = string_visualizer.board_as_string(board, sand_unit=None, viewbounds=BoundingBox(Point(494, 0), Point(503, 9)))
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
            frames = solution.run_simulation(
                inputfile=self.EXAMPLE,
                sand_origin=Point(x=500, y=0),
                create_board_frame_fn=partial(string_visualizer.board_as_string, viewbounds=BoundingBox(Point(494, 0), Point(503, 9))),
                sand_unit_limit=number_of_grains_fallen
            )
            with self.subTest(i=number_of_grains_fallen):
                self.assertEqual(expected_printout, frames[-1])

    def test_falling_path_printout(self):
        expected = """.......+...
.......~...
......~o...
.....~ooo..
....~#ooo##
...~o#ooo#.
..~###ooo#.
..~..oooo#.
.~o.ooooo#.
~#########.
~..........
~..........
~.........."""
        falling_path_output = string_visualizer.generate_falling_sand_block_path(
            inputfile=self.EXAMPLE,
            sand_origin=Point(x=500, y=0),
            viewbounds=BoundingBox(topleft=Point(x=493, y=0), bottomright=Point(x=503, y=12))
        )
        self.assertEqual(expected, falling_path_output)

if __name__ == '__main__':
    unittest.main()