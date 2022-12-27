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

    def test_after_round_scores(self):
        answer_after_round_str = '''After round 1, the monkeys are holding items with these worry levels:
Monkey 0: 20, 23, 27, 26
Monkey 1: 2080, 25, 167, 207, 401, 1046
Monkey 2: 
Monkey 3: 

After round 2, the monkeys are holding items with these worry levels:
Monkey 0: 695, 10, 71, 135, 350
Monkey 1: 43, 49, 58, 55, 362
Monkey 2: 
Monkey 3: 

After round 3, the monkeys are holding items with these worry levels:
Monkey 0: 16, 18, 21, 20, 122
Monkey 1: 1468, 22, 150, 286, 739
Monkey 2: 
Monkey 3: 

After round 4, the monkeys are holding items with these worry levels:
Monkey 0: 491, 9, 52, 97, 248, 34
Monkey 1: 39, 45, 43, 258
Monkey 2: 
Monkey 3: 

After round 5, the monkeys are holding items with these worry levels:
Monkey 0: 15, 17, 16, 88, 1037
Monkey 1: 20, 110, 205, 524, 72
Monkey 2: 
Monkey 3: 

After round 6, the monkeys are holding items with these worry levels:
Monkey 0: 8, 70, 176, 26, 34
Monkey 1: 481, 32, 36, 186, 2190
Monkey 2: 
Monkey 3: 

After round 7, the monkeys are holding items with these worry levels:
Monkey 0: 162, 12, 14, 64, 732, 17
Monkey 1: 148, 372, 55, 72
Monkey 2: 
Monkey 3: 

After round 8, the monkeys are holding items with these worry levels:
Monkey 0: 51, 126, 20, 26, 136
Monkey 1: 343, 26, 30, 1546, 36
Monkey 2: 
Monkey 3: 

After round 9, the monkeys are holding items with these worry levels:
Monkey 0: 116, 10, 12, 517, 14
Monkey 1: 108, 267, 43, 55, 288
Monkey 2: 
Monkey 3: 

After round 10, the monkeys are holding items with these worry levels:
Monkey 0: 91, 16, 20, 98
Monkey 1: 481, 245, 22, 26, 1092, 30
Monkey 2: 
Monkey 3: 

...

After round 15, the monkeys are holding items with these worry levels:
Monkey 0: 83, 44, 8, 184, 9, 20, 26, 102
Monkey 1: 110, 36
Monkey 2: 
Monkey 3: 

...

After round 20, the monkeys are holding items with these worry levels:
Monkey 0: 10, 12, 14, 26, 34
Monkey 1: 245, 93, 53, 199, 115
Monkey 2: 
Monkey 3: 
'''
        monkeys = self.get_monkeys()
        items = self.get_items()
        after_round_strs = solution_np.play_n_rounds(items, monkeys, num_rounds=20, gen_after_round_str=True)
        gen_after_round_str =   '\n'.join(after_round_strs[:10]) \
                              + '\n...\n\n'                      \
                              + after_round_strs[14]             \
                              + '\n...\n\n'                      \
                              + after_round_strs[19]
        self.assertEqual(answer_after_round_str, gen_after_round_str)

    def test_item_inspection_counts(self):
        # part one
        answer_items_inspected = '''Monkey 0 inspected items 101 times.
Monkey 1 inspected items 95 times.
Monkey 2 inspected items 7 times.
Monkey 3 inspected items 105 times.'''
        
        monkeys = self.get_monkeys()
        items = self.get_items()
        items, monkeys = solution_np.play_n_rounds(items, monkeys, num_rounds=20)
        gen_items_inspected = solution_np.generate_items_inspected_str(monkeys)
        self.assertEqual(answer_items_inspected, gen_items_inspected)


        # part two
        answer_items_inspected = '''== After round 1 ==
Monkey 0 inspected items 2 times.
Monkey 1 inspected items 4 times.
Monkey 2 inspected items 3 times.
Monkey 3 inspected items 6 times.

== After round 20 ==
Monkey 0 inspected items 99 times.
Monkey 1 inspected items 97 times.
Monkey 2 inspected items 8 times.
Monkey 3 inspected items 103 times.

== After round 1000 ==
Monkey 0 inspected items 5204 times.
Monkey 1 inspected items 4792 times.
Monkey 2 inspected items 199 times.
Monkey 3 inspected items 5192 times.

== After round 2000 ==
Monkey 0 inspected items 10419 times.
Monkey 1 inspected items 9577 times.
Monkey 2 inspected items 392 times.
Monkey 3 inspected items 10391 times.

== After round 3000 ==
Monkey 0 inspected items 15638 times.
Monkey 1 inspected items 14358 times.
Monkey 2 inspected items 587 times.
Monkey 3 inspected items 15593 times.

== After round 4000 ==
Monkey 0 inspected items 20858 times.
Monkey 1 inspected items 19138 times.
Monkey 2 inspected items 780 times.
Monkey 3 inspected items 20797 times.

== After round 5000 ==
Monkey 0 inspected items 26075 times.
Monkey 1 inspected items 23921 times.
Monkey 2 inspected items 974 times.
Monkey 3 inspected items 26000 times.

== After round 6000 ==
Monkey 0 inspected items 31294 times.
Monkey 1 inspected items 28702 times.
Monkey 2 inspected items 1165 times.
Monkey 3 inspected items 31204 times.

== After round 7000 ==
Monkey 0 inspected items 36508 times.
Monkey 1 inspected items 33488 times.
Monkey 2 inspected items 1360 times.
Monkey 3 inspected items 36400 times.

== After round 8000 ==
Monkey 0 inspected items 41728 times.
Monkey 1 inspected items 38268 times.
Monkey 2 inspected items 1553 times.
Monkey 3 inspected items 41606 times.

== After round 9000 ==
Monkey 0 inspected items 46945 times.
Monkey 1 inspected items 43051 times.
Monkey 2 inspected items 1746 times.
Monkey 3 inspected items 46807 times.

== After round 10000 ==
Monkey 0 inspected items 52166 times.
Monkey 1 inspected items 47830 times.
Monkey 2 inspected items 1938 times.
Monkey 3 inspected items 52013 times.
'''
        
        gen_items_inspected = ''
        monkeys = self.get_monkeys()
        items = self.get_items()

        rounds_played = 0
        for round in [1, 20] + list(range(1_000, 10_001, 1_000)):
            gen_items_inspected += f'== After round {round} == \n'
            items, monkeys = solution_np.play_n_rounds(items, monkeys, num_rounds=(round-rounds_played), worryfatigue=True)
            gen_items_inspected += solution_np.generate_items_inspected_str(monkeys)
            print('\n... done with round', round)
            if round < 10_000:
                gen_items_inspected += '\n'
        self.assertEqual(answer_items_inspected, gen_items_inspected)

if __name__ == '__main__':
    unittest.main()