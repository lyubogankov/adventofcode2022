# std library
import unittest
# local
import solution

class TestDay11(unittest.TestCase):
    
    EXAMPLE = 'example.txt'

    def test_input_file_parsing(self):
        old_maxDiff = self.maxDiff
        self.maxDiff = None
        
        answer_monkey_str = '''Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
'''
        parsed_monkey_str = '\n'.join([str(m) for m in solution.parse_input_file_into_monkey_list(self.EXAMPLE)])
        self.assertEqual(answer_monkey_str, parsed_monkey_str)
        
        self.maxDiff = old_maxDiff

if __name__ == '__main__':
    unittest.main()