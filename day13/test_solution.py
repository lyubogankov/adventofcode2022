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

    def test_input_file_parsing(self):
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

if __name__ == '__main__':
    unittest.main()