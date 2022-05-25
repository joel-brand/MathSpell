import numpy as np
from latex import create_pdf
from term_tree import TermNode
from operations import parse_operation_list
from collections import deque


def encode_phrase(phrase):
    encoding = dict()
    for char in phrase:
        if char not in encoding:
            encoding[char] = np.random.randint(0, 100)
    return encoding


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


def generate(cached_operation_list, phrase, op_file, pdf_title="", pdf_name="math_spell"):

    splitter = parse_operation_list(op_file, cached_operation_list)

    phrase = phrase.lower()

    phrase_words = phrase.split()
    phrase_letters = "".join(phrase_words)
    encoding = encode_phrase(phrase_letters)

    equations = [generate_eqn(splitter, encoding[c]) for c in phrase_letters]

    create_pdf(pdf_title, pdf_name, phrase_words, encoding, equations)


if __name__ == '__main__':
    generate(dict(), "this is a test", "example/example.oplist", "Math 8E 26th May")
    # while True:
    #     operation_list = dict()
    #     cmd = shlex.split(prompt_toolkit.prompt("> "))
    #     if len(cmd) == 0:
    #         continue
    #     if cmd[0] == "exit":
    #         break
    #     if len(cmd) > 4:
    #         print("Invalid command - format should be " +
    #               "'\"<PHRASE>\" \"<OP_FILE>\" \"<(Optional)PDF_TITLE>\" \"<(Optional)PDF_NAME>\"")
    #     generate(operation_list, *cmd)
