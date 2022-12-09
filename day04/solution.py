import re


# Structure of input data
# a-b,c-d
#   where each pair of numbers separated by hyphens indicates the range of ID numbers (a (inclusive) to b (inclusive))
#   and two ID ranges are given per line, since the elves are paired up.

def part_one(raw_data):
    # Question: In how many assignment pairs does one range fully contain the other?
    #   To answer this, we can use set properties!
    subset_counter = 0
    for elf1_id_set, elf2_id_set in raw_data:
        if elf1_id_set.issuperset(elf2_id_set) or elf2_id_set.issuperset(elf1_id_set):
            subset_counter += 1
    print(f"Part 1: number of elf pairs where one elf's responsibilities are a subset of the other's: {subset_counter}")

def part_two(raw_data):
    # Question: In how many assignment pairs do the ranges overlap at all?
    intersection_counter = 0
    for elf1_id_set, elf2_id_set in raw_data:
        if len(elf1_id_set.intersection(elf2_id_set)) > 0:
            intersection_counter += 1
    print(f"Part 2: number of elf pairs with any intersection of responsibilities: {intersection_counter}")

if __name__ == '__main__':
    # raw_data structure:
    #   - list of lists
    #   - each list represents the pair of elves (and therefore has two elements)
    #   - the two elements are sets of ids for which the elves are responsible
    parser = re.compile(r"(\d+)-(\d+),(\d+)-(\d+)")
    for inputfile in ['example.txt', 'input.txt']:
        print(f'--- {inputfile}')
        raw_data = []
        with open(inputfile, 'r') as _inputfile:
            for line in _inputfile.readlines():
                elf1_start, elf1_end, elf2_start, elf2_end = map(int, parser.search(line).groups())
                raw_data.append([
                    {id for id in range(elf1_start, elf1_end + 1)},
                    {id for id in range(elf2_start, elf2_end + 1)}
                ])
        part_one(raw_data)
        part_two(raw_data)