# from dataclasses import dataclass
# import typing
from collections import deque  # using instead of list -- O(1) vs O(n) left side pop!
import copy
import re

### parse text file -> input
class Item:
    UNDAMAGED_ITEM_WORRY_REDUCTION_FACTOR = 3

    def __init__(self, worrylevel):
        self.worrylevel = worrylevel
    
    def __add__(self, other):
        if isinstance(other, int):
            return Item(self.worrylevel + other) 
    
    def __mul__(self, other):
        if isinstance(other, int):
            return Item(self.worrylevel * other)

    def __pow__(self, other):
        if isinstance(other, int):
            return Item(pow(self.worrylevel, other))

    def __repr__(self):
        return f"Item(worrylevel={self.worrylevel})"

    def __str__(self):
        # just the worry level, to match problem description
        return str(self.worrylevel)

    def item_still_intact_worry_reduction(self):
        '''From problem description, upon realizing monkey didn't damage item, worry decreases
        (divided by constant factor and rounded to nearest integer, hence use of integer floor division)'''
        self.worrylevel //= Item.UNDAMAGED_ITEM_WORRY_REDUCTION_FACTOR

class Monkey:
    operation_dict = {
        '+' : Item.__add__,
        '*' : Item.__mul__,
    }

    def __init__(self, monkeyidx, items, operation_fn, operation_fn_str, operation_const, divis_const, divis_throw_target, nondivis_throw_target):
        self.monkeyidx             = monkeyidx
        self.items                 = items
        self.operation_fn          = operation_fn
        self.operation_fn_str      = operation_fn_str
        self.operation_const       = operation_const
        self.divis_const           = divis_const
        self.divis_throw_target    = divis_throw_target
        self.nondivis_throw_target = nondivis_throw_target
        self.items_inspected       = 0  # counter for part one

    def __str__(self):
        item_str = ', '.join([str(item) for item in self.items])
        op_str = '* old' if self.operation_fn_str == '^' else f'{self.operation_fn_str} {self.operation_const}'
        return \
f'''Monkey {self.monkeyidx}:
  Starting items: {item_str}
  Operation: new = old {op_str}
  Test: divisible by {self.divis_const}
    If true: throw to monkey {self.divis_throw_target}
    If false: throw to monkey {self.nondivis_throw_target}
'''

def parse_input_file_into_monkey_list(inputfile, _print=False):
    '''
    
    Using nondivis_throw_target as a flag variable
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

        match mo.lastgroup:
            case 'monkey_idx':
                monkey_idx = int(mo.group('monkey_idx'))
            case 'items_csv':
                items = deque(Item(int(x)) for x in mo.group('items_csv').split(','))
            case 'operation':
                op, val = mo.group('operation').split(' ')
                if op == '*' and val == 'old':
                    operation_fn = Item.__pow__
                    operation_fn_str = '^'
                    operation_const = 2
                else:
                    operation_fn = Monkey.operation_dict[op]
                    operation_fn_str = op
                    operation_const = int(val)
            case 'divis_const':
                divis_const = int(mo.group('divis_const'))
            case 'divis_throw_target':
                divis_throw_target = int(mo.group('divis_throw_target'))
            case 'nondivis_throw_target':
                nondivis_throw_target = int(mo.group('nondivis_throw_target'))
                gathered_all_monkey_info = True

        # if we've gathered all necessary info, make a monkey and reset flag info field.
        if gathered_all_monkey_info:
            monkeys.append(Monkey(monkey_idx, items, operation_fn, operation_fn_str, operation_const, 
                                  divis_const, divis_throw_target, nondivis_throw_target))
            gathered_all_monkey_info = False
            if _print:
                print(' ~ made a monkey!')

    return monkeys

### monkey in the middle - part one
def play_round_of_monkey_in_middle(monkeys, generate_round_detail_str=False, worryfatigue=False):
    round_detail_str = ''

    for monkey in monkeys:
        if generate_round_detail_str:
            round_detail_str += f'Monkey {monkey.monkeyidx}:\n'
        
        while len(monkey.items) > 0:
            # inspect next item
            item = monkey.items.popleft()
            monkey.items_inspected += 1  # for part one question
            if generate_round_detail_str:
                round_detail_str += f'  Monkey inspects an item with a worry level of {item.worrylevel}.\n'
            
            # viewer worries about item
            modified_item = monkey.operation_fn(item, monkey.operation_const)
            if generate_round_detail_str:
                val_str = monkey.operation_const
                match monkey.operation_fn_str:
                    case '+':
                        op_str = 'increases'
                    case '*':
                        op_str = 'is multiplied'
                    case '^':
                        op_str = 'is multiplied'
                        val_str = 'itself'
                round_detail_str += f'    Worry level {op_str} by {val_str} to {modified_item.worrylevel}.\n'
            
            # viewer is releived when item is not broken (modified for part two)
            if not worryfatigue:
                modified_item.item_still_intact_worry_reduction()
                if generate_round_detail_str:
                    round_detail_str += f'    Monkey gets bored with item. Worry level is divided by {Item.UNDAMAGED_ITEM_WORRY_REDUCTION_FACTOR} to {modified_item.worrylevel}.\n'
            
            # divisibility test, to determine which target monkey
            divisible = modified_item.worrylevel % monkey.divis_const == 0
            if generate_round_detail_str:
                round_detail_str += f"    Current worry level is{'' if divisible else ' not'} divisible by {monkey.divis_const}.\n"
            
            # throw to next monkey
            target = monkey.divis_throw_target if divisible else monkey.nondivis_throw_target
            monkeys[target].items.append(modified_item)
            if generate_round_detail_str:
                round_detail_str += f'    Item with worry level {modified_item.worrylevel} is thrown to monkey {target}.\n'

    if generate_round_detail_str:
        return round_detail_str
    return monkeys

def play_n_rounds(monkeys, num_rounds=20, start_round=1, generate_after_round_str=False, worryfatigue=False):
    '''
    start_round is used just for test printing - it doesn't actually matter what round we're on, 
    num_rounds is what affects the outcome.
    '''
    end_round_exclusive = start_round + num_rounds   # we start at 1 - round 1 is *first* round
    
    after_round_status_strings = []
    for round in range(start_round, end_round_exclusive):
        monkeys = play_round_of_monkey_in_middle(monkeys, worryfatigue=worryfatigue)
        if generate_after_round_str:
            after_round_str = f'After round {round}, the monkeys are holding items with these worry levels:\n'
            for monkey in monkeys:
                itemstr = ', '.join([str(item) for item in monkey.items])
                after_round_str += f'Monkey {monkey.monkeyidx}: {itemstr}\n'
            after_round_status_strings.append(after_round_str)
    
    if generate_after_round_str:
        return after_round_status_strings
    return monkeys    

def calculate_monkey_business(monkeys, num_rounds, generate_items_inspected_str=False, worryfatigue=False):
    monkeys = play_n_rounds(monkeys, num_rounds=num_rounds, worryfatigue=worryfatigue)
    if generate_items_inspected_str:
        return '\n'.join([f'Monkey {m.monkeyidx} inspected items {m.items_inspected} times.' for m in monkeys])
    monkeys.sort(key=lambda m: m.items_inspected, reverse=True)
    return monkeys[0].items_inspected * monkeys[1].items_inspected

if __name__ == '__main__':
    monkeys = parse_input_file_into_monkey_list('example.txt')
    print('Part one:', calculate_monkey_business(monkeys, num_rounds=20,     worryfatigue=False))
    print('Part two:', calculate_monkey_business(monkeys, num_rounds=10_000, worryfatigue=True ))

'''
Part 2 requires 10_000 rounds of monkey in the middle... my implementation is way too slow!

Optimizations:
1. per-monkey items stored in deque instead of list, since I am popping from the front.  O(1) vs O(n) - didn't really help though :(
'''