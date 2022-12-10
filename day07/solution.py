'''
Brainstorming

Step 1: turn the input file into a directory tree structure.
    Two types of entities in the tree:
        - Directories (nodes that point to other nodes) -- point to 0 or more files (leaf nodes)
            Have a name, and 0 or more children to whom they point (can be other Directories, or can be Files)
            Should also have a "size contained" field, which is the total size of all files contained below this Dir.
        - Files (nodes that do not point to other nodes)
            Have a name and a size

Step 2: once I have the text file turned into a directory tree,
        make a function for printing the data structure -> human readable (like in their example).

Step 3: Answer part one!
        Iterate over dir tree and extract all directory names / contained sizes.  If their size is at most 100_000, add them to sum.
            (Note that this process can add files more than once since a file can belong to multiple directories' contained size totals).
'''

import re

class Directory:
    def __init__(self, name, parentdir=None):
        # initialize this Directory
        self.name = name
        self.parentdir = parentdir
        self.contents = []
        self.contained_size = 0
        # if applicable, add it to its parentdir
        if parentdir:
            parentdir.contents.append(self)
    def __repr__(self):
        return f"Directory(name={repr(self.name)}, parentdir={repr(self.parentdir)})"
    def __str__(self):
        return f"{self.name} (dir)"
    
    def print_contents(self):
        for item in self.contents:
            print(str(item))

    def print_tree(self, spaces=0):
        # first, print the name of current dir
        print(' '*spaces + f'- {str(self)}')
        # then, print all of the contents
        spaces += 2
        for item in self.contents:
            if type(item) == File:
                print(' '*spaces + f'- {str(item)}')
            else:
                item.print_tree(spaces=spaces)

class File:
    def __init__(self, name, size, parentdir):
        # initialize this File
        self.name = name
        self.size = size
        self.parentdir = parentdir
        # add it to parentdir
        parentdir.contents.append(self)
        # add the contained_size to all directories above this file, going up to the root
        pd = parentdir
        while pd:
            pd.contained_size += size
            pd = pd.parentdir
    def __repr__(self):
        return f"File(name={repr(self.name)}, size={self.size}, parentdir={repr(self.parentdir)})"
    def __str__(self):
        return f"{self.name} (file, size={self.size})"

def parse_command_log_into_dir_tree(inputfile):
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()

    cd_parser = re.compile(r"\$ cd (\S+)")
    ls_file_parser = re.compile(r"(\d+) (\S+)")
    ls_dir_parser = re.compile(r"dir (\S+)")

    root = Directory(name='/')  # special case -- this is the root
    current_dir = root

    # skip last element -- file ends with a newline, so it's an extra empty string.
    # TODO I think I could do this with a match statement -- try it!
    for line in contents.split('\n')[:-1]:
        
        # ls command - we don't care about command itself, just its output!
        if line == '$ ls':
            continue

        # cd command
        elif (m := cd_parser.match(line)):
            dirname = m.groups()[0]
            
            # special case -- go directly to the root directory
            if dirname == '/':
                current_dir = root
                continue

            # move out one level, if we're not already at root
            if dirname == '..':
                if current_dir != root:
                    current_dir = current_dir.parentdir
                continue

            # move in one level - may need to create new Dir
            for item in current_dir.contents:
                # it already exists!  set current_dir pointer to the existing Dir.
                if type(item) == Directory and item.name == dirname:
                    current_dir = item
                    break
            else:
                # if we get here, Dir doesn't exist.  Need to make it!
                newdir = Directory(name=dirname, parentdir=current_dir)
                current_dir = newdir

        # output from ls command -- dir (create new dir!)
        elif (ls := ls_dir_parser.match(line)):
            dirname = ls.groups()[0]
            Directory(name=dirname, parentdir=current_dir)

        # output from ls command -- file (create new file!)
        elif (ls := ls_file_parser.match(line)):
            filesize, filename = ls.groups()
            File(name=filename, size=int(filesize), parentdir=current_dir)

    return root


def make_list_of_dir_meeting_criteria(current_dir, criteria_fn):
    dirs_meeting_criteria = []
    if criteria_fn(current_dir):
        dirs_meeting_criteria.append(current_dir)
    for item in current_dir.contents:
        if type(item) == Directory:
            dirs_meeting_criteria += make_list_of_dir_meeting_criteria(item, criteria_fn)
    return dirs_meeting_criteria

def part_one(root):
    '''Need to find all directories that contain <= 100000, and print their sum.'''
    # dirs_below_size = make_set_of_subdir_below_size(current_dir=root, size_limit=100_000)  # original function, before refactor
    dirs_below_size = make_list_of_dir_meeting_criteria(current_dir=root, criteria_fn=lambda dir: dir.contained_size <= 100_000)
    return sum(dir.contained_size for dir in dirs_below_size)

def part_two(root):
    '''What is the smallest file we can delete to free up enough space for update?
    Total disk space = 70_000_000, size needed for update = 30_000_000.
    '''
    current_disk_usage = root.contained_size
    current_free_space = 70_000_000 - current_disk_usage
    space_to_free_for_update = 30_000_000 - current_free_space

    dirs_above_size = make_list_of_dir_meeting_criteria(current_dir=root, criteria_fn=lambda dir: dir.contained_size >= space_to_free_for_update)
    return min(dir.contained_size for dir in dirs_above_size)


if __name__ == '__main__':
    for inputfile in ['example.txt', 'input.txt']:
        print('---', inputfile, '-'*(40-len(inputfile)))
        dir_tree = parse_command_log_into_dir_tree(inputfile)
        # dir_tree.print_tree()
        print(f'\tpart one: {part_one(dir_tree)}')
        print(f'\tpart two: {part_two(dir_tree)}')