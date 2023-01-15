# Day 12: Hill Climbing Algorithm

## [Part one description](https://adventofcode.com/2022/day/12) (adventofcode.com)

**tl;dr**:

.


## Part One

### Problem Breakdown

A rectangular grid of letters is provided as an input.  Each letter, [*a*, *z*], represents the height of the grid square at those coordinates.

The task is to find the shortest path from the start square (labelled *S*, with height *a*) to the end square (labelled *E*, with height *z*).

There are two rules for traversing the tile grid:
1. Moving from tile A to tile B is allowed if $height_{B} - height_{A} \leq 1$.
2. From current tile (*x*, *y*), can access up to 4 other tiles: (*x* $\pm$ 1, *y*) and (*x*, *y* $\pm$ 1).


### Solution

I briefly pondered writing my own algorithm, but abandoned that when I remembered learning about Dijkstra's shortest-path algorithm in a college data structures course.  Its [Wikipedia page](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) the contains a pseudocode description, which I used as the foundation for my solution.

#### Parsing input into graph

In order to use Dijkstra's algorithm for this problem, I needed to turn the input text file into a graph of vertices (nodes) and edges.  At first I used undirected edges, but realized that the height-based traversal rule meant that tile A might be reachable from B without the converse being true (B reachable from A) - this occurs when $height_{B} - height_{A} > 1$.

I used `namedtuples` to make two data structures - `Nodes` and `DirectedEdges`.  This made the data structure code simpler but resulted in more complicated print routines.  I was able to modify `Nodes` because `tuples` can contain mutable containers, such as `lists`!

Additionally, to validate my process, I wrote a function to visualize the directed graph.  The full input was too large to display within the command prompt, so here is a printout of the directed graph for the problem description example!

![Command-prompt printout of directed graph representation of problem example](../media/day12/example_directed_graph.png)

#### Trying to predict what might change for Part Two

Based on the title "Hill Climbing Algorithm" and the description's mention of climbing gear, I wondered whether Part 2 would feature our protagonist finding an abandoned set of climbing gear mid-hike and would gain the ability to climb hills.  If so, I'd need to change the traversal rules used to parse the input text file into a directed graph!  I represented the traversal rules as an anonymous / `lambda` function and passed it into the parsing routine:

```python
part_one_edge_rule_fn = lambda curr_node, adj_node: \
                            ord(adj_node.height) - ord(curr_node.height) <= 1

def parse_input_into_graph(inputfile, edge_rule_fn)
    ...

start_node, end_node, nodes = parse_input_into_graph(
    inputfile,
    edge_rule_fn=part_one_edge_rule_fn
)
```
#### My implementation of Dijkstra's algorithm

I augmented the pseudocode to not only provide me the shortest path between desired nodes, but also .

I made two implementation errors during
- shortest path from source error
- not properly choosing next node

Solution printout -- show the arrows!

Here is the algorithm in action!  Making this GIF took a very long time on my laptop, but it was fun to pick out the color scheme.  I learned about 



## Part Two


### Problem Breakdown


### Solution



## Bonus 1 - Using an off-the-shelf implementation of Dijkstra's algorithm

Describe the module I used, how I had to change my program to use it

**Compare my solution with the off-the-shelf version, time how long each one takes for part one and part two!**



## Bonus 2 - Implementing A* algorithm