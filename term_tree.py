import numpy as np


class TermNode:

    def __init__(self, value):
        self.left = None
        self.right = None
        self.leaf = True
        self.value = value

    def split(self, splitter):
        result = splitter.split(self.value)
        if result is None:
            return False
        self.left = TermNode(result[0])
        self.right = TermNode(result[1])
        self.value = result[2]
        self.leaf = False
        return True

    def to_string(self, root=True):

        if self.leaf:
            return str(self.value)
        else:
            content = self.left.to_string(False) + self.value + self.right.to_string(False)
            if root:
                return content
            else:
                return "(" + content + ")"