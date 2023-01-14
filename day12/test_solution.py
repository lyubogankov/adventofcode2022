# std library
import unittest
# local
import solution

class TestSolution(unittest.TestCase):
    
    EXAMPLE = 'example.txt'

    def test_input_file_parsing(self):
        example_grid_str = \
'''Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
'''
        start_node, end_node, nodes = solution.parse_input_into_graph(
            inputfile='example.txt',
            edge_rule_fn=solution.part_one_edge_rule_fn
        )
        parsed_graph_print_str = solution.generate_print_str_graph(
            nodes,
            grid_width=8,
            grid_height=5,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=False
        )
        self.assertEqual(parsed_graph_print_str, example_grid_str)

    def test_partone_shortest_path(self):
        start_node, end_node, nodes = solution.parse_input_into_graph(
            inputfile='example.txt',
            edge_rule_fn=solution.part_one_edge_rule_fn
        )
        shortest_path_len, _ = solution.dijstras_shortest_path(nodes, start_node.coords, end_node.coords)
        self.assertEqual(shortest_path_len, 31)

    def test_partone_shortest_path_printout(self):
        shortest_path_example = \
'''v..v<<<<
>v.vv<<^
.>vv>E^^
..v>>>^^
..>>>>>^
'''
        start_node, end_node, nodes = solution.parse_input_into_graph(
            inputfile='example.txt',
            edge_rule_fn=solution.part_one_edge_rule_fn
        )
        shortest_path_len, path_from_start_to_end = solution.dijstras_shortest_path(
            nodes, start_node.coords, end_node.coords
        )
        shortest_path_printout = solution.generate_print_str_shortest_path(
            grid_width=8,
            grid_height=5,
            nodes=nodes,
            shortest_path_coords=path_from_start_to_end
        )
        self.assertEqual(shortest_path_printout, shortest_path_example)



if __name__ == '__main__':
    unittest.main()