# std library
import unittest
# local
import solution

class TestDay13(unittest.TestCase):

    EXAMPLE = 'example.txt'
    INPUT   = 'input.txt'

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    def test_file_parsing(self):
        for textfile in [self.EXAMPLE, self.INPUT]:
            for method in ('iterative', 'recursive'):
                with self.subTest(i=f'{textfile} {method}'):
                    packet_pairs = solution.parse_input_file_into_packet_pairs(textfile, method=method)
                    # generate string, to compare against file contents
                    reconstructed_str = ''
                    for i, packet_pair in enumerate(packet_pairs):
                        for packet in packet_pair:
                            reconstructed_str += solution.generate_list_str(packet) + '\n'
                        if i < len(packet_pairs) - 1:
                            reconstructed_str += '\n'
                    # compare
                    with open(textfile, 'r') as f:
                        contents = f.read()
                    self.assertEqual(contents, reconstructed_str)

    def test_example_order_correctness(self):
        example_outputs = [
'''== Pair 1 ==
- Compare [1,1,3,1,1] vs [1,1,5,1,1]
  - Compare 1 vs 1
  - Compare 1 vs 1
  - Compare 3 vs 5
    - Left side is smaller, so inputs are in the right order
''',

'''== Pair 2 ==
- Compare [[1],[2,3,4]] vs [[1],4]
  - Compare [1] vs [1]
    - Compare 1 vs 1
  - Compare [2,3,4] vs 4
    - Mixed types; convert right to [4] and retry comparison
    - Compare [2,3,4] vs [4]
      - Compare 2 vs 4
        - Left side is smaller, so inputs are in the right order
''',

'''== Pair 3 ==
- Compare [9] vs [[8,7,6]]
  - Compare 9 vs [8,7,6]
    - Mixed types; convert left to [9] and retry comparison
    - Compare [9] vs [8,7,6]
      - Compare 9 vs 8
        - Right side is smaller, so inputs are not in the right order
''',

'''== Pair 4 ==
- Compare [[4,4],4,4] vs [[4,4],4,4,4]
  - Compare [4,4] vs [4,4]
    - Compare 4 vs 4
    - Compare 4 vs 4
  - Compare 4 vs 4
  - Compare 4 vs 4
  - Left side ran out of items, so inputs are in the right order
''',

'''== Pair 5 ==
- Compare [7,7,7,7] vs [7,7,7]
  - Compare 7 vs 7
  - Compare 7 vs 7
  - Compare 7 vs 7
  - Right side ran out of items, so inputs are not in the right order
''',

'''== Pair 6 ==
- Compare [] vs [3]
  - Left side ran out of items, so inputs are in the right order
''',

'''== Pair 7 ==
- Compare [[[]]] vs [[]]
  - Compare [[]] vs []
    - Right side ran out of items, so inputs are not in the right order
''',

'''== Pair 8 ==
- Compare [1,[2,[3,[4,[5,6,7]]]],8,9] vs [1,[2,[3,[4,[5,6,0]]]],8,9]
  - Compare 1 vs 1
  - Compare [2,[3,[4,[5,6,7]]]] vs [2,[3,[4,[5,6,0]]]]
    - Compare 2 vs 2
    - Compare [3,[4,[5,6,7]]] vs [3,[4,[5,6,0]]]
      - Compare 3 vs 3
      - Compare [4,[5,6,7]] vs [4,[5,6,0]]
        - Compare 4 vs 4
        - Compare [5,6,7] vs [5,6,0]
          - Compare 5 vs 5
          - Compare 6 vs 6
          - Compare 7 vs 0
            - Right side is smaller, so inputs are not in the right order
''']
        
        packet_pairs = solution.parse_input_file_into_packet_pairs(self.EXAMPLE)
        for _i, (lhs, rhs) in enumerate(packet_pairs):
            i = _i + 1
            _, print_str = solution.determine_order_correctness(lhs, rhs, pairnum=i)
            with self.subTest(i=i):
                self.assertEqual(print_str, example_outputs[_i])

    def test_example_correct_indices(self):
        '''With this test, I don't need to also test the sum of the indices, 
           bc that's a built-in function!'''
        packet_pairs = solution.parse_input_file_into_packet_pairs(self.EXAMPLE)
        correct_order_pair_numbers = solution.part_one_find_all_correct_pairs(packet_pairs)
        self.assertEqual([1, 2, 4, 6], correct_order_pair_numbers)

if __name__ == '__main__':
    unittest.main()