import numpy as np
from latex import create_pdf
from term_tree import TermNode
from operations import parse_operation_list
from collections import deque
from string import ascii_lowercase
import shlex
import prompt_toolkit
import os.path


def encode_phrase(phrase):
    available = [i for i in range(100)]
    np.random.shuffle(available)
    return {c: available.pop() for c in ascii_lowercase}
    # encoding = dict()
    # available = [i for i in range(100)]
    # np.random.shuffle(available)
    # for char in phrase:
    #     if char not in encoding:
    #         encoding[char] = available.pop()  # np.random.randint(0, 100)
    # return encoding


def generate_eqn(splitter, target, max_terms=4):
    init_node = TermNode(target)
    queue = deque()
    queue.append(init_node)
    terms = 1
    while terms < max_terms and len(queue) > 0:
        next_node = queue.popleft()
        next_node.split(splitter)
        if next_node.leaf:
            # Failed to split
            continue
        if not next_node.left.locked:
            queue.append(next_node.left)
        if not next_node.right.locked:
            queue.append(next_node.right)
        terms += 1
    init_node.use_large_division_at_top()
    return init_node.to_string()


def generate(splitter, phrase, pdf_title=None, pdf_name=None):

    phrase = phrase.lower()

    phrase_words = phrase.split()
    phrase_letters = "".join(phrase_words)
    encoding = encode_phrase(phrase_letters)

    if pdf_name is None:
        i = 0
        pdf_name = "math_spell"
        while os.path.isfile(pdf_name + ".pdf"):
            i += 1
            pdf_name = "math_spell{0}".format(i)

    equations = [generate_eqn(splitter, encoding[c]) for c in phrase_letters]

    create_pdf(pdf_title, pdf_name, phrase_words, encoding, equations)


if __name__ == '__main__':
    cached_operations = dict()
    current_splitter = None
    while True:
        cmd = shlex.split(prompt_toolkit.prompt("> "))
        k = len(cmd)
        if k == 0:
            continue
        elif cmd[0] == "$exit":
            break
        elif cmd[0] == "$op_file":
            if k != 2:
                print("Invalid command - \\op_file takes one argument")
                continue
            op_file = cmd[1]
            current_splitter = parse_operation_list(op_file, cached_operations)
        else:
            if current_splitter is None:
                print("Please set an operations file first")
                continue
            if k > 3:
                print("Invalid command - format should be " +
                      "'\"<PHRASE>\" \"<(Optional)PDF_TITLE>\" \"<(Optional)PDF_NAME>\"")
            generate(current_splitter, *cmd)
