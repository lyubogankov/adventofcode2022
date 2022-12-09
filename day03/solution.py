rucksackfile = 'input.txt'

def prioritize_item(item):
    item_ord = ord(item)
    if 97 <= item_ord <=122:
        return (item_ord - 96)  # 1 - 26   (original ascii range 97 - 122, offsetting by -96)
    elif 65 <= item_ord <= 90:
        return (item_ord - 38)  # 27 - 52  (original ascii range 65 - 90, offsetting by -65 + 27)
    
def turn_rucksack_str_into_set(rucksack_str):
    return {item for item in rucksack_str}

def part_one():
    total_priority_score = 0
    with open(rucksackfile, 'r') as rucksack_file:
        for rucksack_contents in rucksack_file.readlines():
            rucksack_contents = rucksack_contents.replace('\n', '')
            midpoint = int( len(rucksack_contents) / 2 )
            compartment_one_contents = turn_rucksack_str_into_set(rucksack_contents[:midpoint])
            compartment_two_contents = turn_rucksack_str_into_set(rucksack_contents[midpoint:])
            items_in_both_compartments = compartment_one_contents.intersection(compartment_two_contents)
            total_priority_score += sum(prioritize_item(item) for item in items_in_both_compartments)

    print(f'Total priority score for mis-placed items: {total_priority_score}')

def part_two():

    # Parse the file - keep a counter for which line number I'm on.
    # Use mod to determine when a new group needs to be formed (0, 3, 6, ... 3*n % 3 = 0, otherwise 1 or 2)

    # Once I have three elves (look for % 2 = 2), look at the intersection of the three elves' contents

    total_badge_scores = 0
    current_line = 0
    current_group_rucksack_content_sets = []
    with open(rucksackfile, 'r') as rucksack_file:
        for rucksack_contents in rucksack_file.readlines():            
            rucksack_contents = rucksack_contents.replace('\n', '')
            # reset
            if current_line % 3 == 0:
                current_group_rucksack_content_sets = []
            # turn the current line into a set
            current_group_rucksack_content_sets.append({item for item in rucksack_contents})
            # if this is the third elf, come up with a badge for the prior three!
            if current_line % 3 == 2:
                elf_one_contents, elf_two_contents, elf_three_contents = current_group_rucksack_content_sets
                elf_one_two_intersection = elf_one_contents.intersection(elf_two_contents)
                badge_set = elf_one_two_intersection.intersection(elf_three_contents)  # this should be a set of one element
                badge_letter = list(badge_set)[0]
                print(f'\t{badge_letter}')
                total_badge_scores += prioritize_item(badge_letter)

            current_line += 1
    print(f'Total of the badge scores: {total_badge_scores}')

if __name__ == '__main__':
    part_two()