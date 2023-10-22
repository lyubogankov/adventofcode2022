# std library
import pdb
from collections import UserList
# local imports

### input file parsing

## Two approaches to print out lists in problem description printout format.
#   I can either subclass list/UserList and override its __str__ function and 
#   be forced to use my custom list through the whole program (calling 
#   mylist.data instead of mylist w/ UserList -- clunky)
class printlist(UserList):
    '''Overwriting normal list to match problem description printouts'''
    def __init__(self, iterable=[]):
        super().__init__(iterable)
    def __str__(self):
        if len(self.data) == 0:
            return super().__str__()
        retstr = '['
        for item in self.data:
            retstr += f'{str(item)},'
        # remove the trailing comma
        return retstr[:-1] + ']'

#   OR I can make a function that formats lists, and only call it 
#   during print routines.  I think I like option 2 better.
def generate_list_str(_list):
    if len(_list) == 0:
            return '[]'
    retstr = '['
    for item in _list:
        # list -> str
        if isinstance(item, list):
            retstr += f'{generate_list_str(item)},'
        # int -> str
        else:
            retstr += f'{str(item)},'
    # remove the trailing comma
    return retstr[:-1] + ']'

def parse_line_iteratively(line, _print=False, _printchar=False):    
    if _print:
        print('input ', line)
    parsed_line = []
    sublist_stack = [parsed_line]
    current_str = ''
    # skip first outermost bracket
    for c in line[1:]:
        if _printchar:
            print(f'\t{c}', end='    ')
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
        if _printchar:
            print(parsed_line)
    if _print:
        output = generate_list_str(parsed_line)
        print('output', output, end='\n' if _printchar else '\n\n')
        if output != line and not _printchar:
            parse_line_iteratively(line, _print=True, _printchar=True)
    return parsed_line

def parse_line_recursively(line, _print=False, prefix_level=0):
    if _print:
        prefix = '  '*prefix_level
        print(f'{prefix}input:  {line}')
    sublist = []
    current_str = ''
    number_of_chars_to_skip = 0
    for _i, c in enumerate(line[1:]):  # skip the first open bracket
        i = _i + 1                         # adjust index to be for whole line
        if number_of_chars_to_skip:
            number_of_chars_to_skip -= 1
        elif c not in ('[', ',', ']'):
            current_str += c
        elif c in (',', ']') and current_str != '':
            sublist.append(int(current_str))
            current_str = ''
        elif c == '[':
            inner_bracket_counter = 0
            for _y, _c in enumerate(line[i:]):
                if _c == '[':
                    inner_bracket_counter += 1
                elif _c == ']':
                    inner_bracket_counter -= 1
                if inner_bracket_counter == 0:
                    break
            sublist_end = _y + i
            sublist.append(
                parse_line_recursively(
                    line[i:sublist_end+1], _print=_print, prefix_level=prefix_level+1))
            number_of_chars_to_skip = sublist_end - i
    if _print:
        print(f'{prefix}output: {generate_list_str(sublist)}')
        if prefix_level == 0:
            print(f'equivalent? {line == generate_list_str(sublist)}', end='\n\n')
    return sublist

def parse_input_file_into_packet_pairs(inputfile, method='iterative', _print=False):
    with open(inputfile, 'r') as f:
        contents = list(f)
    packet_pairs = []
    for i, line in enumerate(contents):
        # newline / divider between elements
        if i % 3 == 2:
            continue
        if method == 'iterative':
            parsed_line = parse_line_iteratively(line.rstrip(), _print=_print)
        elif method == 'recursive':
            parsed_line = parse_line_recursively(line.rstrip(), _print=_print)
        else:
            raise NotImplementedError("Method must be 'recursive' or 'iterative'.")
        # first element adds a packet pair
        if i % 3 == 0:
            packet_pairs.append([])
        packet_pairs[i//3].append(parsed_line)

    return packet_pairs

### part one
ORDER_CORRECT = 1
ORDER_INCORRECT = 2
ORDER_INDETERMINATE = 3

def determine_order_correctness(lhs, rhs, pairnum=None, indentlevel=0):
    prefix = '  '*indentlevel  + '- '
    resultprefix = '  '*(indentlevel + 1) + '- '
    
    print_str = ''
    if indentlevel == 0:
        print_str += f'== Pair {pairnum} ==\n'
    lhs_str = generate_list_str(lhs) if isinstance(lhs, list) else str(lhs)
    rhs_str = generate_list_str(rhs) if isinstance(rhs, list) else str(rhs)
    print_str += f'{prefix}Compare {lhs_str} vs {rhs_str}\n'
    
    # int vs int
    if isinstance(lhs, int) and isinstance(rhs, int):
        if lhs < rhs:
            print_str += f'{resultprefix}Left side is smaller, so inputs are in the right order\n'
            return ORDER_CORRECT, print_str
        elif rhs < lhs:
            print_str += f'{resultprefix}Right side is smaller, so inputs are not in the right order\n'
            return ORDER_INCORRECT, print_str
        else:
            return ORDER_INDETERMINATE, print_str

    # list vs list
    elif isinstance(lhs, list) and isinstance(rhs, list):
        # go through all items -- stop at first instance of (in)correct order
        for litem, ritem in zip(lhs, rhs):
            result, sub_print_str = determine_order_correctness(litem, ritem, indentlevel=indentlevel+1)
            if result in [ORDER_CORRECT, ORDER_INCORRECT]:
                return result, print_str + sub_print_str
            print_str += sub_print_str
        # tie-breaker - list lengths
        if len(lhs) < len(rhs):
            print_str += f'{resultprefix}Left side ran out of items, so inputs are in the right order\n'
            return ORDER_CORRECT, print_str
        elif len(rhs) < len(lhs):
            print_str += f'{resultprefix}Right side ran out of items, so inputs are not in the right order\n'
            return ORDER_INCORRECT, print_str
        else:
            return ORDER_INDETERMINATE, print_str

    # list vs int
    else:
        lhs_int = isinstance(lhs, int)
        side       = 'left'     if lhs_int else 'right'
        value      = lhs        if lhs_int else rhs

        print_str += f'{resultprefix}Mixed types; convert {side} to [{value}] and retry comparison\n'
        result, sub_print_str = determine_order_correctness(
            lhs = [lhs] if lhs_int else lhs, 
            rhs = rhs if lhs_int else [rhs], 
            indentlevel=indentlevel + 1
        )
        return result, print_str + sub_print_str


def part_one_find_all_correct_pairs(packet_pairs, _print=False):
    correct_order_pair_numbers = []
    for _i, (lhs, rhs) in enumerate(packet_pairs):
        i = _i + 1
        order, print_str = determine_order_correctness(lhs, rhs, pairnum=i)
        if _print:
            print(print_str)
        if order == ORDER_CORRECT:
            correct_order_pair_numbers.append(i)
    return correct_order_pair_numbers

def part_one_obtain_sum(packet_pairs, _print=False):
    return sum(part_one_find_all_correct_pairs(packet_pairs, _print=_print))

### part two

class Packet:
    def __init__(self, value):
        self.value = value
    def __comparison(self, other, expected_comparison_outcome):
        # if not isinstance(other, Packet):
        #     raise NotImplemented
        return determine_order_correctness(lhs=self.value, rhs=other.value)[0] == expected_comparison_outcome
    def __lt__(self, other):
        return self.__comparison(other, expected_comparison_outcome=ORDER_CORRECT)
    def __le__(self, other):
        return not self > other
    def __eq__(self, other):
        return self.__comparison(other, expected_comparison_outcome=ORDER_INDETERMINATE)
    def __ge__(self, other):
        return not self < other
    def __gt__(self, other):
        return self.__comparison(other, expected_comparison_outcome=ORDER_INCORRECT)
    def __str__(self):
        return str(self.value())
    def __repr__(self):
        return f'Packet({self.value})'

def flatten_packet_pairs(packet_pairs):
    """Flatten nested packet pair lists, and encapsulate each packet value within Packet class instance."""
    flattened = []
    for (lhs, rhs) in packet_pairs:
        flattened += [Packet(lhs), Packet(rhs)]
    return flattened

def part_two_sort_and_calculate_decoder_key(packets):
    packets.append(Packet([[2]]))
    packets.append(Packet([[6]]))
    sorted_packets = sorted(packets)
    return (sorted_packets.index(Packet([[2]])) + 1) * (sorted_packets.index(Packet([[6]])) + 1)


if __name__ == '__main__':
    # part 1
    packet_pairs = parse_input_file_into_packet_pairs('input.txt', method='recursive', _print=False)
    print(f'Part one: sum of correct_order indices = {part_one_obtain_sum(packet_pairs)}')

    # part 2
    packets = flatten_packet_pairs(packet_pairs)
    decoder_key = part_two_sort_and_calculate_decoder_key(packets)
    print(f'Part two: decoder key (product of special packet indices) = {decoder_key}')