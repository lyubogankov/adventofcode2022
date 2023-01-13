# std library
from collections import namedtuple
from pprint import pprint

### colors
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
RESET = '\033[0m'

### input file -> data structure
Node = namedtuple('Node', ['height', 'coords', 'connections', 'shortest_path_from_source'])
# Edge = namedtuple('Edge', ['weight', 'node_one_coords', 'node_two_coords'])  # undirected edge
DirectedEdge = namedtuple('DirectedEdge', ['weight', 'node_from_coords', 'node_to_coords'])
class Point_2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point_2D(x={' ' if self.x >= 0 else ''}{self.x}, y={' ' if self.y >= 0 else ''}{self.y})"
    def __str__(self):
        return f"({' ' if self.x >= 0 else ''}{self.x}, {' ' if self.y >= 0 else ''}{self.y})"
    def __add__(self, point2):
        point1 = self
        x = point1.x + point2.x
        y = point1.y + point2.y
        return Point_2D(x, y)
    def __sub__(self, point2):
        point1 = self
        x = point1.x - point2.x
        y = point1.y - point2.y
        return Point_2D(x, y)
    def __mul__(self, k):
        if isinstance(k, int):
            return Point_2D(k*self.x, k*self.y)
    def __iadd__(self, point2):
        point1 = self
        point1.x += point2.x
        point1.y += point2.y
        return point1
    # heavily inspired by https://stackoverflow.com/q/390250
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False
    # https://stackoverflow.com/a/1608882 -- if I implement __eq__, I also need to implement __hash__
    # https://stackoverflow.com/a/2909119 -- solution for implementing hash.  Rely on hash of tuple!
    def __hash__(self):
        key = (self.x, self.y)
        return hash(key)

def generate_print_str_connected_graph(nodes, grid_width, grid_height):

    WIDTH_BETWEEN_CHARS_X = 5
    WIDTH_BETWEEN_CHARS_Y = 2
    ARROW_COLOR = MAGENTA
    print_str = ''

    for y in range(grid_height):  # rows
    
        row_str = ''
        for x in range(grid_width):  # cols
            curr_node = nodes[(x, y)]
            
            # check whether the node to the left is connected to current node
            if x > 0:
                left_neighbor = nodes[(x-1, y)]
                neighb_to_node = DirectedEdge(
                    weight=1,
                    node_from_coords=left_neighbor.coords,
                    node_to_coords=curr_node.coords
                )
                node_to_neighb = DirectedEdge(
                    weight=1,
                    node_from_coords=curr_node.coords,
                    node_to_coords=left_neighbor.coords
                )

                right_conn = neighb_to_node in left_neighbor.connections
                left_conn = node_to_neighb in curr_node.connections
                row_str += ' '
                if left_conn or right_conn:
                    row_str += ARROW_COLOR
                    row_str += '<' if left_conn else '-'
                    row_str += '-'
                    row_str += '>' if right_conn else '-'
                    row_str += RESET
                else:
                    row_str += ' '*(WIDTH_BETWEEN_CHARS_X - 2)
                row_str += ' '

                # if neighb_to_node in left_neighbor.connections:
                #     row_str += '-->'
                # if node_to_neighb in curr_node.connections:
                #     row_str += '<--'
                # else:
                #     row_str += ' '*WIDTH_BETWEEN_CHARS_X

            row_str += curr_node.height

        # if applicable, check last two lines for any connections
        if y > 0:
            between_rows_str_top = ''
            between_rows_str_bot = ''
            for x in range(grid_width):
                curr_node = nodes[(x, y)]
                bottom_neighbor = nodes[(x, y-1)]

                neighb_to_node = DirectedEdge(
                    weight=1,
                    node_from_coords=bottom_neighbor.coords,
                    node_to_coords=curr_node.coords
                )
                node_to_neighb = DirectedEdge(
                    weight=1,
                    node_from_coords=curr_node.coords,
                    node_to_coords=bottom_neighbor.coords
                )

                top_conn = neighb_to_node in bottom_neighbor.connections
                bot_conn = node_to_neighb in curr_node.connections
                if top_conn or bot_conn:
                    between_rows_str_top += ARROW_COLOR
                    between_rows_str_bot += ARROW_COLOR
                    between_rows_str_top += '^' if top_conn else '|'
                    between_rows_str_bot += 'v' if bot_conn else '|'
                    between_rows_str_top += RESET
                    between_rows_str_bot += RESET
                else:
                    between_rows_str_top += ''
                    between_rows_str_top += ''

                # if neighb_to_node in bottom_neighbor.connections:
                #     between_rows_str_top += '^'
                #     between_rows_str_bot += '|'
                # elif node_to_neighb in curr_node.connections:
                #     between_rows_str_top += '|'
                #     between_rows_str_bot += 'v'
                # else:
                #     between_rows_str_top += ''
                #     between_rows_str_top += ''
                
                if x < grid_width - 1:
                    between_rows_str_top += ' '*WIDTH_BETWEEN_CHARS_X
                    between_rows_str_bot += ' '*WIDTH_BETWEEN_CHARS_X
            print_str = between_rows_str_top + '\n' + between_rows_str_bot + '\n' + print_str

        print_str = row_str + '\n' + print_str

    return print_str

def parse_input_into_graph(inputfile, edge_rule_fn):
    # return the start node as the graph?

    with open(inputfile, 'r') as f:
        lines = list(f)

    start_node = None
    end_node = None
    nodes = {}

    # lines from bottom -> top, read left-to-right
    for y, row in enumerate(reversed(lines)):
        print('row ', y)
        for x, node_height in enumerate(row.rstrip()):  # looping over each character in the row str
            print(f'\tcol {x}: {node_height}')

            if node_height == 'S':
                start_node = node = Node(height='a', coords=Point_2D(x, y), connections=set(), shortest_path_from_source=[])
            elif node_height == 'E':
                end_node   = node = Node(height='z', coords=Point_2D(x, y), connections=set(), shortest_path_from_source=[])
            else:
                node = Node(height=node_height, coords=Point_2D(x, y), connections=set(), shortest_path_from_source=[])

            # this is how I'm looking up the nodes
            nodes[(x, y)] = node

            # form connections between this node and prior nodes, if applicable
                                             # left neighbor,     bottom neighbor
            for condition, neighborcoords in [(x > 0, (x-1, y)), (y > 0, (x, y-1))]:
                if condition:
                    neighbor = nodes[neighborcoords]  # either to the left, or below current node
                    if edge_rule_fn(node, neighbor):
                        edge = DirectedEdge(
                            weight=1,
                            node_from_coords=node.coords,
                            node_to_coords=neighbor.coords
                        )
                        node.connections.add(edge)
                    if edge_rule_fn(neighbor, node):
                        edge = DirectedEdge(
                            weight=1,
                            node_from_coords=neighbor.coords,
                            node_to_coords=node.coords
                        )
                        neighbor.connections.add(edge)

    return start_node, end_node, nodes

### part one


# first try my own dijstra implementation, then try this:
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.dijkstra.html


if __name__ == '__main__':
    
    start_node, end_node, nodes = parse_input_into_graph(
        inputfile='example.txt',
        # for part one - "if height diff is higher than +1, can't traverse"
        edge_rule_fn=lambda curr_node, adj_node: ord(adj_node.height) - ord(curr_node.height) <= 1
    )
    # for node_coords, node in nodes.items():
    #     print(node_coords, node.height)
    print(generate_print_str_connected_graph(nodes, grid_width=8, grid_height=5))