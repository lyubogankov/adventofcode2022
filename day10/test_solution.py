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

if __name__ == '__main__':
    unittest.main()