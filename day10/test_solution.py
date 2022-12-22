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

if __name__ == '__main__':
    unittest.main()