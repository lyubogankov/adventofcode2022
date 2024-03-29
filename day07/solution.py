'''
Brainstorming prior to starting

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
    
    # Wanted to implement this after the fact.
    # What if we constrained solution to not allow Directory to have member variable contained_size?
    # If we really cared about memory, then storing contained_size would be a no-go since it's not
    #   information that we couldn't calculate on the fly (unlike the other parameters).
    def calc_contained_size(self):
        # I originally used a match/case statement, as follows:
        #       match type(item):
        #           case File: ...
        #           case Directory: ...
        # However, got an error! 'Capture makes remaining patterns unreachable.'
        # https://stackoverflow.com/a/67525259
        # ^ Raymond Hettinger has some suggestions but I like if/else better than those.
        contained_size = 0
        for item in self.contents:
            if type(item) == File:
                contained_size += item.size
            elif type(item) == Directory:
                contained_size += item.calc_contained_size()
        return contained_size

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

def parse_command_log_into_dir_tree_v2(inputfile):
    '''This rewrite is brought to you by Raymond Hettinger.  https://stackoverflow.com/a/72538070
    It's almost exactly the same in terms of LOC, but a different approach.
    Using one big regex expression with named groups instead of three, and match/case instead of if/else.
    '''
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()

    # When in VERBOSE mode, whitespace is ignored.
    #   I used [ ] to match spaces (char class of just spaces).  
    #   I like it better than escaping the whitespace ('\ 'vs '[ ]')
    #   Yes, it's one extra character, but I like how it looks.
    pattern = re.compile(r"""
          \$[ ]cd[ ](?P<cd_dir>\S+)                      # $ cd dirname          -> dirname
        | dir[ ](?P<ls_dir>\S+)                          # dir dirname           -> dirname
        | (?P<ls_file_size>\d+)[ ](?P<ls_file_name>\S+)  # filesize filename.ext -> filesize filename&ext
    """,
    re.VERBOSE)

    root = Directory(name='/')  # special case -- this is the root
    current_dir = root

    # skip last element -- file ends with a newline, so it's an extra empty string.
    for line in contents.split('\n')[:-1]:
        mo = pattern.fullmatch(line)
        # skip when no match
        if not mo:
            continue
        match mo.lastgroup:
            # log a directory into the dir tree
            case 'ls_dir':
                dirname = mo.group('ls_dir')
                Directory(name=dirname, parentdir=current_dir)
            # log a file into the dir tree
            case 'ls_file_name':
                filename = mo.group('ls_file_name')
                filesize = mo.group('ls_file_size')
                File(name=filename, size=int(filesize), parentdir=current_dir)
            # cd -- need to change current_dir pointer, and potentially create new dir
            case 'cd_dir':
                dirname = mo.group('cd_dir')
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
    return root

def parse_command_log_into_dir_tree(inputfile):
    '''First implimentation of file parser using three separate regex expressions and if/else.'''
    with open(inputfile, 'r') as _inputfile:
        contents = _inputfile.read()

    cd_parser = re.compile(r"\$ cd (\S+)")
    ls_file_parser = re.compile(r"(\d+) (\S+)")
    ls_dir_parser = re.compile(r"dir (\S+)")

    root = Directory(name='/')  # special case -- this is the root
    current_dir = root

    # skip last element -- file ends with a newline, so it's an extra empty string.
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


def test_calc_contained_size(root):
    '''Testing out the two implementations, storing vs calculating contained_size'''
    assert root.contained_size == root.calc_contained_size()
    for item in root.contents:
        if type(item) == Directory:
            test_calc_contained_size(item)

if __name__ == '__main__':
    for inputfile in ['example.txt', 'input.txt']:
        print('---', inputfile, '-'*(40-len(inputfile)))
        dir_tree = parse_command_log_into_dir_tree(inputfile)
        # dir_tree.print_tree()
        print(f'\tpart one: {part_one(dir_tree)}')
        print(f'\tpart two: {part_two(dir_tree)}')

        # # testing out Directory.calc_contained_size() -- it worked!
        # test_calc_contained_size(dir_tree)