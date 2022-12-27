# std library
import re
# third-party
import numpy as np


### input file parsing / internal representation
WORRY_REDUCT_FACTOR = 3

class Item:
    OWNERIDX = 0
    QUEUEIDX = 1
    WORRYLVL = 2

class Monkey:
    def __init__(self, num_items_held, operation_fn_str, operation_const, divis_const, divis_throw_target, nondivis_throw_target):
        self.num_items_held        = num_items_held
        self.operation_fn_str      = operation_fn_str
        self.operation_const       = operation_const
        self.divis_const           = divis_const
        self.divis_throw_target    = divis_throw_target
        self.nondivis_throw_target = nondivis_throw_target

        self.items_inspected       = 0  # counter for part one

    def __repr__(self):
        reprstr  = f"Monkey(operation_fn_str='{self.operation_fn_str}', "
        reprstr += f"operation_const={self.operation_const}, "
        reprstr += f"divis_const={self.divis_const}, "
        reprstr += f"divis_throw_target={self.divis_throw_target}, "
        reprstr += f"nondivis_throw_target={self.nondivis_throw_target})"
        return reprstr

def parse_input_file_into_items_and_monkey_list(inputfile, _print=False):
    '''Parse input file formatted per specefication in problem description into items array and monkeys list.
    '''

    with open(inputfile, 'r') as f:
        lines = list(f)

    pattern = re.compile(r"""
          Monkey[ ](?P<monkey_idx>[\d]+):
        | Starting[ ]items:(?P<items_csv>[\d,\s]*)
        | Operation:[ ]new[ ]=[ ]old[ ](?P<operation>.+)
        | Test:[ ]divisible[ ]by[ ](?P<divis_const>\d+)
        | If[ ] true:[ ]throw[ ]to[ ]monkey[ ](?P<divis_throw_target>\d+)
        | If[ ]false:[ ]throw[ ]to[ ]monkey[ ](?P<nondivis_throw_target>\d+)
    """, re.VERBOSE)

    monkeys = []
    item_values = []
    current_items = []
    
    gathered_all_monkey_info = False
    for line in lines:
        line = line.replace('\n', '').replace('  ', '')
        if _print:
            print(line, end='   ')

        mo = pattern.fullmatch(line)
        if not mo:
            if _print:
                print('\n', end='')
            continue
        if _print:
            item = [x for x in mo.groups() if x]
            print(f'{mo.lastgroup} = {item}')

        if mo.lastgroup == 'monkey_idx':
            monkey_idx = int(mo.group('monkey_idx'))
        elif mo.lastgroup == 'items_csv':
            # items = deque(Item(int(x)) for x in mo.group('items_csv').split(','))
            for i, worrylevel_str in enumerate(mo.group('items_csv').split(', ')):
                current_items.append((monkey_idx, i, int(worrylevel_str)))
        elif mo.lastgroup == 'operation':
            op, val = mo.group('operation').split(' ')
            if op == '*' and val == 'old':   # do something abt this one
                operation_fn_str = '^'
                operation_const = 2
            else:
                operation_fn_str = op
                operation_const = int(val)
        elif mo.lastgroup == 'divis_const':
            divis_const = int(mo.group('divis_const'))
        elif mo.lastgroup == 'divis_throw_target':
            divis_throw_target = int(mo.group('divis_throw_target'))
        elif mo.lastgroup == 'nondivis_throw_target':
            nondivis_throw_target = int(mo.group('nondivis_throw_target'))
            gathered_all_monkey_info = True

        # if we've gathered all necessary info, make a monkey and reset needed fields.
        if gathered_all_monkey_info:
            monkeys.append(Monkey(len(current_items), operation_fn_str, operation_const, divis_const, divis_throw_target, nondivis_throw_target))
            item_values += current_items
            current_items = []
            gathered_all_monkey_info = False
            if _print:
                print(' ~ made a monkey!')

    item_array = np.array(item_values, dtype=[('owneridx', np.uint64), ('queueidx', np.uint64), ('worrylevel', np.uint64)])
    return item_array, monkeys

def generate_pretty_print_str_items_and_monkeys(items, monkeys):
    per_monkey_item_worrylevels = [[] for _ in range(len(monkeys))]
    for owneridx, _, worrylevel in items:
        per_monkey_item_worrylevels[owneridx].append(str(worrylevel))

    pretty_print_str = ''
    for i, monkey in enumerate(monkeys):
        item_str = ', '.join(per_monkey_item_worrylevels[i])
        op_str = '* old' if monkey.operation_fn_str == '^' else f'{monkey.operation_fn_str} {monkey.operation_const}'
        pretty_print_str += \
f'''Monkey {i}:
  Starting items: {item_str}
  Operation: new = old {op_str}
  Test: divisible by {monkey.divis_const}
    If true: throw to monkey {monkey.divis_throw_target}
    If false: throw to monkey {monkey.nondivis_throw_target}
'''
        if i < len(monkeys) - 1:
            pretty_print_str += '\n'
    return pretty_print_str

def play_round_of_monkey_in_middle(items, monkeys,
                                   undamaged_item_worry_reduction_factor=WORRY_REDUCT_FACTOR,
                                   worryfatigue=False, monkey_divis_lcm=None, _print=False):
    # inspect all items in each monkey's possession at once.
    for i, monkey in enumerate(monkeys):

        if _print:
            print(f'Monkey {i}:')

        # get reference to slice of items (assumption: items array is sorted)
        _start = 0 if i == 0 else sum(m.num_items_held for m in monkeys[:i])
        _end   = _start + monkeys[i].num_items_held
        current_items = items[_start:_end]
        current_item_worrylvls = current_items.view(np.uint64)[Item.WORRYLVL::3]

        if _print:
            print(f"Items: {items}")
            print(f"Slice: {_start}:{_end}")

        # monkey inspects items
        if _print:
            old_inspection_cnt = monkey.items_inspected
        monkey.items_inspected += monkey.num_items_held  # all items held will be given away
        if _print:
            print(f"  Monkey has inspected {monkey.items_inspected} items up until now ({old_inspection_cnt} + {monkey.num_items_held})")
            print(f"  Items in monkey's possession: {current_items}")

        # viewer worries about items
        if monkey.operation_fn_str == '+':
            current_item_worrylvls += monkey.operation_const
        elif monkey.operation_fn_str == '*':
            current_item_worrylvls *= monkey.operation_const
        elif monkey.operation_fn_str == '^':
            current_item_worrylvls *= current_item_worrylvls
        if _print:
            print(f"  Handling increases worry:     {current_items}")

        # viewer may or may not be relieved when item is not broken
        if not worryfatigue:
            current_item_worrylvls //= undamaged_item_worry_reduction_factor
            if _print:
                print(f"  Releived that nothing broke:  {current_items}")
        # try to reduce the worry levels by LCM of all monkey divis constants to keep numbers down
        else:
            current_item_worrylvls %= monkey_divis_lcm
            # _divis_array = current_item_worrylvls % monkey_divis_lcm
            # for j, modresult in enumerate(_divis_array):
            #     if modresult == 0:
            #         current_items[j][Item.WORRYLVL] //= monkey_divis_lcm
            #         if _print:
            #             print(f'  MONKEY LCM REDUCTION, WOOHOO')

        # apply divisibility test
        divis_array = current_item_worrylvls % monkey.divis_const
        if _print:
            print(f"  Divis counts (% {monkey.divis_const}): {divis_array}")
        
        # throw to next monkey
        if _print:
            divis_target = monkey.divis_throw_target
            ndivs_target = monkey.nondivis_throw_target
            divis_pre = monkeys[divis_target].num_items_held
            ndivs_pre = monkeys[ndivs_target].num_items_held

        for j, modresult in enumerate(divis_array):
            target = monkey.divis_throw_target if modresult == 0 else monkey.nondivis_throw_target
            current_items[j][Item.OWNERIDX] = target
            current_items[j][Item.QUEUEIDX] = monkeys[target].num_items_held
            monkeys[target].num_items_held += 1
        monkey.num_items_held = 0

        # sort the items
        items.sort()

        if _print:
            print("  Throwing aftermath:")
            print(f"    Current monkey ({i})   num items held: {monkey.num_items_held}")
            print(f"    Divis target ({divis_target})     num items held: {monkeys[divis_target].num_items_held}  ({divis_pre} before)")
            print(f"    Nnondivis target ({ndivs_target}) num items held: {monkeys[ndivs_target].num_items_held}  ({ndivs_pre} before)")
            print('\n')

    return items, monkeys

def play_n_rounds(items, monkeys, num_rounds=20, start_round=1,
                  undamaged_item_worry_reduction_factor=WORRY_REDUCT_FACTOR,
                  worryfatigue=False, gen_after_round_str=False, _print=False):
    '''
    start_round is used just for test printing - it doesn't actually matter what round we're on, 
    num_rounds is what affects the outcome.
    '''
    end_round_exclusive = start_round + num_rounds   # we start at 1 - round 1 is *first* round
    
    monkey_divis_lcm = np.lcm.reduce(np.array([m.divis_const for m in monkeys]))

    after_round_status_strings = []
    for round in range(start_round, end_round_exclusive):
        if _print:
            print('='*100, f' ROUND {round}', '='*10)
        items, monkeys = play_round_of_monkey_in_middle(items, monkeys, undamaged_item_worry_reduction_factor, worryfatigue, monkey_divis_lcm, _print)
        
        if gen_after_round_str:
            after_round_str = f'After round {round}, the monkeys are holding items with these worry levels:\n'
            for i, _ in enumerate(monkeys):
                _start = 0 if i == 0 else sum(m.num_items_held for m in monkeys[:i])
                _end   = _start + monkeys[i].num_items_held
                current_item_worrylvls = items[_start:_end].view(np.uint64)[Item.WORRYLVL::3]

                itemstr = ', '.join([str(item) for item in current_item_worrylvls])
                after_round_str += f'Monkey {i}: {itemstr}\n'
            after_round_status_strings.append(after_round_str)
    
    if gen_after_round_str:
        return after_round_status_strings
    return (items, monkeys)

def generate_items_inspected_str(monkeys):
    return '\n'.join([f'Monkey {i} inspected items {m.items_inspected} times.' for i, m in enumerate(monkeys)])

def calculate_monkey_business(monkeys):
    monkeys.sort(key=lambda m: m.items_inspected, reverse=True)
    return monkeys[0].items_inspected * monkeys[1].items_inspected

if __name__ == '__main__':
    items, monkeys = parse_input_file_into_items_and_monkey_list('input.txt')
    # play_round_of_monkey_in_middle(items, monkeys, _print=True)
    # print(
    #     '\n'.join(play_n_rounds(items, monkeys, num_rounds=20, gen_after_round_str=True, worryfatigue=True, _print=True))
    # )
    _, monkeys = play_n_rounds(items, monkeys, num_rounds=10_000, worryfatigue=True)
    print(generate_items_inspected_str(monkeys))
    print(calculate_monkey_business(monkeys))

'''
Idea so far: have a numpy array that represents the items.
    each item has a worrylevel and an owner monkey (idx).

    Tried doing structured arrays for the items:
        values = (worrylevel, ownermonkeyidx) pairs
        dtypes = [('worrylevel', int), ('ownermonkeyidx', int)]
        array = np.array[values, dtypes=dtypes]

    However, when doing 
        array.sort(kind='stable', order='ownermonkeyidx')
    the order of the worrylevels is also sorted... so it won't do.
    Also tried kind='mergesort' and kind=None, but no luck!

    I can do broadcasting, though (applying a constant to the entire array, or a slice of it)

    I can also replace portions of the array, if needed.  ndarrays are mutable, as are structured arrays.




Update -- 

https://numpy.org/doc/stable/user/basics.copies.html
https://numpy.org/doc/stable/reference/generated/numpy.ndarray.view.html#numpy.ndarray.view

Using numpy structured array with owneridx, queueidx, and theeen worrylevel.  Sorting w/o issue now :)
Also -- I made a "view" of the structured array to only modify the worrylevels, it works well!

Idk about speed though.  How can I "benchmark" this code vs my original solution, on a round-by-round basis?


This is my 1st round printout.


---------------------------------------------------------------------------------------------------
Monkey 0:
  Monkey has inspected 2 up until now (0 + 2)
  Items in monkey's possession: [(0, 0, 79) (0, 1, 98)]
  Handling increases worry:     [(0, 0, 1501) (0, 1, 1862)]
  Releived that nothing broke:  [(0, 0, 500) (0, 1, 620)]
  Divis counts (% 23): [17 22]
  Throwing aftermath:
    Current monkey (0)   num items held: 0
    Divis target (2)     num items held: 3  (3 before)
    Nnondivis target (3) num items held: 3  (1 before)


Monkey 1:
  Monkey has inspected 4 up until now (0 + 4)
  Items in monkey's possession: [(1, 0, 54) (1, 1, 65) (1, 2, 75) (1, 3, 74)]
  Handling increases worry:     [(1, 0, 60) (1, 1, 71) (1, 2, 81) (1, 3, 80)]
  Releived that nothing broke:  [(1, 0, 20) (1, 1, 23) (1, 2, 27) (1, 3, 26)]
  Divis counts (% 19): [1 4 8 7]
  Throwing aftermath:
    Current monkey (1)   num items held: 0
    Divis target (2)     num items held: 3  (3 before)
    Nnondivis target (0) num items held: 4  (0 before)


Monkey 2:
  Monkey has inspected 3 up until now (0 + 3)
  Items in monkey's possession: [(0, 0, 20) (0, 1, 23) (0, 2, 27)]                                 < from here onwards, slicing issue!
  Handling increases worry:     [(0, 0, 400) (0, 1, 529) (0, 2, 729)]                                  add more print statements to debug.
  Releived that nothing broke:  [(0, 0, 133) (0, 1, 176) (0, 2, 243)]
  Divis counts (% 13): [3 7 9]
  Throwing aftermath:
    Current monkey (2)   num items held: 0
    Divis target (1)     num items held: 0  (0 before)
    Nnondivis target (3) num items held: 6  (3 before)


Monkey 3:
  Monkey has inspected 6 up until now (0 + 6)
  Items in monkey's possession: [(0, 3,  26) (2, 0,  79) (2, 1,  60) (2, 2,  97) (3, 0,  74) (3, 1, 500)]
  Handling increases worry:     [(0, 3,  29) (2, 0,  82) (2, 1,  63) (2, 2, 100) (3, 0,  77) (3, 1, 503)]
  Releived that nothing broke:  [(0, 3,   9) (2, 0,  27) (2, 1,  21) (2, 2,  33) (3, 0,  25) (3, 1, 167)]
  Divis counts (% 17): [ 9 10  4 16  8 14]
  Throwing aftermath:
    Current monkey (3)   num items held: 0
    Divis target (0)     num items held: 4  (4 before)
    Nnondivis target (1) num items held: 6  (0 before)


After round 1, the monkeys are holding items with these worry levels:
Monkey 0: 9, 27, 21, 33
Monkey 1: 25, 167, 620, 133, 176, 243
Monkey 2: 
Monkey 3: 
---------------------------------------------------------------------------------------------------

'''