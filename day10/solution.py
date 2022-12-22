# from collections import namedtuple

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
def run_instructions_and_return_cpustate(instruction_list, start_cycle=0, end_cycle=None, mid_instruction=0, cpu_state={'register_x' : 1}, _print=False):

    cycle_count = start_cycle
    for instruction in instruction_list:
        if _print:
            print(f'cpu state: {cpu_state}')
            print(f'\t[cycle {cycle_count:>3}] {str(instruction)}')
        # instructions have different execution times, measured in number of cycles
        for instr_cycle in range(mid_instruction, instruction.num_cycles):
            # test for simulation break
            if cycle_count == end_cycle:
                return cpu_state, instr_cycle
            cycle_count += 1
        # apply operation, if needed
        if instruction.operation:
            cpu_state['register_x'] = instruction.operation(instruction.arg, cpu_state['register_x'])
    # if we weren't given an end cycle, we'll run out of instructions.  still want to return cpu state!
    return cpu_state, None

def run_instructions_on_cpu_partone(instr_list, _print=False):

    cpu_state = {'register_x' : 1}

    # mid_instr_break = 0
    # start, end, width = 20, 220, 40
    # for start_cycle, end_cycle, instr_slice in [(0, 20, slice(20))] + \
    #         [(s, e, slice(s, e)) for s, e in zip(range(start, end+1, width), range(start+width, end+width+1, width))]:
    #     instructions = instr_list[instr_slice]
    #     cpu_state, cycles_into_instr = run_instructions_and_return_cpustate(instructions, start_cycle, end_cycle, cycles_into_instr, cpu_state, _print)
    #     if _print:
    #         print(f'cpu state: {cpu_state}')
    #     print(cpu_state)

    # I don't like this approach - not handling if I return mid-cycle.  If I do that, when I restart sim, need to pass in that instruction as well.


if __name__ == '__main__':
    instr_list = parse_instruction_list_from_file('example_two.txt')
    run_instructions_on_cpu_partone(instr_list)