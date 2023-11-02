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
        """BoundingBox is includes both the topleft and bottomright Point_2Ds"""
        self.topleft = topleft
        self.bottomright = bottomright
        # checking axis orientations to compute valid range of x, y values
        if topleft.x < bottomright.x:
            self.xrange = range(topleft.x, bottomright.x + 1)
        else:
            self.xrange = range(bottomright.x, topleft.x + 1)

        if topleft.y < bottomright.y:
            self.yrange = range(topleft.y, bottomright.y + 1)
        else:
            self.yrange = range(bottomright.y, topleft.y + 1)
    
    # in operator
    def __contains__(self, item: Point_2D):
        return item.x  in self.xrange and item.y in self.yrange

    def width(self):
        return abs(self.bottomright.x - self.topleft.x)

    def height(self):
        return abs(self.bottomright.y - self.topleft.y)