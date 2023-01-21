# std library
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