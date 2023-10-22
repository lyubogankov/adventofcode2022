# Day 13: Distress Signal

## [Part one description](https://adventofcode.com/2022/day/13) (adventofcode.com)

**tl;dr**:

[Recursion vs iteration](#input-file-parsing), 


## Part One

### Problem Breakdown

The input consists of pairs of lists ('packets'), each of which contain either integers or lists with zero or more elements.  The structure can nest to an arbitrary depth.

First, I need to determine whether the two packets are "in order" according to a set of rules.  The first instance that determines (in)correctness halts the comparison process.
- If comparing two lists, perform element-wise comparison and stop when shorter list is exhausted.
    - If any pair of elements is correctly or incorrectly ordered, that is the overall order.
    - Else, if left list was exhausted first, correct order
    - Else, if right list was exhausted first, incorrect order
    - Otherwise indeterminate, keep parsing
- If comparing two integers:
    - left < right: correct
    - right < left: incorrect
    - left == right: indeterminate, keep parsing
- If integer vs list: turn integer into list with integer as sole element and re-try comparison

Then, I need to determine which packet-pair indices (1-indexed) are in the correct order, and find the sum of those indices!

### Solution

#### Input file parsing

When thinking through the solution I didn't spend much time on parsing the input file, but this turned out to be an equally tricky challenge!

I implemented file parsing iteratively and recursively and unit tested both methods using both the example and puzzle input text files!  Both methods use a stack - the iterative approach uses a `list` as a stack, while the recursive method uses Python's function-call stack.

The iterative approach turned out to be more succinct;  here it is, without the print statements:

```python
def parse_line_iteratively(line, _print=False, _printchar=False):
    parsed_line = []
    sublist_stack = [parsed_line]
    current_str = ''
    # skip first outermost bracket
    for c in line[1:]:
        if c == '[':
            innerlist = []
            sublist_stack[-1].append(innerlist)  # attach to parsed_list
            sublist_stack.append(innerlist)      # for adding more elements
        elif c == ',' or c == ']':
            if current_str:
                sublist_stack[-1].append(int(current_str))
                current_str = ''
            if c == ']':
                sublist_stack.pop()
        else:
            current_str += c
    return parsed_line
```

#### Determining packet order correctness

It was fun writing a recursive function to solve the order correctness comparison!  My function returns both the order determination (`ORDER_CORRECT`, `ORDER_INCORRECT`, `ORDER_INDETERMINATE`) as well as a string showing the step-by-step comparisons, formatted just like the example (to facilitate unit testing)!


## Part Two

### Problem Breakdown

Instead of looking at the packets in pairs to determine whether their ordering is correct, the task now is to:
1. Add two special packets into our overall packet list, `[[2]]` and `[[6]]`
2. Sort the overall packet list
3. Compute the "decoder key" by multiplying the 1-based index of the two special packets from the sorted list

### Solution

#### Sorting

At first, I thought I'd have to write my own sorting algorithm to support comparison between packets using the logic from Part One.  However, I realized that leverage Python's data model would allow me to write a small `Packet` class that implements rich comparison operators (`<`, `<=`, `==`, `>=`, `>`).  Once I implemented this class, I could sort a `list` of `Packets` by using Python's build-in sorting algorithm and neatly solve the problem!