# std library
import heapq
import math
import pdb
import time
import os
import sys
from collections import namedtuple, defaultdict, deque
from pprint import pprint
# third party
import numpy as np
# local
ANIMATION_GIF_MODE = False
if ANIMATION_GIF_MODE:
    _file = os.path.dirname(f'{os.getcwd()}/{__file__}')
    sys.path.append(f'{os.path.dirname(_file)}/common')
    import screenshot
    params=screenshot.ScreenshotParams(
        topoffset=56,
        leftoffset=0,
        width=909,
        height=761-56,
        monitor=1,
        framefolder='a_star'
    )

### colors
# (8 colors)
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
RESET = '\033[0m'
# # 256 colors -- hand-picking colors for aesthetics
# # for contrast, repeating ROYGBIV since the elevation spirals up to peak
height_colorcode_map = {
    'a' : 106,
    'b' : 100,
    'c' : 103,
    'd' : 124,  # R ---
    'e' : 166,  # 0
    'f' : 227,  # Y
    'g' : 28,   # G
    'h' : 27,   # B
    'i' : 63,   # I
    'j' : 90,   # V
    'k' : 88,   # R ---
    'l' : 208,  # O
    'm' : 154,  # Y
    'n' : 82,   # G
    'o' : 117,  # B
    'p' : 105,  # I
    'q' : 135,  # V
    'r' : 160,  # R ---
    's' : 130,  # O
    't' : 227,  # Y
    'u' : 28,   # G
    'v' : 38,   # B
    'w' : 33,   # I
    'x' : 92,   # V
    'y' : 123,  # bonus
    'z' : 160,  # bonus
}
# using 256 colors!  https://www.ditig.com/256-colors-cheat-sheet
# height_colorcode_map = {}
# # a-c = shades of grey
# for i in range(0, 3):
#     letter = chr(ord('a') + i)
#     height_colorcode_map[letter] = 244 + i*3
# # d-z = shades of pink -> red
# for i in range(3, 26):
#     letter = chr(ord('a') + i)
#     height_colorcode_map[letter] = 183 - (i-3)
height_color_map = {chr : f'\033[38;5;{color}m' for chr, color in height_colorcode_map.items()}

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

### printing
def generate_print_str_graph(nodes, grid_width, grid_height, start_coords=None, end_coords=None, connected=False, heightcolors=False):

    WIDTH_BETWEEN_CHARS_X = 5
    WIDTH_BETWEEN_CHARS_Y = 2
    ARROW_COLOR = '\033[38;5;39m'
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
            elif heightcolors:
                row_str += f'{height_color_map[curr_node.height]}{curr_node.height}{RESET}'
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

def generate_annotated_print_str(grid_width, grid_height, nodes, shortest_path_coords=[],unvisited_set=set(), current_coords=None, heightcolor=False, arrowcolor=WHITE):

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
                row_str += f'{arrowcolor}{shortest_path_node_arrows[(x, y)]}{RESET}'
            elif shortest_path_coords and (x, y) == shortest_path_coords[-1]:
                row_str += 'E'
            # coloring as the alg runs to visualize what we've already looked at
            elif (x, y) == current_coords:
                color = GREEN
            elif unvisited_set:
                color = BLACK if (x, y) in unvisited_set else height_color_map[height]
            # default case - coloring for shortest path
            elif heightcolor:
                color = height_color_map[height]
            else:
                row_str += '.'
            # some of the if statements above modify color but don't themselves append to row_str.
            if color:
                row_str += f'{color}{height}{RESET}'
        print_str = row_str + '\n' + print_str
    return print_str
def generate_print_str_shortest_path(grid_width, grid_height, nodes, shortest_path_coords, heightcolor=False, arrowcolor=WHITE):
    return generate_annotated_print_str(
        grid_width, grid_height, nodes,
        shortest_path_coords=shortest_path_coords,
        heightcolor=heightcolor, arrowcolor=arrowcolor
    )
def generate_print_str_during_sim(grid_width, grid_height, nodes, unvisited_set, current_coords, heightcolor=False):
    return generate_annotated_print_str(grid_width, grid_height, nodes, unvisited_set=unvisited_set, current_coords=current_coords, heightcolor=heightcolor)

def generate_astar_pring_str_during_sim(grid_width, grid_height, nodes, exploration_boundary, visited_coords, heightcolor):
    print_str = ''
    for y in range(grid_height):  # rows
        row_str = ''
        for x in range(grid_width):  # cols
            height = nodes[(x, y)].height
            # deciding node color
            if (x, y) in exploration_boundary:
                color = '\033[48;5;240m' + GREEN
            elif (x, y) in visited_coords:
                color = height_color_map[height]
            else:
                color = BLACK
            row_str += f'{color}{height}{RESET}'
        print_str = row_str + '\n' + print_str
    return print_str

def generate_shortest_path_comparison_print_str(grid_width, grid_height, nodes, shortest_paths):
    
    arrow_annotations = []
    for shortest_path_coords in shortest_paths:
        from_to_pairs = zip(shortest_path_coords[:-1], shortest_path_coords[1:])
        arrow_annotations.append({_from : direction_arrow_for_node_from(_from, _to) for _from, _to in from_to_pairs})
    
    shortest_path_colors = [
        '\033[38;5;39m',  # DeepSkyBlue1
        '\033[38;5;51m',  # Cyan
        '\033[38;5;11m',  # Yellow
        '\033[38;5;10m',  # Lime
    ]

    print_str = ''
    for y in range(grid_height):  # rows
        row_str = ''
        for x in range(grid_width):  # cols
            # setup
            height = nodes[(x, y)].height
            included_in_paths = []
            for i, arrows in enumerate(arrow_annotations):
                if (x, y) in arrows:
                    included_in_paths.append(i)
            # pick colors and/or display str
            if (x, y) == shortest_path_coords[0][-1]:
                row_str += 'E'
            # elif len(included_in_paths) == len(arrow_annotations):
            #     row_str += arrow_annotations[0][(x, y)]
            elif len(included_in_paths) > 0:
                idx = included_in_paths[-1]
                arrowcolor = shortest_path_colors[idx]
                arrow = arrow_annotations[idx][(x, y)]
                row_str += f'{arrowcolor}{arrow}{RESET}'
            else:
                heightcolor = height_color_map[height]
                row_str += f'{heightcolor}{height}{RESET}'
        print_str = row_str + '\n' + print_str
    return print_str

### part one
part_one_edge_rule_fn = lambda curr_node, adj_node: ord(adj_node.height) - ord(curr_node.height) <= 1

# first try my own dijstra implementation, then try this:
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.dijkstra.html
def dijstras_shortest_path(nodes, start_coords, end_coords, _animate=False, screenshotter=None):
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
                current_coords=current_coords,
                heightcolor=True
            ))
            time.sleep(0.3)
            if ANIMATION_GIF_MODE:
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

def manhattan_distance(point_one, point_two):
    '''Returns the "Manhattan", or 4-way grid, distance between two points.

    Inputs:
        point_one, point_two: 2-tuple of integers (x, y)

    Returns
        integer

    https://en.wikipedia.org/wiki/Taxicab_geometry
    '''
    x1, y1 = point_one
    x2, y2 = point_two
    return abs(x2 - x1) + abs(y2 - y1)

def reconstruct_path(camefrom, current_coords):
    path = deque([current_coords])
    while current_coords in camefrom:
        current_coords = camefrom[current_coords]
        path.appendleft(current_coords)
    return list(path)

def default_f_of_n(*, g_of_n, h_of_n, **kwargs):
    '''f(n) = g(n) + h(n)'''
    return g_of_n + h_of_n
def height_then_f_of_n(*, current_node, end_node, g_of_n, h_of_n, **kwargs):
    return (
        ord(end_node.height) - ord(current_node.height),  # height difference
        g_of_n + h_of_n                                   # original fscore
    )
def height_dotprod_f_of_n(*, start_node, current_node, end_node, g_of_n, h_of_n, **kwargs):
    v_start_to_n = [current_node.coords[i] - start_node.coords[i] for i in range(2)]  # 0=x, 1=y
    v_n_to_end   = [end_node.coords[i]   - current_node.coords[i] for i in range(2)]
    return (
        ord(end_node.height) - ord(current_node.height),  # height difference,
        np.dot(v_start_to_n, v_n_to_end) / (np.linalg.norm(v_start_to_n) * np.linalg.norm(v_n_to_end)),
        g_of_n + h_of_n
    )

def a_star_shortest_path(nodes, start, end, heuristic_fn=manhattan_distance, fscore_fn=default_f_of_n, _animate=False, screenshotter=None):
    '''Find the shortest path from start to end.  The heuristic function is used to determine next-node selection.
    
    Inputs:
        nodes (dict)
            (x, y) : Node, where x and y are integers and Node is a namedtuple representing a graph node
        start (2-tuple of integers)
        end   (2-tuple of integers)
            (x, y)
        heuristic_fn (function)
            Requred to take two arguments, both coordinate pairs.  Calculates heuristic from start -> end.

    Returns:
        list
            shortest path from start -> end
    
    Note that this function does not use the Node namedtuple's shortest_path_from_start_to_end in leiu of
    the camefrom dict -- a much cleaner solution!

    Take 2 - instead of using f(n) as prioritization criteria, will use:
        (height_end - height_n, f(n)) -- when sorting, this means that climbing hills is higher priority than finding shortest path

    Other ideas:
    - instead of using manhattan distance for h(n),
      could take the normalized dot product between "vector" from start -> n and n -> end to prioritize moving towards end?

      (height_diff, dot_prod(start_n, n_end), g(n)) = priority
    '''
    ## animation setup
    if _animate:
        grid_height = max(y+1 for (_, y) in nodes.keys())
        grid_width  = max(x+1 for (x, _) in nodes.keys())

    ## Setting up data structures

    # Map/dict where camefrom[coords_n] stores the coords of 
    # node immediately preceding node n on shortest path from start.
    camefrom = {}

    # Stores "g(n)" values for each node.  Default = infinity for unvisited nodes.
    shortest_known_path_from_start = defaultdict(lambda: math.inf)
    shortest_known_path_from_start[start] = 0

    # Stores "f(n)" values for each node.  f(n) = g(n)                              + h(n)
    #                                           = shortest_known_path_from_start[n] + heuristic_fn(n)
    # Could re-compute this to avoid storing it, but prioritizing runtime over storage.
    fscore = defaultdict(lambda: math.inf)
    fscore[start] = heuristic_fn(start, end)

    # discovered nodes, ranked by f(n) = g(n) + h(n), where
    #                                    g(n)        = cost from start -> node n
    #                                           h(n) = estimated cost from node n -> end
    # Using a min-heap (heapq.py) as a priority queue
    # Also using a set to keep track of membership of exploration_boundary list, bc lists have O(n) membership.
    #   This doubles the space requirement, though.
    exploration_boundary = [(fscore[start], 0, start)]  # heapq operates on list, it's not a separate data structure.
    exploration_boundary_set = {start,}

    ## Running the search
    while len(exploration_boundary) > 0:
        (_, _, current) = heapq.heappop(exploration_boundary)
        exploration_boundary_set.remove(current)

        if current == end:
            shortest_path = reconstruct_path(camefrom, end)
            return len(shortest_path), shortest_path

        # examine all neighbors
        for edge in nodes[current].connections:
            neighbor = edge.node_to_coords
            path_len_from_start = shortest_known_path_from_start[current] + edge.weight
            
            if path_len_from_start < shortest_known_path_from_start[neighbor]:
                camefrom[neighbor] = current
                shortest_known_path_from_start[neighbor] = path_len_from_start
                # Using passed-in function for fscore to experiment with different approaches.
                # Need to pass all possible arguments that any of my fscore functions may take!
                fscore[neighbor] = fscore_fn(
                    g_of_n=path_len_from_start,
                    h_of_n=heuristic_fn(neighbor, end),
                    start_node=nodes[start],
                    end_node=nodes[end],
                    current_node=nodes[neighbor]
                )
                if neighbor not in exploration_boundary_set:
                    exploration_boundary_set.add(neighbor)
                    # since this is a minheap -- prioritize later-added nodes over earlier-added nodes in case of fscore tie
                    heapq.heappush(exploration_boundary, (fscore[neighbor], -1*len(exploration_boundary), neighbor))

        if _animate:
            os.system('clear')  # linux only
            print(generate_astar_pring_str_during_sim(
                grid_width,
                grid_height,
                nodes,
                exploration_boundary_set,
                visited_coords=set(shortest_known_path_from_start.keys()),
                heightcolor=True
            ))
            time.sleep(0.3)
            if ANIMATION_GIF_MODE:
                iteration = len([dist for dist in shortest_known_path_from_start.values() if dist < math.inf])
                screenshot.screenshot(screenshotter, params, sim_iteration=f'{iteration}', savefolder='day12')

if __name__ == '__main__':
    
    if ANIMATION_GIF_MODE:
        screenshotter = screenshot.mss.mss()

    for inputfile in ['input.txt']: # ['example.txt', 'input.txt']:
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
                connected=True
            ))

        print('\n\n')
        print(generate_print_str_graph(
            nodes,
            grid_width,
            grid_height,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=False,
            heightcolors=True
        ))

        # # Dijkstra's alg
        # shortest_path_len, path_from_start_to_end = dijstras_shortest_path(
        #     nodes, start_node.coords, end_node.coords,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )

        # # A* alg
        # shortest_path_len, path_from_start_to_end = a_star_shortest_path(
        #     nodes, start_node.coords, end_node.coords,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )

        # print(f'Shortest path length from S -> E: {shortest_path_len}', end='\n\n')
        # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, path_from_start_to_end, heightcolor=True, arrowcolor='\033[38;5;39m'))


        ### Comparing algorithm outputs
        # for shortest_path_alg in [dijstras_shortest_path, a_star_shortest_path]:
            
        #     print(f'--- {shortest_path_alg.__name__}')

        #     shortest_path_len, path_from_start_to_end = shortest_path_alg(
        #         nodes, start_node.coords, end_node.coords,
        #         _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        #     )

        #     print(f'Shortest path length from S -> E: {shortest_path_len}', end='\n\n')
        #     print(generate_print_str_shortest_path(grid_width, grid_height, nodes, path_from_start_to_end, heightcolor=True, arrowcolor='\033[38;5;39m'))


        ### Generating algorithm comparison graphic
        shortest_paths = []

        # dshortest_path_len, dpath_from_start_to_end = dijstras_shortest_path(
        #     nodes, start_node.coords, end_node.coords,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )
        # print('D shortest path: ', dshortest_path_len)
        # shortest_paths.append(dpath_from_start_to_end)

        # # w/ default heuristic
        # ashortest_path_len, apath_from_start_to_end = a_star_shortest_path(
        #     nodes, start_node.coords, end_node.coords,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )
        # print('A shortest path: ', ashortest_path_len)
        # shortest_paths.append(apath_from_start_to_end)

        # comparing my three fscore formulations:
        for fscorefn in [default_f_of_n, height_then_f_of_n, height_dotprod_f_of_n]:
            ashortest_path_len, apath_from_start_to_end = a_star_shortest_path(
                nodes, start_node.coords, end_node.coords, fscore_fn=fscorefn,
                _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
            )
            print(f'A shortest path ({fscorefn.__name__}): ', ashortest_path_len)
            shortest_paths.append(apath_from_start_to_end)

            print(f'Shortest path length from S -> E: {ashortest_path_len}', end='\n\n')
            print(generate_print_str_shortest_path(grid_width, grid_height, nodes, apath_from_start_to_end, heightcolor=True, arrowcolor=WHITE))

        # print(generate_shortest_path_comparison_print_str(grid_width, grid_height, nodes, shortest_paths))

    if ANIMATION_GIF_MODE:
        screenshotter.close()