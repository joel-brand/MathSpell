import numpy as np
import math


class Operation:

    def __init__(self, symbol, split_function, do_not_expand=False):
        self.symbol = symbol
        self.split_function = split_function
        self.do_not_expand = do_not_expand

    def split(self, value):
        result = self.split_function(value)
        if result is not None:
            return result + [self.symbol, self.do_not_expand]


class OperationList:

    def __init__(self):
        self.all_operations = list()
        self.all_probabilities = list()

    def add_operation(self, operation, probability):
        self.all_operations.append(operation)
        try:
            self.all_probabilities.append(float(probability))
        except ValueError:
            raise "Probability must be a valid decimal"

    def split(self, value):
        for operation in np.random.choice(self.all_operations, size=len(self.all_operations), replace=False,
                                          p=self.all_probabilities):
            result = operation.split(value)
            if result is not None:
                return result


class OperandList:
    TYPE_MULTIPLICATION = "*"
    TYPE_DIVISION = "/"
    TYPE_ADDITION = "+"
    TYPE_SUBTRACTION = "-"
    TYPE_EXPONENTIATION = "^"
    TYPE_INVERSE_EXPONENTIATION = "^/"  # Have this as a separate type for now, to keep all the arithmetic as integers

    def __init__(self, list_type):
        self.list_type = list_type
        self.all_operand_pairs = list()

    def add_operand_pair(self, op1, op2):
        self.all_operand_pairs.append((op1, op2))

    def make_operation(self):
        if self.list_type == OperandList.TYPE_MULTIPLICATION:
            return self.make_multiplication_operation()
        elif self.list_type == OperandList.TYPE_DIVISION:
            return self.make_division_operation()
        elif self.list_type == OperandList.TYPE_ADDITION:
            return self.make_addition_operation()
        elif self.list_type == OperandList.TYPE_SUBTRACTION:
            return self.make_subtraction_operation()
        elif self.list_type == OperandList.TYPE_EXPONENTIATION:
            return self.make_exponentiation_operation()
        elif self.list_type == OperandList.TYPE_INVERSE_EXPONENTIATION:
            return self.make_inverse_exponentiation_operation()

    def make_multiplication_operation(self):
        def split(value):
            all_factorisations = factorise(value)
            for (fact_1, fact_2) in np.random.permutation(all_factorisations):
                for (op_1, op_2) in self.all_operand_pairs:
                    if (op_1.matches(fact_1) and op_2.matches(fact_2)) or (
                            op_1.matches(fact_2) and op_2.matches(fact_1)):
                        return [fact_1, fact_2]

        return Operation("*", split)

    def make_division_operation(self):
        def split(value):
            for (op_1, op_2) in np.random.permutation(self.all_operand_pairs):
                for divisor in op_2.get_shuffled_range():
                    if op_1.matches(value * divisor):
                        return [value * divisor, divisor]

        return Operation("/", split)

    def make_addition_operation(self):
        def split(value):
            for (op_1, op_2) in np.random.permutation(self.all_operand_pairs):
                left_low = max(value - op_2.high, 0)
                left_high = max(value - op_2.low, 0)
                for left in op_1.get_shuffled_intersecting_range(left_low, left_high):
                    right = value - left
                    if op_2.matches(right):
                        return [left, right]

        return Operation("+", split)

    def make_subtraction_operation(self):
        def split(value):
            for (op_1, op_2) in np.random.permutation(self.all_operand_pairs):
                left_low = value + op_2.low
                left_high = value + op_2.high
                for left in op_1.get_shuffled_intersecting_range(left_low, left_high):
                    right = left - value
                    if op_2.matches(right):
                        return [left, right]

        return Operation("-", split)

    def make_exponentiation_operation(self):
        def split(value):
            for (op_1, op_2) in np.random.permutation(self.all_operand_pairs):
                for exponent in op_2.get_shuffled_range():
                    base = value ** (1/exponent)
                    if not base.is_integer():
                        continue
                    base = int(base)
                    if op_1.matches(base):
                        return [base, exponent]
        return Operation("^", split, do_not_expand=True)

    def make_inverse_exponentiation_operation(self):
        def split(value):
            for (op_1, op_2) in np.random.permutation(self.all_operand_pairs):
                for exponent in op_2.get_shuffled_range():
                    base = value ** exponent
                    if not base.is_integer():
                        continue
                    base = int(base)
                    if op_1.matches(base):
                        return [base, 1/exponent]
        return Operation("^", split, do_not_expand=True)


class Operand:

    def __init__(self, low, high, step=1):
        self.low = low
        self.high = high
        self.step = step

    def matches(self, value):
        if value < self.low:
            return False
        if value > self.high:
            return False
        if value % self.step != 0:
            return False
        return True

    @staticmethod
    def parse(val_string):
        if type(val_string) != str:
            raise "Invalid type cannot be parsed into operand"
        if val_string == "":
            raise "Operand string cannot be empty"
        if val_string.isdecimal():
            number = int(val_string)
            return Operand(number, number, 1)
        else:
            if not (val_string[0] == "[" and val_string[-1] == "]"):
                raise "Operand string must be integer or a list specifier"
            try:
                list_tokens = list(map(int, val_string[1:-1].split(",")))
                k = len(list_tokens)
                if k not in [2, 3]:
                    raise "Invalid operand list specifier"
                return Operand(*list_tokens)
            except ValueError:
                raise "Operand list specifier must contain integers"

    def get_shuffled_range(self):
        return np.random.permutation(range(self.low, self.high + 1, self.step))

    def get_shuffled_intersecting_range(self, low, high):
        if self.step == 1:
            intersection_range = range(max(self.low, low), min(self.high, high) + 1)
        else:
            intersection_low = math.ceil(max(self.low, low) / self.step) * self.step
            intersection_high = math.ceil(min(self.high, high) / self.step) * self.step
            intersection_range = range(intersection_low, intersection_high + 1, self.step)
        return np.random.permutation(intersection_range)


def factorise(value, include_one=False):
    factors = [(n, value // n) for n in range(2, int(value ** 0.5) + 1) if value % n == 0]
    if include_one:
        factors.append((1, value))
    return factors


def parse_operand_list(file_name):
    with open(file_name, "r") as f:
        header = f.readline().split()
        if len(header) != 1:
            raise "Malformed header in {} - expected one token".format(file_name)
        list_type = header[0]
        result = OperandList(list_type)
        for line_no, line in enumerate(f):
            ops = line.rstrip().split(";")
            if len(ops) != 2:
                raise "Malformed line ({}) in {} - expected two tokens".format(line_no, file_name)
            op1 = Operand.parse(ops[0])
            op2 = Operand.parse(ops[1])
            result.add_operand_pair(op1, op2)
    return result


def parse_operation_list(file_name, all_operations):
    result = OperationList()
    with open(file_name, "r") as f:
        for line_no, line in enumerate(f):
            tokens = line.rstrip().split(";")
            if len(tokens) != 2:
                raise "Malformed line ({}) in {} - expected two tokens".format(line_no, file_name)
            operation_file = tokens[0]
            operation_probability = tokens[1]
            if operation_file not in all_operations:
                # Only parse the operation file if we haven't already done so
                all_operations[operation_file] = parse_operand_list(operation_file).make_operation()
            result.add_operation(all_operations[operation_file], operation_probability)
    if not sum(result.all_probabilities) == 1:
        raise "Operation probabilities must sum to 1"
    return result


def add(value):
    if value <= 1:
        return None
    left = value - np.random.randint(1, value - 1)
    return left, value - left


def subtract(value):
    right = np.random.randint(100)
    return value + right, right


def sqrt(value):
    if (value ** 0.5).is_integer():
        return ()
