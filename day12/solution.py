# std library
import copy
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
        savefolder='day12',
        framefolder='longest_path',
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

### input file -> data structure --------------------------------------------------------------------------------------
Node = namedtuple('Node', ['height', 'coords', 'connections', 'shortest_path_from_start', 'flags'])
def initialize_node(height, coords):
    return Node(height=height, coords=coords, connections=set(), shortest_path_from_start=[], flags={'pruned': False})
# Edge = namedtuple('Edge', ['weight', 'node_one_coords', 'node_two_coords'])  # undirected edge
DirectedEdge = namedtuple('DirectedEdge', ['weight', 'node_to_coords'])  # edges belong to nodes, so the "from" is the node to which the edge belongs

def parse_input_into_graph(inputfile, edge_rule_fn):

    with open(inputfile, 'r') as f:
        lines = list(f)

    start_node = None
    end_node = None
    nodes = {}

    # lines from bottom -> top, read left-to-right
    for y, row in enumerate(reversed(lines)):
        for x, node_height in enumerate(row.rstrip()):  # looping over each character in the row str
            if node_height == 'S':
                node = start_node = initialize_node(height='a',  coords=(x, y))
            elif node_height == 'E':
                node = end_node   = initialize_node(height='z',  coords=(x, y))
            else:
                node              = initialize_node(node_height, coords=(x, y))

            # this is how I'm looking up the nodes
            nodes[(x, y)] = node

            # form connections between this node and prior nodes, if applicable
                                             # left neighbor,     bottom neighbor
            for condition, neighborcoords in [(x > 0, (x-1, y)), (y > 0, (x, y-1))]:
                if not condition:
                    continue
                neighbor = nodes[neighborcoords]  # either to the left, or below current node
                if edge_rule_fn(node, neighbor):
                    edge = DirectedEdge(
                        weight=1,
                        node_to_coords=neighbor.coords
                    )
                    node.connections.add(edge)
                if edge_rule_fn(neighbor, node):
                    edge = DirectedEdge(
                        weight=1,
                        node_to_coords=node.coords
                    )
                    neighbor.connections.add(edge)

    return start_node, end_node, nodes, x+1, y+1

### printing ----------------------------------------------------------------------------------------------------------
def generate_print_str_graph(grid_width, grid_height, nodes, start_coords=None, end_coords=None, connected=False, heightcolors=False, showpruned=False):

    WIDTH_BETWEEN_CHARS_X = 1
    WIDTH_BETWEEN_CHARS_Y = 1
    ARROW_COLOR = '\033[38;5;39m'
    print_str = ''

    for y in range(grid_height):  # rows
    
        row_str = ''
        for x in range(grid_width):  # cols
            curr_node = nodes[(x, y)]
            
            # check whether the node to the left is connected to current node
            if x > 0 and connected:
                left_neighbor = nodes[(x-1, y)]
                neighb_to_node = DirectedEdge(weight=1, node_to_coords=    curr_node.coords)
                node_to_neighb = DirectedEdge(weight=1, node_to_coords=left_neighbor.coords)

                right_conn = neighb_to_node in left_neighbor.connections
                left_conn = node_to_neighb in curr_node.connections
                if left_conn or right_conn:
                    row_str += ARROW_COLOR
                    if left_conn and right_conn: row_str += '-'
                    elif left_conn:              row_str += '<'
                    elif right_conn:             row_str += '>'
                    row_str += RESET
                else:
                    row_str += ' '*(WIDTH_BETWEEN_CHARS_X)

            if (x, y) == start_coords:
                row_str += 'S'
            elif (x, y) == end_coords:
                row_str += 'E'
            elif showpruned and curr_node.flags['pruned']:
                row_str += f'{BLACK}{curr_node.height}{RESET}'
            elif heightcolors:
                row_str += f'{height_color_map[curr_node.height]}{curr_node.height}{RESET}'
            else:
                row_str += curr_node.height

        # if applicable, check last two lines for any connections
        if y > 0 and connected:
            between_rows_str = ''
            for x in range(grid_width):
                curr_node = nodes[(x, y)]
                bottom_neighbor = nodes[(x, y-1)]
                neighb_to_node = DirectedEdge(weight=1, node_to_coords=      curr_node.coords)
                node_to_neighb = DirectedEdge(weight=1, node_to_coords=bottom_neighbor.coords)

                top_conn = neighb_to_node in bottom_neighbor.connections
                bot_conn = node_to_neighb in curr_node.connections
                if top_conn or bot_conn:
                    between_rows_str += ARROW_COLOR
                    if top_conn and bot_conn: between_rows_str += '|'
                    elif top_conn:            between_rows_str += '^'
                    elif bot_conn:            between_rows_str += 'v'
                    between_rows_str += RESET
                else:
                    between_rows_str += ' '
                
                if x < grid_width - 1:
                    between_rows_str += ' '*WIDTH_BETWEEN_CHARS_X
            print_str = between_rows_str + '\n' + print_str
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

def generate_annotated_print_str(grid_width, grid_height, nodes, shortest_path_coords=[], unvisited_set=set(), current_coords=None, heightcolor=False, arrowcolor=WHITE):

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
                if arrowcolor is not None:
                    row_str += f'{arrowcolor}{shortest_path_node_arrows[(x, y)]}{RESET}'
                else:
                    row_str += shortest_path_node_arrows[(x, y)]
            elif shortest_path_coords and (x, y) == shortest_path_coords[-1]:
                row_str += 'E'
            # coloring as the alg runs to visualize what we've already looked at
            elif (x, y) == current_coords:
                color = GREEN
            elif unvisited_set:
                color = BLACK if (x, y) in unvisited_set else height_color_map[height]
            elif nodes[(x, y)].flags['pruned']:
                color = BLACK
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

def generate_astar_print_str_during_sim(grid_width, grid_height, nodes, exploration_boundary, visited_coords, heightcolor):
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
        # '\033[38;5;39m',  # DeepSkyBlue1
        '\033[38;5;126m',  # magenta
        # RED,
        '\033[38;5;51m',  # Cyan
        '\033[38;5;11m',  # Yellow
        '\033[38;5;10m',  # Lime
    ]
    # adding bg color
    bgcolor = '\033[48;5;245m'
    for i in range(len(shortest_path_colors)):
        shortest_path_colors[i] = bgcolor + shortest_path_colors[i]

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

## Dijkstra's ---------------------------------------------------------------------------------------------------------
def dijkstras_shortest_path(nodes, start_coords, end_coords, print_stats=False, _animate=False, screenshotter=None, return_unvisited=False):
    '''
    Arguments
        nodes: dictionary
            Maps coordinates, tuple of two integers (x, y), to Node namedtuples
        start_coords: 2-tuple of integers
            (x, y) coordinates of start node
        end_coords: 2-tuple of integers
            (x, y) coordinates of end node

    Optional Arguments
        print_stats: bool
            On return, print out nodes/edges processed
        _animate: bool
            Create animation of algorithm running
        screenshotter: mss.mss()
            Take screenshots (for animation)
        return_unvisited: bool
            Instead of returning shortest path + length, return set of unvisited coords
    
    Returns
        shortest_path_len: int
            Number of steps in the shortest path  (infinity if end is unreachable from start)
        shortest_path: list of Nodes
            From start -> end, each node visited.  Can be used to print the path.  (empty list if end unreachable from start)
    
        OR
        unvisited_set: set of tuples of integers
            (x, y) coordinates of all unvisited Nodes

    From https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

    first try my own dijkstra implementation, then try this?
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.dijkstra.html

    shortest path: 380
    Num edges processed: 7974
    Num nodes visited:   4549/4633
    '''
    ## Setup
    grid_height = max(y+1 for (x, y) in nodes.keys())
    grid_width  = max(x+1 for (x, y) in nodes.keys())

    edges_processed = 0
    nodes_processed = 0

    # 1. Create set of unvisited nodes.
    unvisited_coords = set(nodes.keys())

    # 2. Create tentative distance tracker
    # https://stackoverflow.com/questions/7781260/how-can-i-represent-an-infinite-number-in-python
    tentative_distance_from_start = {coords : math.inf for coords in unvisited_coords}
    tentative_distance_from_start[start_coords] = 0

    ## Run Dijkstra's alg!  Keep running until we've visited all *reachable* nodes.
    current_coords = start_coords
    while len([coords for coords in unvisited_coords if tentative_distance_from_start[coords] < math.inf]) > 0:

        # 3. For current node, look at all of its unvisited edges and calculate distance from start -> neighbor.
        for edge in nodes[current_coords].connections:

            if edge.node_to_coords not in unvisited_coords:
                continue
            edges_processed += 1

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
        nodes_processed += 1  # processed = looked at all neighbors

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

        # 5. Check for termination (if return_unvisited, we want to visit the entire graph)
        if current_coords == end_coords and not return_unvisited:
            break

        # 6. Select next node!
        if len(unvisited_coords) > 0:
            current_coords = min(unvisited_coords, key=lambda c: tentative_distance_from_start[c])

    # terminate after looking at the whole graph
    if return_unvisited:
        return unvisited_coords
    if print_stats:
        print('Num edges processed: ', edges_processed)
        print('Num nodes processed: ', nodes_processed)
        print('Num nodes visited: ', len(nodes) - len(unvisited_coords))
    if end_coords in unvisited_coords:
        return math.inf, []
    shortest_path_len = tentative_distance_from_start[end_coords]
    path_from_start_to_end = nodes[end_coords].shortest_path_from_start + [end_coords]
    return shortest_path_len, path_from_start_to_end

def dijkstras_longest_path(nodes, start_coords, end_coords):
    '''
    DID NOT WORK
        On the wiki page for Dijkstra's algorithm is a discussion of types of graphs the alg can handle.
        Notably, it cannot handle graphs with negative edge weights because it'd get stuck in a cycle.
        The longest path problem is simliar to shortest path with negative weights.
    '''
    edges_processed = 0
    nodes_processed = 0

    camefrom = {}

    # 1. Create set of unvisited nodes.
    unvisited_coords = set(nodes.keys())

    # 2. Create tentative distance tracker
    # CHANGE: math.inf to -math.inf
    tentative_distance_from_start = {coords : -math.inf for coords in unvisited_coords}  
    tentative_distance_from_start[start_coords] = 0

    ## Run Dijkstra's alg!
    current_coords = start_coords
    while len(unvisited_coords) > 0:
        print(f'Visiting new node: {current_coords}')

        # 3. For current node, look at all of its unvisited edges and calculate distance from start -> neighbor.
        for edge in nodes[current_coords].connections:
            neighb_coords = edge.node_to_coords
            print(f'\t>{neighb_coords}')

            edges_processed += 1

            start_to_neighb_dist_thru_curr_node = tentative_distance_from_start[current_coords] + edge.weight
            start_to_neighb_longest_known_path  = tentative_distance_from_start[neighb_coords]

            # CHANGE: < to >
            # CHANGE: only update if we're not forming a cycle
            if start_to_neighb_dist_thru_curr_node > start_to_neighb_longest_known_path and \
                    neighb_coords not in reconstruct_path(camefrom, current_coords):
                tentative_distance_from_start[neighb_coords] = start_to_neighb_dist_thru_curr_node
                camefrom[neighb_coords] = current_coords
                print(f'\t\told: {start_to_neighb_longest_known_path} vs new: {start_to_neighb_dist_thru_curr_node}')

        # 4. Current node is done!  Remove it from unvisited set.
        unvisited_coords.remove(current_coords)
        nodes_processed += 1

        # 5. Select next node!
        # CHANGE: now looking for max instead of min
        if len(unvisited_coords) > 0:
            current_coords = max(unvisited_coords, key=lambda coords: tentative_distance_from_start[coords])
            # current_coords = min(unvisited_coords, key=lambda c: tentative_distance_from_start[c] if tentative_distance_from_start[c] >= 0 else math.inf)

    # terminate after looking at the whole graph
    print('Num edges processed: ', edges_processed)
    print('Num nodes processed: ', nodes_processed)
    print('Num nodes visited: ', len(nodes) - len(unvisited_coords))

    longest_path_len = tentative_distance_from_start[end_coords]
    longest_path = reconstruct_path(camefrom, end_coords)
    return longest_path_len, longest_path

## A* -----------------------------------------------------------------------------------------------------------------
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

def to_vector(node_from, node_to):
    return [node_to.coords[i] - node_from.coords[i] for i in range(2)]  # i=0=x, i=1=y

def normalized_dotprod(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def default_f_of_n(*, g_of_n, h_of_n, **kwargs):
    '''f(n) = g(n) + h(n)
    Rationale:
    - g(n) = shortest known path from start -> current node
    - h(n, end) = heuristic from current node -> end.  I'm using manhattan distance.
    Therefore minimizing f(n) means choosing node that has shortest path from start to end 
      based on heuristic / best guess.

    Reported shortest path 380
    Num edges processed: 16913
    Num nodes visited:    4538/4633  (11 fewer than Dijkstra)
    '''
    return g_of_n + h_of_n
def height_then_f_of_n(*, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''Rationale:
    If we prioritize height over raw fscore, it should get to end faster
      bc it doesn't spend time exploring the 'a' pits.
    We're trying to minimize the height difference between neighbor and end,
      so going downhill is penalized.

    Reported shortest path 380
    Num edges processed: 9916
    Num nodes visited:    3293/4633 (1245 fewer than Dijkstra)
    '''
    return (
        ord(end_node.height) - ord(neighbor_node.height),  # height difference
        g_of_n + h_of_n                                   # original fscore
    )
def height_fofn_hofn(*, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''
    Reported shortest path: 380
    Num edges processed: 9908  (8 fewer than above)
    Num nodes visited:   3286  (7 fewer than above)
    '''
    return (
        ord(end_node.height) - ord(neighbor_node.height),  # height difference
        g_of_n + h_of_n,                                   # original fscore
        h_of_n                                             # tie-breaker for height/fscore
    )
def height_dotprod_f_of_n(*, current_node, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''
    Rationale:
    To break ties between height diff, trying to move towards end node.
      Accomplishing this w/ dot product, minimizing the dot prod between
      current -> end vector and neighbor -> end vector = want them to be parallel.

    Reported shortest path 510
    Num edges processed: 31033
    Num nodes visited:    4131/4633

    I originally thought minimizing dot product would mean obtaining dot prod = 0 aka parallel vectors.
    However, normalized dot product yields a value [-1, 1] so really I am optimizing for away from end...

    I could do -1*dotprod though, that'd prioritize going towards (-1*1) rather than away (-1*-1)
    '''
    height_diff = ord(end_node.height) - ord(current_node.height)
    estimated_dist_to_end = g_of_n + h_of_n
    if current_node == end_node:
        return (height_diff, 0, estimated_dist_to_end)
    dotprod = normalized_dotprod(to_vector(current_node, neighbor_node), to_vector(current_node, end_node))
    return (height_diff, dotprod, estimated_dist_to_end)
def height_f_of_n_dotprod(*, current_node, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''
    Reported shortest path 380
    Num edges processed: 11108
    Num nodes visited:    3675/4366

    This one worked *in spite of* the dotprod, not because of it.
    '''
    height_diff, dotprod, f_of_n = height_dotprod_f_of_n(current_node=current_node, neighbor_node=neighbor_node, end_node=end_node, g_of_n=g_of_n, h_of_n=h_of_n)
    return (height_diff, f_of_n, dotprod)
def height_f_of_n_theta(*, current_node, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''Rationale:
    cos(theta) can go from 0 -> 180 degrees, so minimizing this value points us towards the end!
    Update - this actually yeielded the same results as -1*normalized dotprod :o

    Shortest path: 380
    Num edges processed: 11252
    Num nodes visited:   3672/4633
    '''
    height_diff, dotprod, f_of_n = height_dotprod_f_of_n(current_node=current_node, neighbor_node=neighbor_node, end_node=end_node, g_of_n=g_of_n, h_of_n=h_of_n)
    return (height_diff, f_of_n, math.acos(dotprod))
def height_negdotprod_f_of_n(*, current_node, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''
    Shortest path: 388 ***
    Num edges processed: 9593
    Num nodes visited:   3166/4633
    '''
    height_diff, dotprod, f_of_n = height_dotprod_f_of_n(current_node=current_node, neighbor_node=neighbor_node, end_node=end_node, g_of_n=g_of_n, h_of_n=h_of_n)
    return (height_diff, -1*dotprod, f_of_n)
def height_f_of_n_negdotprod(*, current_node, neighbor_node, end_node, g_of_n, h_of_n, **kwargs):
    '''
    Shortest path: 380
    Num edges processed: 11252
    Num nodes visited:    3672/4633
    '''
    height_diff, dotprod, f_of_n = height_dotprod_f_of_n(current_node=current_node, neighbor_node=neighbor_node, end_node=end_node, g_of_n=g_of_n, h_of_n=h_of_n)
    return (height_diff, f_of_n, -1*dotprod)

def a_star_shortest_path(nodes, start, end, heuristic_fn=manhattan_distance, fscore_fn=default_f_of_n, print_stats=True, revisiting_allowed=True, _animate=False, screenshotter=None):
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

    edges_processed = 0
    nodes_processed = 0

    # heuristic consistency check
    if not revisiting_allowed:
        visited_set = set()

    ## Running the search
    while len(exploration_boundary) > 0:
        (_, _, current) = heapq.heappop(exploration_boundary)
        exploration_boundary_set.remove(current)
        # for heuristic consistency check
        if not revisiting_allowed:
            visited_set.add(current)

        if current == end:
            if print_stats:
                print('Num edges processed: ', edges_processed)
                print('Num nodes processed: ', nodes_processed)
                print(f'Num nodes visited: ', len([x for x in shortest_known_path_from_start.values() if x < math.inf]))
            shortest_path = reconstruct_path(camefrom, end)
            # the puzzle want the number of steps from start -> end, which is one less than number of nodes in shortest path
            return len(shortest_path) - 1, shortest_path

        # examine all neighbors
        for edge in nodes[current].connections:
            
            # heuristic consistency check
            if not revisiting_allowed and edge.node_to_coords in visited_set:
                continue
            edges_processed += 1

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
                    current_node=nodes[current],
                    neighbor_node=nodes[neighbor]
                )
                if neighbor not in exploration_boundary_set:
                    exploration_boundary_set.add(neighbor)
                    # since this is a minheap -- prioritize later-added nodes over earlier-added nodes in case of fscore tie
                    heapq.heappush(exploration_boundary, (fscore[neighbor], -1*len(exploration_boundary), neighbor))
        nodes_processed += 1  # processed = looked at all neighbors

        if _animate:
            os.system('clear')  # linux only
            print(generate_astar_print_str_during_sim(
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

### puzzle ------------------------------------------------------------------------------------------------------------
part_one_edge_rule_fn = lambda curr_node, adj_node: ord(adj_node.height) - ord(curr_node.height) <= 1

def part_two(nodes, end_coords):

    candidate_a_tiles = []
    for node in nodes.values():

        # we need to start at an 'a'
        if node.height != 'a':
            continue

        # look through all edges -- does it point to a 'b'?
        # shortest possible path up would be a -> b -> c -> ... -> z
        for edge in node.connections:
            neighbor = nodes[edge.node_to_coords]
            if neighbor.height == 'b':
                candidate_a_tiles.append(node.coords)
                break
    
    # now, find the shortest path among the candidate a tiles:
    results = []
    for a_tile_coords in candidate_a_tiles:
        pathlen, steps = a_star_shortest_path(
            nodes=nodes,
            start=a_tile_coords,
            end=end_coords,
            fscore_fn=height_fofn_hofn,
            print_stats=False
        )
        results.append((pathlen, steps, a_tile_coords))

    results.sort(key=lambda x: x[0])
    # for len, _, coords in results:
    #     print(len, coords)
    return results[0]

## Longest Path -------------------------------------------------------------------------------------------------------
def prune_node(grid_width, grid_height, nodes, coords_to_prune):
    '''Remove this node from connection sets of all potential neighbor nodes, and clear its connections.'''
    
    # remove node from neihbors' connections, if needed
    (x, y) = nodes[coords_to_prune].coords
    if x > 0:               nodes[(x-1, y  )].connections.discard(DirectedEdge(1, coords_to_prune)) # S neighbor
    if y > 0:               nodes[(x,   y-1)].connections.discard(DirectedEdge(1, coords_to_prune)) # W
    if x < grid_width  - 1: nodes[(x+1, y  )].connections.discard(DirectedEdge(1, coords_to_prune)) # N
    if y < grid_height - 1: nodes[(x,   y+1)].connections.discard(DirectedEdge(1, coords_to_prune)) # E

    # delete all outgoing connections from this node (empty the set)
    nodes[coords_to_prune].connections.clear()
    nodes[coords_to_prune].flags['pruned'] = True

def find_connected_nodes(nodes, start_coords, bidir):
    '''Traverse graph and find all nodes that are (bidirectionally) connected to start.
    Beginning with start node, only look at nodes that are (bidirectionally) connected to current node.
    '''
    visited_coords = set()
    exploration_boundary = {start_coords, }

    while len(exploration_boundary) > 0:
        current_coords = exploration_boundary.pop()

        # check -- is the neighbor node (bidirectionally) connected to current node?
        for edge in nodes[current_coords].connections:
            neighb_coords = edge.node_to_coords
            if neighb_coords in visited_coords:
                continue
            if not bidir or DirectedEdge(weight=1, node_to_coords=current_coords) in nodes[neighb_coords].connections:
                exploration_boundary.add(neighb_coords)
        visited_coords.add(current_coords)
    return visited_coords

def prune_graph(grid_width, grid_height, nodes, start_coords, end_coords, prune_dead_ends, _animate=False, screenshotter=None):
    '''Prunes `nodes` graph in-place.  Remove nodes unreachable from start, that cannot reach end.'''

    def animate(iteration):
        os.system('clear')  # linux only
        print(generate_annotated_print_str(grid_width, grid_height, nodes, heightcolor=True,))
        time.sleep(0.3)
        # take screenshot
        if ANIMATION_GIF_MODE:
            screenshot.screenshot(screenshotter, params, sim_iteration=iteration)

    unreachable_from_start = dijkstras_shortest_path(nodes, start_coords=start_coords, end_coords=end_coords, return_unvisited=True)
    for coords in unreachable_from_start:
        prune_node(grid_width, grid_height, nodes, coords)
    if _animate: animate(iteration=0)
    
    visited_coords = set()
    unreachable_subgraph_count = 0
    for coords in nodes:
        if coords in unreachable_from_start or coords in visited_coords:
            continue
        # try to get from current coords -> end
        path_len, _ = dijkstras_shortest_path(nodes, start_coords=coords, end_coords=end_coords)
        # can be reached -- all nodes bidirectionally connected to this one can ALSO reach end
        if path_len < math.inf:
            for bidir_connected_coords in find_connected_nodes(nodes, coords, bidir=True):
                if bidir_connected_coords in visited_coords:
                    continue
                visited_coords.add(bidir_connected_coords)
                # if this is a dead-end node, prune it.  Need to then re-evaluate the node to which it was connected (and so on).
                if prune_dead_ends and len(nodes[bidir_connected_coords].connections) == 1:
                    current_coords = bidir_connected_coords
                    while len(nodes[current_coords].connections) == 1:
                        neighbor_coords = list(nodes[current_coords].connections)[0].node_to_coords
                        prune_node(grid_width, grid_height, nodes, current_coords)
                        current_coords = neighbor_coords
                        visited_coords.add(current_coords)
            continue
        # otherwise, can't -- prune this node and all the nodes it's connected to
        for unreachable_coords in find_connected_nodes(nodes, coords, bidir=False):
            visited_coords.add(unreachable_coords)
            prune_node(grid_width, grid_height, nodes, unreachable_coords)
        unreachable_subgraph_count += 1
        if _animate: animate(iteration=unreachable_subgraph_count)

def prune_unreachable_nodes(grid_width, grid_height, nodes, start_coords, end_coords):
    prune_graph(grid_width, gridh_height, nodes, start_coords, end_coords, prune_dead_ends=False)

def prune_dead_end_nodes(grid_width, grid_height, nodes, start_coords, end_coords):
    prune_graph(grid_width, gridh_height, nodes, start_coords, end_coords, prune_dead_ends=True )

def find_all_paths_from_start_to_end(nodes, start_coords, end_coords, _print=False):
    '''Find all possible paths from start -> end.

    Before running this function, strongly recommend running:
        1) `prune_graph(..., prune_dead_ends=False)`
        2) `prune_graph(..., prune_dead_ends=True )`
    '''
    explored_paths = [[start_coords]]
    paths_from_start_to_end = []
    
    while explored_paths != []:
        path_from_start_to_current = explored_paths.pop()
        current_coords = path_from_start_to_current[-1]
        if _print:
            print(f'{current_coords}                    {path_from_start_to_current}')
    
        for edge in nodes[current_coords].connections:
            neighbor_coords = edge.node_to_coords
            if _print:
                print(f'\t{neighbor_coords}', end='')
            
            if neighbor_coords in path_from_start_to_current or neighbor_coords == end_coords:
                if neighbor_coords == end_coords:
                    paths_from_start_to_end.append(copy.copy(path_from_start_to_current) + [neighbor_coords])
                if _print:
                    print('\n', end='')
                continue

            explored_paths.append(copy.copy(path_from_start_to_current) + [neighbor_coords])
            if _print:
                print(' - append')
    paths_from_start_to_end.sort(key=len, reverse=True)
    return paths_from_start_to_end

def longest_path(nodes, start_coords, end_coords, _print=False):
    '''Find longest path from start -> end.
    
    Before running this function, strongly recommend running:
        1) `prune_graph(..., prune_dead_ends=False)`
        2) `prune_graph(..., prune_dead_ends=True )`
    '''
    paths_from_start_to_end = find_all_paths_from_start_to_end(nodes, start_coords, end_coords, _print)
    longest_path = paths_from_start_to_end[0]
    return len(longest_path), longest_path

# ---------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    
    if ANIMATION_GIF_MODE:
        screenshotter = screenshot.mss.mss()

    for inputfile in ['input.txt']: # ['example.txt', 'input.txt']:
        example = inputfile == 'example.txt'
        print('\n---', inputfile)

        start_node, end_node, nodes, grid_width, grid_height = parse_input_into_graph(
            inputfile=inputfile,
            # for part one - "if height diff is higher than +1, can't traverse"
            edge_rule_fn=part_one_edge_rule_fn
        )
        # print out the input heightmap
        print(generate_print_str_graph(
            grid_width,
            grid_height,
            nodes,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=False,
            heightcolors=True,
        ))
        print('\n\n')
        # print out the input heightmap as a directed graph
        print(generate_print_str_graph(
            grid_width,
            grid_height,
            nodes,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=True,
            heightcolors=True,
        ))
        print('\n\n')

        # pruning step 1 -- remove nodes that can't reach end
        prune_graph(grid_width, grid_height, nodes, start_node.coords, end_node.coords, prune_dead_ends=False)
        print(generate_print_str_graph(
            grid_width,
            grid_height,
            nodes,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=True,
            heightcolors=True,
            showpruned=True,
        ))
        print('\n\n')
        # pruning step 2 -- remove dead-end nodes
        prune_graph(grid_width, grid_height, nodes, start_node.coords, end_node.coords, prune_dead_ends=True )
        print(generate_print_str_graph(
            grid_width,
            grid_height,
            nodes,
            start_coords=start_node.coords,
            end_coords=end_node.coords,
            connected=True,
            heightcolors=True,
            showpruned=True,
        ))
        print('\n\n')

        ##### PART TWO
        # best_path_len, best_path, coords = part_two(nodes, end_node.coords)
        # print(f'Shortest overall path: {best_path_len} from coords {coords}')
        # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, best_path, heightcolor=True, arrowcolor='\033[48;5;245m\033[38;5;126m'))

        ##### PART ONE

        ### Run a single algorithm and print out the results

        # # Dijkstra's alg
        # dshortest_path_len, dpath_from_start_to_end = dijkstras_shortest_path(
        #     nodes, start_node.coords, end_node.coords,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )
        # print(f'Shortest path length from S -> E: {dshortest_path_len}', end='\n\n')
        # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, dpath_from_start_to_end, heightcolor=True, arrowcolor='\033[38;5;39m'))

        # # A*
        # ashortest_path_len, apath_from_start_to_end = a_star_shortest_path(
        #     nodes, start_node.coords, end_node.coords, fscore_fn=height_fofn_hofn,
        #     _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        # )
        # print('A shortest path: ', ashortest_path_len)
        # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, apath_from_start_to_end, heightcolor=True, arrowcolor='\033[38;5;39m'))


        ### Generating algorithm comparison graphic
        # shortest_paths = []

        # _, dpath_from_start_to_end = dijkstras_shortest_path(nodes, start_node.coords, end_node.coords)
        # shortest_paths.append(dpath_from_start_to_end)
        
        # _, apath_from_start_to_end = a_star_shortest_path(nodes, start_node.coords, end_node.coords, fscore_fn=height_f_of_n_theta)
        # shortest_paths.append(apath_from_start_to_end)

        # _, apath_from_start_to_end = a_star_shortest_path(nodes, start_node.coords, end_node.coords, fscore_fn=height_f_of_n_negdotprod)
        # shortest_paths.append(apath_from_start_to_end)

        # comparing my fscore formulations:
        # for fscorefn in [default_f_of_n, height_then_f_of_n, height_fofn_hofn,
        #                  height_dotprod_f_of_n, height_f_of_n_dotprod,
        #                  height_f_of_n_theta,
        #                  height_negdotprod_f_of_n, height_f_of_n_negdotprod]:
        #     ashortest_path_len, apath_from_start_to_end = a_star_shortest_path(
        #         nodes, start_node.coords, end_node.coords, fscore_fn=fscorefn,
        #         _animate=False, screenshotter=screenshotter if ANIMATION_GIF_MODE else None
        #     )
        #     print(f'A shortest path ({fscorefn.__name__}): ', ashortest_path_len, end='\n\n')
        #     # shortest_paths.append(apath_from_start_to_end)
        #     # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, apath_from_start_to_end, heightcolor=True, arrowcolor='\033[48;5;245m\033[38;5;126m'))

        # print(generate_shortest_path_comparison_print_str(grid_width, grid_height, nodes, shortest_paths))

        
        # ### Dijkstra's longest path -- doesn't work
        # dlongest_path_len, dpath_from_start_to_end = dijkstras_longest_path(nodes, start_node.coords, end_node.coords)


        # ### My longest path

        # # testing graph pruning
        # prune_graph(grid_width, grid_height, nodes, start_node.coords, end_node.coords, _animate=True, screenshotter=screenshotter)
    
        # longest_path_len, path_from_start_to_end = longest_path(nodes, start_node.coords, end_node.coords)
        # print(f'Longest path length from S -> E: {longest_path_len}', end='\n\n')
        # print(generate_print_str_shortest_path(grid_width, grid_height, nodes, path_from_start_to_end, heightcolor=True, arrowcolor='\033[38;5;39m'))

        # all_paths = find_all_paths_from_start_to_end(nodes, start_node.coords, end_node.coords)
        # for i, path in enumerate(all_paths):
        #     print(f'Path length from S -> E: {len(path)}  [{i+1} / {len(all_paths)}]', end='\n\n')
        #     print(generate_print_str_shortest_path(grid_width, grid_height, nodes, path, heightcolor=True, arrowcolor='\033[38;5;39m'))

    if ANIMATION_GIF_MODE:
        screenshotter.close()