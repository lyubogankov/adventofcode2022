### Day 11: Monkey in the Middle

## Part One
After reading the problem description, I broke the problem into several layers:
- The game consists of multiple rounds.  I need to be able to simulate effects of N (1+) rounds on items/monkeys
- Each round consists of turns -- one turn per monkey, from 0 -> M
- Each monkey's turn consists of handling each item in its possession, from 0 -> M.I
- Each item handling consists of inspection (worry about item increases/decreases), and throwing to another monkey

**The `Monkey` object**

Has member variables with information from input text file:
- List of Item objects (more on this in a sec)
- Inspection-related: worry increase operation function / constant
- Throwing-related: divisibility constant, two potential targets
    - If the current item's worry level is divisible by monkey's divis constant, throw to first target; otherwise, to second.
- Number of items inspected, a counter that's incremented during per-round simulation

Additionally, I wrote a `__str__` method so that I could match the per-monkey printout shown in the problem description and input text file (for unit testing).  I did not write a `__repr__` method, because I could not find a way to properly print the worry-increase operation function name.

**The `Item` object**

The only per-item value to keep track of is its current worry level (quantified amount of worry viewer has for the item).

I defined several dunder methods for use with the per-monkey worry-increase operation: `__add__`, `__mul__`, and `__pow__`.  Additionally, I wrote `__str__` and `__repr__` methods for useful printouts.

**Reading from input file**

I used a verbose regular expression string with named groups to process the input file into `Monkey` objects.  I recently read about this method of using regex (Raymond Hettinger, StackOverFlow) and I like its readability.

```
    pattern = re.compile(r"""
          Monkey[ ](?P<monkey_idx>[\d]+):
        | Starting[ ]items:(?P<items_csv>[\d,\s]*)
        | Operation:[ ]new[ ]=[ ]old[ ](?P<operation>.+)
        | Test:[ ]divisible[ ]by[ ](?P<divis_const>\d+)
        | If[ ] true:[ ]throw[ ]to[ ]monkey[ ](?P<divis_throw_target>\d+)
        | If[ ]false:[ ]throw[ ]to[ ]monkey[ ](?P<nondivis_throw_target>\d+)
    """, re.VERBOSE)

    ...

    mo = pattern.fullmatch(line)

    ...

    if not mo:
        continue

    match mo.lastgroup:
        case 'monkey_idx': ...
        case 'items_csv':  ...
        ...
```

## Part Two

## Reflection