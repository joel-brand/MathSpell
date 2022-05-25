import numpy as np
from itertools import combinations_with_replacement
from functools import partial
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex import Document, Section
from latex import create_pdf
import sys

class TermNode:

    def __init__(self, value):
        self.left = None
        self.right = None
        self.leaf = True
        self.value = value

    def split(self, op_list):

        for _ in range(len(op_list)):
            op = np.random.choice(op_list, replace=False)
            result = op.split(self.value)
            if result is None:
                continue
            self.left = TermNode(result[0])
            self.right = TermNode(result[1])
            self.value = op.symbol
            self.leaf = False
            return True

        return False

    def to_string(self, root=True):

        if self.leaf:
            return str(self.value)
        else:
            content = self.left.to_string(False) + self.value + self.right.to_string(False)
            if root:
                return content
            else:
                return "(" + content + ")"


class Operation:

    def __init__(self, symbol, split_function):
        self.symbol = symbol
        self.split_function = split_function

    def split(self, value):
        return self.split_function(value)


def factorise(value, include_one=False):
    factors = [(n, value // n) for n in range(2, int(value ** 0.5) + 1) if value % n == 0]
    if include_one:
        factors.append((1, value))
    return factors


def multiply(value, difficulty_filter=None):
    factors = factorise(value)
    if difficulty_filter is not None:
        filtered = list(filter(difficulty_filter, factors))
    else:
        filtered = factors
    k = len(filtered)
    if k == 0:
        return None
    else:
        return filtered[np.random.randint(k)]


def divide(value, allowed_divisors):
    divisor = np.random.choice(allowed_divisors)
    return value * divisor, divisor


def easy_divide(value):
    if value > 12:
        return None
    divisor = np.random.randint(2, 12)
    return value * divisor, divisor


def multiply_factor_leq_12(value):
    return multiply(value, lambda factors: factors[0] <= 12 or factors[1] <= 12)


def divide_divisor_leq_12(value):
    return divide(value, [i + 1 for i in range(1, 12)])


def divide_divisor_bounded(value):
    return divide(value, [i + 1 for i in range(1, min(12, 144 // value))])


def multiply_predefined(value, multiply_map):
    if value not in multiply_map:
        return None
    else:
        factors = multiply_map[value]
        return factors[np.random.randint(len(factors))]


def get_predefined_multiply_factors():
    result = dict()
    # 12x12 times tables (excluding 1)
    for i, j in combinations_with_replacement([k+1 for k in range(1, 12)], 2):
        prod = i * j
        if prod not in result:
            result[prod] = list()
        result[prod].append((i, j))

    # We'll allow 'easy' multiplications up to a bound of 1000
    for i in ([2] + [k * 10 for k in range(1, 100)]):
        for j in range(13, 1000 // i):
            prod = i * j
            if prod not in result:
                result[prod] = list()
            result[prod].append((i, j))

    # We'll allow 'easy-ish' multiplications up to a bound of 200
    for i in [3, 4, 5, 11, 15]:
        for j in range(13, 200 // i):
            prod = i * j
            if prod not in result:
                result[prod] = list()
            result[prod].append((i, j))


    return result


def add(value):
    if value <= 1:
        return None
    left = value - np.random.randint(1, value-1)
    return left, value-left


def subtract(value):
    right = np.random.randint(100)
    return value+right, right


def sqrt(value):
    if (value ** 0.5).is_integer():
        return ()


def encode_phrase(phrase):
    encoding = dict()
    for char in phrase:
        if char not in encoding:
            encoding[char] = np.random.randint(0, 100)
    return encoding


def generate_eqn(op_list, target, max_terms=2):
    init_node = TermNode(target)
    init_node.split(op_list)
    init_node.left.split(op_list)
    init_node.right.split(op_list)
    return init_node.to_string()


class AmsMath(Environment):
    packages = [Package("amsmath")]


def run(phrase, pdf_title, pdf_name="mathspell"):
    predefined_multiply_factors = get_predefined_multiply_factors()
    op_list = [
        Operation("*", partial(multiply_predefined, multiply_map=predefined_multiply_factors)),
        Operation("/", easy_divide),
        Operation("+", add),
        Operation("-", subtract)
    ]
    phrase = phrase.lower()
    phrase_words = phrase.split()
    phrase_letters = "".join(phrase_words)
    encoding = encode_phrase(phrase_letters)
    equations = [generate_eqn(op_list, encoding[c]) for c in phrase_letters]

    doc = Document()
    with doc.create(Section("Test")):
        with doc.create(AmsMath()):
            test = ""

    create_pdf(pdf_title, pdf_name, phrase_words, encoding, equations)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
