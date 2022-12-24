# from dataclasses import dataclass
# import typing
import re

# parse text file -> input
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
                items = [Item(int(x)) for x in mo.group('items_csv').split(',')]
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

if __name__ == '__main__':
    pass

'''
How to use monkey:

new_item = m.operation_fn(item, m.operation_const)
'''