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
        

if __name__ == '__main__':
    parse_input_file_into_packet_pairs('input.txt', method='recursive', _print=True)