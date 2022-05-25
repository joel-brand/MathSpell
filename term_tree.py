import numpy as np


class TermNode:

    def __init__(self, value, locked=False):
        self.left = None
        self.right = None
        self.leaf = True
        self.value = value
        self.locked = locked

    def split(self, splitter):
        result = splitter.split(self.value)
        if result is None:
            return False
        left_val, right_val, symbol, lock_left, lock_right = result
        self.left = TermNode(left_val, lock_left)
        self.right = TermNode(right_val, lock_right)
        self.value = symbol
        self.leaf = False
        return True

    def to_string(self, root=True):
        if self.leaf:
            return str(self.value)
        else:
            content = self.value(self.left.to_string(False), self.right.to_string(False))
            if root:
                return "x = " + content
            else:
                return "(" + content + ")"

    def use_large_division_at_top(self):
        if self.leaf:
            return
        elif self.value.__name__ == "divide_symbol":
            self.value = lambda l, r: "\\frac{{{0}}}{{{1}}}".format(l, r)
        else:
            self.left.use_large_division_at_top()
            self.right.use_large_division_at_top()
