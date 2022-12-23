# std library
import unittest
# local
import solution
from solution import Instruction

class TestDay10(unittest.TestCase):

    EXAMPLEONE = 'example_one.txt'
    EXAMPLETWO = 'example_two.txt'

    def test_file_parsing(self):
        '''Testing whether we can correctly parse input file into Instruction objects.
        Instruction object's __str__ method outputs same format as input file.
        '''
        for examplefile in [self.EXAMPLEONE, self.EXAMPLETWO]:
            with self.subTest(i=examplefile):
                instr_list = solution.parse_instruction_list_from_file(examplefile)
                with open(examplefile, 'r') as _examplefile:
                    contents = _examplefile.read()
                
                lines = contents.split('\n')[:-1]
                self.assertEqual(len(lines), len(instr_list))  # each line got turned into an Instruction

                for instr, line in zip(instr_list, lines):
                    self.assertEqual(str(instr), line)

    # part one
    def test_partone_register_snapshots(self):
        '''Day10 part one: simulating instructions on a CPU.
        At specific cycle counts, need to sample the CPU's X register value.  Testing that here!'''
        instr_list = solution.parse_instruction_list_from_file(self.EXAMPLETWO)
        sampled_register_values = [21, 19, 18, 21, 16, 18]
        for sim_output, answer in zip(solution.run_instructions_on_cpu_partone(instr_list), sampled_register_values):
            with self.subTest(i=f'cycle {sim_output.cycle}'):
                self.assertEqual(sim_output.val, answer)

    def test_partone_signal_strength_sum(self):
        instr_list = solution.parse_instruction_list_from_file(self.EXAMPLETWO)
        self.assertEqual(solution.calculate_signal_strength_sum(instr_list), 13140)

    # part two
    def test_sprite_pos_str_generation(self):
        outcomes = [
            # from adventofcode problem description
            ( 1, '###.....................................'),
            (16, '...............###......................'),
            ( 5, '....###.................................'),
            (11, '..........###...........................'),
            ( 8, '.......###..............................'),
            (13, '............###.........................'),
            (12, '...........###..........................'),
            ( 4, '...###..................................'),
            (17, '................###.....................'),
            (21, '....................###.................'),
            (20, '...................###..................'),
            # my own test cases (focusing on edge cases)
            ( 0, '##......................................'),
            (-1, '#.......................................'),
            (-2, '........................................'),
            (38, '.....................................###'),
            (39, '......................................##'),
            (40, '.......................................#'),
            (41, '........................................'),
        ]

        for x_pos, sprite_str in outcomes:
            self.assertEqual(sprite_str, solution.generate_sprite_pos_str(x_pos, linewidth=40))

    def test_crt_cycle_by_cycle_explanation(self):
        answer = '''Sprite position: ###.....................................

Start cycle   1: begin executing addx 15
During cycle  1: CRT draws pixel in position 0
Current CRT row: #

During cycle  2: CRT draws pixel in position 1
Current CRT row: ##
End of cycle  2: finish executing addx 15 (Register X is now 16)
Sprite position: ...............###......................

Start cycle   3: begin executing addx -11
During cycle  3: CRT draws pixel in position 2
Current CRT row: ##.

During cycle  4: CRT draws pixel in position 3
Current CRT row: ##..
End of cycle  4: finish executing addx -11 (Register X is now 5)
Sprite position: ....###.................................

Start cycle   5: begin executing addx 6
During cycle  5: CRT draws pixel in position 4
Current CRT row: ##..#

During cycle  6: CRT draws pixel in position 5
Current CRT row: ##..##
End of cycle  6: finish executing addx 6 (Register X is now 11)
Sprite position: ..........###...........................

Start cycle   7: begin executing addx -3
During cycle  7: CRT draws pixel in position 6
Current CRT row: ##..##.

During cycle  8: CRT draws pixel in position 7
Current CRT row: ##..##..
End of cycle  8: finish executing addx -3 (Register X is now 8)
Sprite position: .......###..............................

Start cycle   9: begin executing addx 5
During cycle  9: CRT draws pixel in position 8
Current CRT row: ##..##..#

During cycle 10: CRT draws pixel in position 9
Current CRT row: ##..##..##
End of cycle 10: finish executing addx 5 (Register X is now 13)
Sprite position: ............###.........................

Start cycle  11: begin executing addx -1
During cycle 11: CRT draws pixel in position 10
Current CRT row: ##..##..##.

During cycle 12: CRT draws pixel in position 11
Current CRT row: ##..##..##..
End of cycle 12: finish executing addx -1 (Register X is now 12)
Sprite position: ...........###..........................

Start cycle  13: begin executing addx -8
During cycle 13: CRT draws pixel in position 12
Current CRT row: ##..##..##..#

During cycle 14: CRT draws pixel in position 13
Current CRT row: ##..##..##..##
End of cycle 14: finish executing addx -8 (Register X is now 4)
Sprite position: ...###..................................

Start cycle  15: begin executing addx 13
During cycle 15: CRT draws pixel in position 14
Current CRT row: ##..##..##..##.

During cycle 16: CRT draws pixel in position 15
Current CRT row: ##..##..##..##..
End of cycle 16: finish executing addx 13 (Register X is now 17)
Sprite position: ................###.....................

Start cycle  17: begin executing addx 4
During cycle 17: CRT draws pixel in position 16
Current CRT row: ##..##..##..##..#

During cycle 18: CRT draws pixel in position 17
Current CRT row: ##..##..##..##..##
End of cycle 18: finish executing addx 4 (Register X is now 21)
Sprite position: ....................###.................

Start cycle  19: begin executing noop
During cycle 19: CRT draws pixel in position 18
Current CRT row: ##..##..##..##..##.
End of cycle 19: finish executing noop

Start cycle  20: begin executing addx -1
During cycle 20: CRT draws pixel in position 19
Current CRT row: ##..##..##..##..##..

During cycle 21: CRT draws pixel in position 20
Current CRT row: ##..##..##..##..##..#
End of cycle 21: finish executing addx -1 (Register X is now 20)
Sprite position: ...................###..................
'''
        instr_list = solution.parse_instruction_list_from_file(self.EXAMPLETWO)
        _, test_str = solution.generate_crt_printstr_parttwo(instr_list, cycle_num_end=21, gen_test_str=True)
        
        old_maxdiff = self.maxDiff
        self.maxDiff = None

        self.assertEqual(answer, test_str)

        self.maxDiff = old_maxdiff

    def test_crt_printout(self):
        answer = '''##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######.....'''
        instr_list = solution.parse_instruction_list_from_file(self.EXAMPLETWO)
        crt_str, _ = solution.generate_crt_printstr_parttwo(instr_list)
        
        old_maxdiff = self.maxDiff
        self.maxDiff = None
        self.assertEqual(answer, crt_str)
        self.maxDiff = old_maxdiff

if __name__ == '__main__':
    unittest.main()