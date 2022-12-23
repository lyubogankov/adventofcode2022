from collections import namedtuple

### input file parsing
class Instruction:

    NOOP = 'noop'
    ADDX = 'addx'

    def __init__(self, name, num_cycles, arg=None, operation_fn=None):
        self.name = name
        self.arg = arg
        self.num_cycles = num_cycles
        self.operation = operation_fn

    def __str__(self):
        return f'{self.name} {self.arg}' if self.arg else f'{self.name}'

    def __repr__(self):
        return f"Instruction(name='{self.name}', arg={self.arg}, num_cycles={self.num_cycles}, operation={self.operation_fn})"

    def prettyprint(self, argwidth, namewidth=4):
        return eval(f"f'{self.name:<{namewidth}} {str(self.arg):>{argwidth}}' if self.arg else f'{self.name:<{namewidth+1+argwidth}}'")

def parse_instruction_list_from_file(instruction_file):
    with open(instruction_file, 'r') as instfile:
        contents = instfile.read()

    instruction_list = []
    for line in contents.split('\n')[:-1]:
        match line.split(' '):
            case [Instruction.NOOP]:
                instruction_list.append(Instruction(name=Instruction.NOOP, num_cycles=1))
            case [Instruction.ADDX, val]:  # addition
                instruction_list.append(Instruction(name=Instruction.ADDX, num_cycles=2, arg=int(val), operation_fn=lambda x, y: x + y))
    return instruction_list

### manipulation / simulation / game loop
def run_instructions_and_return_cpustate(instr_list, instr_start_idx=0, start_cycle=0, num_cycles=None, mid_instr_start_cycles=0, cpu_state={'register_x' : 1}, _print=False):

    if num_cycles is not None:
        end_cycle = start_cycle + num_cycles

    if _print:
        print(f'run_instructions_and_return_cpustate(start_cycle={start_cycle}, num_cycles={num_cycles}, mid_instr_start_cycles={mid_instr_start_cycles}), instr_start_idx={instr_start_idx}) | end_cycle={end_cycle}')

    # if start_cycle == end_cycle or (type(end_cycle) == int and start_cycle >= end_cycle):
    #     return cpu_state, 0, None
    cycle_count = start_cycle

    for instr_num, instruction in enumerate(instr_list[instr_start_idx:], start=1):
        if _print:
            print(f'\t[{str(cycle_count):>3}]   {(instruction.prettyprint(argwidth=3))}  |  cpu state before instr: {cpu_state}')
        # instructions have different execution times, measured in number of cycles
        for instr_cycle in range(mid_instr_start_cycles if instr_num == 1 else 0, instruction.num_cycles):
            cycle_count += 1
            if cycle_count == end_cycle:
                return cpu_state, instr_num, instr_cycle+1
        # apply operation, if needed
        if instruction.operation:
            cpu_state['register_x'] = instruction.operation(instruction.arg, cpu_state['register_x'])
        # Added clause -- if we are trying to simulate clock boundary between cycles (num_cycles=0),
        #                 need to end after instruction is applied.
        if cycle_count == end_cycle:
            return cpu_state, instr_num, 0
    # if we weren't given an end cycle, we'll run out of instructions.  still want to return cpu state!
    return cpu_state, instr_num, None

### part one
RegisterSnapshot = namedtuple('RegisterSnapshot', ['cycle', 'val'])

def run_instructions_on_cpu_partone(instr_list, _print=False):

    cpu_state = {'register_x' : 1}
    snapshots_register_x = []

    # [0, 20)
    instrs_completed = 0
    cpu_state, instructions_run, mid_instr_cycle_count = run_instructions_and_return_cpustate(instr_list, num_cycles=20, cpu_state=cpu_state, _print=_print)
    instrs_completed += instructions_run
    snapshots_register_x.append(RegisterSnapshot(cycle=20, val=cpu_state['register_x']))

    # [[20, 60), [180, 220)]
    for offset in range(0, 181, 40):
        if mid_instr_cycle_count > 0:
            instrs_completed -= 1
        cpu_state, instructions_run, mid_instr_cycle_count = \
                run_instructions_and_return_cpustate(instr_list, instr_start_idx=instrs_completed, mid_instr_start_cycles=mid_instr_cycle_count,
                                                     start_cycle=20+offset, num_cycles=40, cpu_state=cpu_state, _print=_print)
        instrs_completed += instructions_run
        snapshots_register_x.append(RegisterSnapshot(cycle=60+offset, val=cpu_state['register_x']))
    
    return snapshots_register_x

def calculate_signal_strength_sum(instr_list, _print=False):
    snapshots_register_x = run_instructions_on_cpu_partone(instr_list, _print)
    return sum(snapshot.cycle * snapshot.val for snapshot in snapshots_register_x)

### part two
def generate_sprite_pos_str(middle_pixel_pos, linewidth=40):
    # ensure we don't print off screen
    sprite_start_pixel = max(0,           middle_pixel_pos - 1)
    sprite_end_pixel   = min(linewidth-1, middle_pixel_pos + 1)
    sprite_width = (sprite_end_pixel - sprite_start_pixel) + 1
    return '.'*sprite_start_pixel + '#'*sprite_width + '.'*(linewidth - sprite_width - sprite_start_pixel)

def generate_crt_printstr_parttwo(instr_list, cycle_num_start=1, cycle_num_end=240, _print=False, gen_test_str=False):
    '''
    - Initial sprite pos = 1 (register x value), and regX value represents the middle pixel (sprite is 3 wide)
    - CRT rows go from [0, 39] or [0, 40) - whichever notation you prefer (they are 40 pixels wide)
    - CRT prints from top left to bottom right, one pixel DURING each cycle
    '''

    CRT_LINEWIDTH = 40
    crt_str = ''

    cpu_state = {'register_x' : 1}
    current_instr = 0
    mid_instr_cycle_count = 0

    if gen_test_str:
        test_str = f"Sprite position: {generate_sprite_pos_str(cpu_state['register_x'])}\n\n"

    for cycle_num in range(cycle_num_start, cycle_num_end + 1):
        
        ## cycle start
        if gen_test_str and mid_instr_cycle_count == 0:
            test_str += f'Start cycle  {cycle_num:>2}: begin executing {str(instr_list[current_instr])}\n'
        
        ## during cycle, generate CRT string
        crt_pixel_pos = (cycle_num-1) % CRT_LINEWIDTH
        # if we're at the start of a newline, need to terminate old one!
        if crt_pixel_pos == 0 and crt_str != '':
            crt_str += '\n' 
        crt_str += '#' if (cpu_state['register_x'] - 1 <= crt_pixel_pos <= cpu_state['register_x'] + 1) else '.'
        if gen_test_str:
            test_str += f'During cycle {cycle_num:>2}: CRT draws pixel in position {crt_pixel_pos}\n'
            test_str += f'Current CRT row: {crt_str}\n'

        ## after cycle, apply instruction to CPU
        cpu_state, instructions_run, mid_instr_cycle_count = \
                run_instructions_and_return_cpustate(instr_list, instr_start_idx=current_instr,
                                                     mid_instr_start_cycles=mid_instr_cycle_count,
                                                     start_cycle=cycle_num-1, num_cycles=1, cpu_state=cpu_state, _print=_print)
        current_instr += instructions_run
        if mid_instr_cycle_count > 0:
            current_instr -= 1
        
        # finish out instruction, if needed
        if mid_instr_cycle_count == instr_list[current_instr].num_cycles:
            prior_cpu_register_x_val = cpu_state['register_x']
            cpu_state, instructions_run, mid_instr_cycle_count = \
                    run_instructions_and_return_cpustate(instr_list, instr_start_idx=current_instr,
                                                        mid_instr_start_cycles=mid_instr_cycle_count,
                                                        start_cycle=cycle_num, num_cycles=0, cpu_state=cpu_state, _print=_print)
            current_instr += 1  # we're done with this instruction!
            if gen_test_str:
                test_str += f"End of cycle {cycle_num:>2}: finish executing {str(instr_list[current_instr-1])}"
                if instr_list[current_instr-1].name != Instruction.NOOP:
                    test_str += f" (Register X is now {cpu_state['register_x']})"
                test_str += '\n'
                if prior_cpu_register_x_val != cpu_state['register_x']:
                    test_str += f"Sprite position: {generate_sprite_pos_str(cpu_state['register_x'])}\n"
        ## finish test_str
        if gen_test_str and cycle_num_end - cycle_num > 0:
            test_str += '\n'
            

    return crt_str, test_str if gen_test_str else None

if __name__ == '__main__':
    instr_list = parse_instruction_list_from_file('input.txt')
    # print(f'Part one: {calculate_signal_strength_sum(instr_list, _print=True)}')
    # crt_str, test_str = generate_crt_printstr_parttwo(instr_list, cycle_num_end=21, gen_test_str=True, _print=True)
    crt_str, _ = generate_crt_printstr_parttwo(instr_list)
    print(crt_str)

'''
Potential switchups that might occur for part two:
- more than one register, instructions affect different registers based on some rule
- additional instruction type(s)
- more than one CPU, instructions get mapped to different CPUs based on some rule

Tried to parameterize the sim funciton to be able to address these if they come up!


Actual switchup for part 2 -- simulating a CRT!  I did not expect that :P


I was able to check my output using a simple spreadsheet:

--------------+--------------------------+----------------------------------
col A         | col B                    | col C
(instruction) | (post-instr cycle count) | (post-instruction X register val)
--------------+--------------------------+----------------------------------
                 0                          1                               row 1
addx 1           2                          2                               row 2
noop             3                          2                               row 3
...              ...                        ...
                =IF(LEFT(A2, 4)="addx", B1+2, B1+1)
                                           =IF(LEFT(A2, 4)="addx", C1+RIGHT(A2, LEN(A2)-5), C1)


I created unit tests based on the adventofcode problem description and worked examples.

I matched the printout of their cycle-by-cycle execution for part two, and was able to directly compare printouts as the unittest.
This process exposed the need for a "0-cycle" advance of the simulation, to allow for instructions
(which occur BETWEEN cycles, on clock edges) to finish!
'''