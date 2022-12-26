# std library
import copy
import unittest
# local
import solution_np

class TestDay11(unittest.TestCase):

    EXAMPLE = 'example.txt'

    def setUp(self):
        self.maxDiff = None
        self.items, self.monkeys = solution_np.parse_input_file_into_items_and_monkey_list(self.EXAMPLE)

    def get_monkeys(self):
        return copy.deepcopy(self.monkeys)
    def get_items(self):
        return copy.deepcopy(self.items)

    def test_input_file_parsing(self):
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
        parsed_monkey_str = solution_np.generate_pretty_print_str_items_and_monkeys(self.get_items(), self.get_monkeys())
        self.assertEqual(answer_monkey_str, parsed_monkey_str)

if __name__ == '__main__':
    unittest.main()