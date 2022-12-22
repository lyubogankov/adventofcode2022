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
def run_instructions_and_return_cpustate(instr_list, instr_start_idx=0, start_cycle=0, end_cycle=None, mid_instr_start_cycles=0, cpu_state={'register_x' : 1}, _print=False):

    if _print:
        print(f'run_instructions_and_return_cpustate(start_cycle={start_cycle}, end_cycle={end_cycle}, mid_instr_start_cycles={mid_instr_start_cycles}), instr_start_idx={instr_start_idx})')

    if start_cycle == end_cycle or (type(end_cycle) == int and start_cycle >= end_cycle):
        return cpu_state, 0, None
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
    # if we weren't given an end cycle, we'll run out of instructions.  still want to return cpu state!
    return cpu_state, instr_num, None

def run_instructions_on_cpu_partone(instr_list, _print=False):

    RegisterSnapshot = namedtuple('RegisterSnapshot', ['cycle', 'val'])

    cpu_state = {'register_x' : 1}
    snapshots_register_x = []

    # [0, 20)
    instrs_completed = 0
    cpu_state, instructions_run, mid_instr_cycle_count = run_instructions_and_return_cpustate(instr_list, end_cycle=20, cpu_state=cpu_state, _print=_print)
    instrs_completed += instructions_run
    snapshots_register_x.append(RegisterSnapshot(cycle=20, val=cpu_state['register_x']))

    # [[20, 60), [180, 220)]
    for offset in range(0, 181, 40):
        if mid_instr_cycle_count > 0:
            instrs_completed -= 1
        cpu_state, instructions_run, mid_instr_cycle_count = \
                run_instructions_and_return_cpustate(instr_list, instr_start_idx=instrs_completed, mid_instr_start_cycles=mid_instr_cycle_count,
                                                    start_cycle=20+offset, end_cycle=60+offset, cpu_state=cpu_state, _print=_print)
        instrs_completed += instructions_run
        snapshots_register_x.append(RegisterSnapshot(cycle=60+offset, val=cpu_state['register_x']))
    
    return snapshots_register_x

def calculate_signal_strength_sum(instr_list, _print=False):
    snapshots_register_x = run_instructions_on_cpu_partone(instr_list, _print)
    return sum(snapshot.cycle * snapshot.val for snapshot in snapshots_register_x)

if __name__ == '__main__':
    instr_list = parse_instruction_list_from_file('input.txt')
    print(f'Part one: {calculate_signal_strength_sum(instr_list, _print=True)}')


'''
Potential switchups that might occur for part two:
- more than one register, instructions affect different registers based on some rule
- additional instruction type(s)
- more than one CPU, instructions get mapped to different CPUs based on some rule

Tried to parameterize the sim funciton to be able to address these if they come up!
'''