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

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

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