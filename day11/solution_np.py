# std library
import re
# third-party
import numpy as np

'''
Idea so far: have a numpy array that represents the items.
    each item has a worrylevel and an owner monkey (idx).

    Tried doing structured arrays for the items:
        values = (worrylevel, ownermonkeyidx) pairs
        dtypes = [('worrylevel', int), ('ownermonkeyidx', int)]
        array = np.array[values, dtypes=dtypes]

    However, when doing 
        array.sort(kind='stable', order='ownermonkeyidx')
    the order of the worrylevels is also sorted... so it won't do.
    Also tried kind='mergesort' and kind=None, but no luck!

    I can do broadcasting, though (applying a constant to the entire array, or a slice of it)

    I can also replace portions of the array, if needed.  ndarrays are mutable, as are structured arrays.


'''