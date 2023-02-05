# # download input file -- this did not work
# import requests
# url = r"https://adventofcode.com/2022/day/1/input"
# r = requests.get(url)
from pprint import pprint

inputfile = "input.txt"

'''
parsing rules:
each line represents calories of a particular food item carried by an elf
elves can carry 1+ food items
delineation between elves = newline
'''
elf_list = []
buffer = []

with open(inputfile, 'r') as inputfile:
    for line in inputfile.readlines():
        if line == '\n':
            elf_list.append([int(item) for item in buffer])  # str -> int calories
            buffer.clear()  # empty out, start anew
            continue
        buffer.append(line.replace('\n', ''))
    # once the file has been read, need to put last elf's items into list 
    else:
        elf_list.append([int(item) for item in buffer])

# PART ONE loop over elves and find max calories
elf_total_calorie_list = [sum(food_list) for food_list in elf_list]
elf_total_calorie_list.sort(reverse=True)
print(f'Elf with most calories is carrying: {elf_total_calorie_list[0]}')

# PART TWO find sum of top 3 elf calories
print(f'Total calories of top 3 elves carrying most calories: {sum(elf_total_calorie_list[:3])}')