# std library
import unittest
# local
import solution
from solution import Point_2D, Grid

class TestDay09(unittest.TestCase):

    examplefile = 'example.txt'

    def test_file_parsing(self):
        '''Testing whether the input file is correctly parsed into move objects.
        The move object's __str__ method outputs in same format as input lines for easy testing.
        '''
        move_list = solution.read_input_file_into_move_list(self.examplefile)
        with open(self.examplefile, 'r') as exfile:
            contents = exfile.read()

        inputlines = contents.split('\n')[:-1]
        self.assertEqual(len(move_list), len(inputlines))
        for move, line in zip(move_list, inputlines):
            with self.subTest(i=line):
                self.assertEqual(str(move), line)

    def test_atomic_move_rope_simulation(self):
        '''The move/outcome answers come directly from adventofcode problem description (oracle)'''
        move_list = solution.read_input_file_into_move_list(self.examplefile)
        atomic_move_list = []
        for move in move_list:
            for i, atomic_move in enumerate(solution.Move.turn_repeated_move_into_atomic_move_list(move)):
                atomic_move_list.append((f'{move.name} {i}/{move.repetitions}', atomic_move))
        atomic_move_outcomes = [
# R 4
'''......
......
......
......
TH....''',

'''......
......
......
......
sTH...''',

'''......
......
......
......
s.TH..''',

'''......
......
......
......
s..TH.''',

# U 4
'''......
......
......
....H.
s..T..''',

'''......
......
....H.
....T.
s.....''',

'''......
....H.
....T.
......
s.....''',

'''....H.
....T.
......
......
s.....''',

# L 3
'''...H..
....T.
......
......
s.....''',

'''..HT..
......
......
......
s.....''',

'''.HT...
......
......
......
s.....''',

# D 1
'''..T...
.H....
......
......
s.....''',

# R 4
'''..T...
..H...
......
......
s.....''',

'''..T...
...H..
......
......
s.....''',

'''......
...TH.
......
......
s.....''',

'''......
....TH
......
......
s.....''',

# D 1
'''......
....T.
.....H
......
s.....''',

# L 5
'''......
....T.
....H.
......
s.....''',

'''......
....T.
...H..
......
s.....''',

'''......
......
..HT..
......
s.....''',

'''......
......
.HT...
......
s.....''',

'''......
......
HT....
......
s.....''',

# R 2
'''......
......
.H....
......
s.....''',

'''......
......
.TH...
......
s.....'''
        ]

        self.assertEqual(len(atomic_move_list), len(atomic_move_outcomes))

        # initial condition
        h = Point_2D(x=0, y=0)
        t = Point_2D(x=0, y=0)
        grid = Grid(
            topl=Point_2D(x=0, y=4),
            botr=Point_2D(x=5, y=0)
        )
        for (label, move), outcome_str in zip(atomic_move_list, atomic_move_outcomes):
            h, t = solution.update_h_and_t_pos(h_initial=h, t_initial=t, h_atomic_move=move)
            with self.subTest(i=label):
                self.assertEqual(
                    solution.generate_current_grid_state_string(h, t, grid, start_point=Point_2D(x=0, y=0)),
                    outcome_str
                )

if __name__ == '__main__':
    unittest.main()