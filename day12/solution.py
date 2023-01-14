# std library
import math
import pdb
import time
import os
import sys
from collections import namedtuple
from pprint import pprint
# local
ANIMATION_GIF_MODE = False
if ANIMATION_GIF_MODE:
    _file = os.path.dirname(f'{os.getcwd()}/{__file__}')
    sys.path.append(f'{os.path.dirname(_file)}/common')
    import screenshot
    params=screenshot.ScreenshotParams(
        topoffset=46,
        leftoffset=0,
        width=1360,
        height=788,
        monitor=1,
        framefolder='dijkstra_bad'
    )

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
Node = namedtuple('Node', ['height', 'coords', 'connections', 'shortest_path_from_start'])
# Edge = namedtuple('Edge', ['weight', 'node_one_coords', 'node_two_coords'])  # undirected edge
DirectedEdge = namedtuple('DirectedEdge', ['weight', 'node_to_coords'])  # edges belong to nodes, so the "from" is the node to which the edge belongs

def parse_input_into_graph(inputfile, edge_rule_fn):
    # return the start node as the graph?

    with open(inputfile, 'r') as f:
        lines = list(f)

    start_node = None
    end_node = None
    nodes = {}

    # lines from bottom -> top, read left-to-right
    for y, row in enumerate(reversed(lines)):
        for x, node_height in enumerate(row.rstrip()):  # looping over each character in the row str
            if node_height == 'S':
                start_node = node = Node(height='a', coords=(x, y), connections=set(), shortest_path_from_start=[])  # previously, Point_2D(x, y)
            elif node_height == 'E':
                end_node   = node = Node(height='z', coords=(x, y), connections=set(), shortest_path_from_start=[])  # previously, Point_2D(x, y)
            else:
                node = Node(height=node_height, coords=(x, y), connections=set(), shortest_path_from_start=[])  # previously, Point_2D(x, y)

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
                            # node_from_coords=node.coords,
                            node_to_coords=neighbor.coords
                        )
                        node.connections.add(edge)
                    if edge_rule_fn(neighbor, node):
                        edge = DirectedEdge(
                            weight=1,
                            # node_from_coords=neighbor.coords,
                            node_to_coords=node.coords
                        )
                        neighbor.connections.add(edge)

    return start_node, end_node, nodes

def generate_print_str_graph(nodes, grid_width, grid_height, start_coords=None, end_coords=None, connected=False):

    WIDTH_BETWEEN_CHARS_X = 5
    WIDTH_BETWEEN_CHARS_Y = 2
    ARROW_COLOR = MAGENTA
    print_str = ''

    for y in range(grid_height):  # rows
    
        row_str = ''
        for x in range(grid_width):  # cols
            curr_node = nodes[(x, y)]
            
            # check whether the node to the left is connected to current node
            if x > 0 and connected:
                left_neighbor = nodes[(x-1, y)]
                neighb_to_node = DirectedEdge(
                    weight=1,
                    # node_from_coords=left_neighbor.coords,
                    node_to_coords=curr_node.coords
                )
                node_to_neighb = DirectedEdge(
                    weight=1,
                    # node_from_coords=curr_node.coords,
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

            if (x, y) == start_coords:
                row_str += 'S'
            elif (x, y) == end_coords:
                row_str += 'E'
            else:
                row_str += curr_node.height

        # if applicable, check last two lines for any connections
        if y > 0 and connected:
            between_rows_str_top = ''
            between_rows_str_bot = ''
            for x in range(grid_width):
                curr_node = nodes[(x, y)]
                bottom_neighbor = nodes[(x, y-1)]

                neighb_to_node = DirectedEdge(
                    weight=1,
                    # node_from_coords=bottom_neighbor.coords,
                    node_to_coords=curr_node.coords
                )
                node_to_neighb = DirectedEdge(
                    weight=1,
                    # node_from_coords=curr_node.coords,
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
                
                if x < grid_width - 1:
                    between_rows_str_top += ' '*WIDTH_BETWEEN_CHARS_X
                    between_rows_str_bot += ' '*WIDTH_BETWEEN_CHARS_X
            print_str = between_rows_str_top + '\n' + between_rows_str_bot + '\n' + print_str
        print_str = row_str + '\n' + print_str
    return print_str

def direction_arrow_for_node_from(node_from_coords, node_to_coords):
    x_from, y_from = node_from_coords
    x_to,   y_to   = node_to_coords
    if   x_to - x_from ==  1: return '>'
    elif x_to - x_from == -1: return '<'
    elif y_to - y_from ==  1: return '^'
    elif y_to - y_from == -1: return 'v'
    else:
        raise Exception(f'Unexpected coord pair: {node_from_coords} -> {node_to_coords}')

def generate_annotated_print_str(grid_width, grid_height, nodes, shortest_path_coords=[], color_shortest_path=False, unvisited_set=set(), current_coords=None):

    if shortest_path_coords:
        from_to_pairs = zip(shortest_path_coords[:-1], shortest_path_coords[1:])
        shortest_path_node_arrows = { _from : direction_arrow_for_node_from(_from, _to) for _from, _to in from_to_pairs}

    print_str = ''
    for y in range(grid_height):  # rows
        row_str = ''
        for x in range(grid_width):  # cols
            # setup
            color = None
            height = nodes[(x, y)].height
            # shortest path
            if shortest_path_coords and (x, y) in shortest_path_node_arrows:
                row_str += shortest_path_node_arrows[(x, y)]
            elif shortest_path_coords and (x, y) == shortest_path_coords[-1]:
                row_str += 'E'
            # coloring as the alg runs to visualize what we've already looked at
            elif (x, y) == current_coords:
                color = GREEN
            elif unvisited_set:
                color = BLACK if (x, y) in unvisited_set else YELLOW
            # default case - coloring for shortest path
            elif color_shortest_path:
                if height == 'a':
                    color = GREEN
                elif height == 'c':
                    color = YELLOW
                else:
                    color = MAGENTA
            else:
                row_str += '.'
            # some of the if statements above modify color but don't themselves append to row_str.
            if color:
                row_str += f'{color}{height}{RESET}'
        print_str = row_str + '\n' + print_str
    return print_str
def generate_print_str_shortest_path(grid_width, grid_height, nodes, shortest_path_coords, color_shortest_path=False):
    return generate_annotated_print_str(
        grid_width, grid_height, nodes,
        shortest_path_coords=shortest_path_coords,
        color_shortest_path=color_shortest_path
    )
def generate_print_str_during_sim(grid_width, grid_height, nodes, unvisited_set, current_coords):
    return generate_annotated_print_str(grid_width, grid_height, nodes, unvisited_set=unvisited_set, current_coords=current_coords)


### part one
part_one_edge_rule_fn = lambda curr_node, adj_node: ord(adj_node.height) - ord(curr_node.height) <= 1

def dijstras_shortest_path(nodes, start_coords, end_coords, _print=False, _animate=False, screenshotter=None):
    '''
    Arguments
        nodes: dictionary
            Maps coordinates, tuple of two integers (x, y), to Node namedtuples
        start_coords: 2-tuple of integers
            (x, y) coordinates of start node
        end_coords: 2-tuple of integers
            (x, y) coordinates of end node
    
    Returns
        shortest_path_len: int
            Number of steps in the shortest path
        shortest_path: list of Nodes
            From start -> end, each node visited.  Can be used to print the path.
    
    From https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
    '''
    
    ## Setup
    grid_height = max(y+1 for (x, y) in nodes.keys())
    grid_width  = max(x+1 for (x, y) in nodes.keys())

    # 1. Create set of unvisited nodes.
    unvisited_coords = set(nodes.keys())

    # 2. Create tentative distance tracker
    # https://stackoverflow.com/questions/7781260/how-can-i-represent-an-infinite-number-in-python
    tentative_distance_from_start = {coords : math.inf for coords in unvisited_coords}
    tentative_distance_from_start[start_coords] = 0

    ## Run Dijstra's alg!
    current_coords = start_coords
    while len(unvisited_coords) > 0:

        # 3. For current node, look at all of its unvisited edges and calculate distance from start -> neighbor.
        for edge in nodes[current_coords].connections:

            if edge.node_to_coords not in unvisited_coords:
                continue

            start_to_neighb_dist_thru_curr_node = tentative_distance_from_start[current_coords] + edge.weight
            start_to_neighb_shortest_known_path = tentative_distance_from_start[edge.node_to_coords]

            if start_to_neighb_dist_thru_curr_node < start_to_neighb_shortest_known_path:
                # found shorter path - update!
                tentative_distance_from_start[edge.node_to_coords] = start_to_neighb_dist_thru_curr_node
                # write down best known path from source -> current node
                nodes[edge.node_to_coords].shortest_path_from_start.clear()
                for coords in nodes[current_coords].shortest_path_from_start:
                    nodes[edge.node_to_coords].shortest_path_from_start.append(coords)
                nodes[edge.node_to_coords].shortest_path_from_start.append(current_coords)

        # 4. Current node is done!  Remove it from unvisited set.
        unvisited_coords.remove(current_coords)

        if _animate:
            os.system('clear')  # linux only
            print(generate_print_str_during_sim(
                grid_width,
                grid_height,
                nodes,
                unvisited_set=unvisited_coords,
                current_coords=current_coords
            ))
            time.sleep(0.3)
            screenshot.screenshot(screenshotter, params, sim_iteration=f'{len(nodes) - len(unvisited_coords)}', savefolder='day12')

        # 5. Check for termination
        if current_coords == end_coords:
            shortest_path_len = tentative_distance_from_start[current_coords]
            path_from_start_to_end = nodes[current_coords].shortest_path_from_start + [current_coords]
            return shortest_path_len, path_from_start_to_end

        # 6. Select next node!
        min_tentative_distance = math.inf
        for coords in unvisited_coords:
            if tentative_distance_from_start[coords] < min_tentative_distance:
                current_coords = coords
                min_tentative_distance = tentative_distance_from_start[coords]

    # terminate after looking at the whole graph
    shortest_path_len = tentative_distance_from_start[end_coords]
    path_from_start_to_end = nodes[end_coords].shortest_path_from_start + [end_coords]
    return shortest_path_len, path_from_start_to_end


# first try my own dijstra implementation, then try this:
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.dijkstra.html


if __name__ == '__main__':
    
    if ANIMATION_GIF_MODE:
        screenshotter = screenshot.mss.mss()

    for inputfile in ['example.txt', 'input.txt']:
        example = inputfile == 'example.txt'
        if example:
            grid_width = 8
            grid_height = 5
        else:
            grid_width = 113
            grid_height = 41

        print('\n---', inputfile)

        start_node, end_node, nodes = parse_input_into_graph(
            inputfile=inputfile,
            # for part one - "if height diff is higher than +1, can't traverse"
            edge_rule_fn=part_one_edge_rule_fn
        )

        if example:  # input is too large to render like this
            print(generate_print_str_graph(
                nodes,
                grid_width,
                grid_height,
                start_coords=start_node.coords,
                end_coords=end_node.coords,
                connected=True))  # example
        
        shortest_path_len, path_from_start_to_end = dijstras_shortest_path(
            nodes, start_node.coords, end_node.coords,
            _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        )

        print(f'Shortest path length from S -> E: {shortest_path_len}', end='\n\n')
        print(generate_print_str_shortest_path(grid_width, grid_height, nodes, path_from_start_to_end, color_shortest_path=not(example)))

    if ANIMATION_GIF_MODE:
        screenshotter.close()