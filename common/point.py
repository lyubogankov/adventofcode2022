class Point_2D:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point_2D(x={' ' if self.x >= 0 else ''}{self.x}, y={' ' if self.y >= 0 else ''}{self.y})"

    def __str__(self):
        return f"({' ' if self.x >= 0 else ''}{self.x}, {' ' if self.y >= 0 else ''}{self.y})"

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point_2D(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point_2D(x, y)

    def __mul__(self, k):
        if isinstance(k, int):
            return Point_2D(k*self.x, k*self.y)

    ## I want Point_2D to be immutable
    # def __iadd__(self, other):
    #     self.x += other.x
    #     self.y += other.y
    #     return self

    # heavily inspired by https://stackoverflow.com/q/390250
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    # https://stackoverflow.com/a/1608882 -- if I implement __eq__, I also need to implement __hash__
    # https://stackoverflow.com/a/2909119 -- solution for implementing hash.  Rely on hash of tuple!
    def __hash__(self):
        key = (self.x, self.y)
        return hash(key)

class BoundingBox:
    def __init__(self, topleft: Point_2D, bottomright: Point_2D):
        self.topleft = topleft
        self.bottomright = bottomright
        # checking axis orientations
        self.x__right_gt_left = topleft.x < bottomright.x
        self.y__bottom_gt_left = topleft.y < bottomright.y
    
    # in operator
    def __contains__(self, item):
        pass
        # TODO: how to represent this in a coordinate-system agnostic manner??
        #   right now I can only think of how to use it for my particular case,
        #   where
        #       left = -x, right = +x
        #       top  = -y, bot   = +y
        #
        #   I suppose that since each axis has two possible configurations, there are
        #   four combinations.  Perhaps I can test for it in the constructor and set
        #   flag variables to help with the __contains__ check
        #       l -x r +x | t -y t +y
        #       l -x r +x | t +y t -y
        #       l +x r -x | t -y t +y
        #       l +x r -x | t +y t -y