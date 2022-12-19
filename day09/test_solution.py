# std library
import unittest
# local
import solution
from solution import Point_2D, Grid

class TestDay09(unittest.TestCase):

    examplefile = 'example.txt'
    exampletwofile = 'example_two.txt'

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

    @staticmethod
    def verify_atomic_move_rope_sim_n_knots(tester, num_knots, grid, exfile, per_move_outcomes, mode, start_point=Point_2D(x=0, y=0)):
        '''The move/outcome answers come directly from adventofcode problem description (oracle)
        
        mode = 'atomic' or 'nonatomic'
            atomic    = each move has repetitions = 1
            nonatomic = move can have repetitions > 1
        ''' 
        old_tester_maxdiff = tester.maxDiff
        tester.maxDiff = None

        atomic = mode == 'atomic'
        nonatomic = mode == 'nonatomic'

        knots = [Point_2D(x=start_point.x, y=start_point.y) for _ in range(num_knots)]

        _move_list = solution.read_input_file_into_move_list(exfile)    
        # generate move list and ensure we match number of outcomes
        if atomic:
            move_and_label_list = [] 
            for i, move in enumerate(_move_list):
                for j, atomic_move in enumerate(solution.Move.turn_repeated_move_into_atomic_move_list(move)):
                    move_and_label_list.append((f'(move {i}/{len(_move_list)}) {move.name} {j}/{move.repetitions}', atomic_move))
        elif nonatomic:
            move_and_label_list = [(f'(move {i}/{len(_move_list)}) {str(move)}', move) for i, move in enumerate(_move_list)]
        tester.assertEqual(len(move_and_label_list), len(per_move_outcomes))

        for (label, move), outcome_str in zip(move_and_label_list, per_move_outcomes):
            # if atomic -- repetitions = 1.  nonatomic - no such guarantee, but we're checking at the end.
            for _ in range(move.repetitions):
                knots = solution.update_all_knot_pos(knots, move, grid, start_point)
                current_grid_str = solution.generate_current_grid_state_string(knots, grid, start_point)
                # test after every move repetition for atomic mode (ex1)
                if atomic:
                    with tester.subTest(i=label):
                        tester.assertEqual(current_grid_str, outcome_str)
            # test after all move repetitions for nonatomic mode (ex2)
            if nonatomic:
                with tester.subTest(i=label):
                    tester.assertEqual(current_grid_str, outcome_str)

        tester.maxDiff = old_tester_maxdiff

    def test_atomic_move_rope_simulation_2knots(self):
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
        # initial condition
        grid = Grid.create_grid_with_dimensions(width=6, height=5)
        # run the sim!
        TestDay09.verify_atomic_move_rope_sim_n_knots(
            tester=self, grid=grid, exfile=self.examplefile, per_move_outcomes=atomic_move_outcomes, num_knots=2, mode='atomic')

    def test_move_rope_simulation_10knots(self):
        with self.subTest(i=self.examplefile):
            atomic_move_outcomes = [
# R 4
'''......
......
......
......
1H....''',

'''......
......
......
......
21H...''',

'''......
......
......
......
321H..''',

'''......
......
......
......
4321H.''',

# U 4
'''......
......
......
....H.
4321..''',

'''......
......
....H.
.4321.
5.....''',

'''......
....H.
....1.
.432..
5.....''',

'''....H.
....1.
..432.
.5....
6.....''',

# L 3
'''...H..
....1.
..432.
.5....
6.....''',

'''..H1..
...2..
..43..
.5....
6.....''',

'''.H1...
...2..
..43..
.5....
6.....''',

# D 1
'''..1...
.H.2..
..43..
.5....
6.....''',

# R 4
'''..1...
..H2..
..43..
.5....
6.....''',

'''..1...
...H..
..43..
.5....
6.....''',

'''......
...1H.
..43..
.5....
6.....''',

'''......
...21H
..43..
.5....
6.....''',

# D 1
'''......
...21.
..43.H
.5....
6.....''',

# L 5
'''......
...21.
..43H.
.5....
6.....''',

'''......
...21.
..4H..
.5....
6.....''',

'''......
...2..
..H1..
.5....
6.....''',

'''......
...2..
.H13..
.5....
6.....''',

'''......
......
H123..
.5....
6.....''',

# R 2
'''......
......
.H23..
.5....
6.....''',

'''......
......
.1H3..
.5....
6.....'''
            ]
            grid = Grid.create_grid_with_dimensions(width=6, height=5)
            # run the sim!
            TestDay09.verify_atomic_move_rope_sim_n_knots(
                tester=self, grid=grid, exfile=self.examplefile, per_move_outcomes=atomic_move_outcomes, num_knots=10, mode='atomic')
        with self.subTest(i=self.exampletwofile):
            move_outcomes = [
# R 5
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
...........54321H.........
..........................
..........................
..........................
..........................
..........................''',

# U 8
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
................H.........
................1.........
................2.........
................3.........
...............54.........
..............6...........
.............7............
............8.............
...........9..............
..........................
..........................
..........................
..........................
..........................''',

# L 8
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
........H1234.............
............5.............
............6.............
............7.............
............8.............
............9.............
..........................
..........................
...........s..............
..........................
..........................
..........................
..........................
..........................''',

# D 3
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
.........2345.............
........1...6.............
........H...7.............
............8.............
............9.............
..........................
..........................
...........s..............
..........................
..........................
..........................
..........................
..........................''',

# R 17
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
................987654321H
..........................
..........................
..........................
..........................
...........s..............
..........................
..........................
..........................
..........................
..........................''',

# D 10
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
...........s.........98765
.........................4
.........................3
.........................2
.........................1
.........................H''',

# L 25
'''..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
..........................
...........s..............
..........................
..........................
..........................
..........................
H123456789................''',

# U 20
'''H.........................
1.........................
2.........................
3.........................
4.........................
5.........................
6.........................
7.........................
8.........................
9.........................
..........................
..........................
..........................
..........................
..........................
...........s..............
..........................
..........................
..........................
..........................
..........................''',
            ]
            grid = Grid.create_grid_with_dimensions(width=26, height=21)
            # run the sim!
            TestDay09.verify_atomic_move_rope_sim_n_knots(
                tester=self, num_knots = 10, grid=grid, exfile=self.exampletwofile, per_move_outcomes=move_outcomes,
                start_point=Point_2D(x=11, y=5), mode='nonatomic'
            )

    def test_part_one(self):
        outcome_str = \
'''..##..
...##.
.####.
....#.
s###..'''
        move_list = solution.read_input_file_into_move_list(self.examplefile)
        t_move_set, t_move_str = solution.simulate_rope(move_list, num_knots=2)
        self.assertEqual(len(t_move_set), 13)
        self.assertEqual(t_move_str, outcome_str)

    def test_part_two(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=1) # default verbosity