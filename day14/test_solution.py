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
                create_board_frame_fn=string_visualizer.create_board_frame_fn,
                sand_unit_limit=number_of_grains_fallen
            )
            with self.subTest(i=number_of_grains_fallen):
                self.assertEqual(expected_printout, frames[-1])

if __name__ == '__main__':
    unittest.main()