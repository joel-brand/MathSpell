from pylatex.base_classes import Environment, LatexObject
from pylatex.package import Package
from pylatex import Document, Enumerate, TikZ, TikZDraw, TikZCoordinate, TikZUserPath, TikZOptions, VerticalSpace
from pylatex.math import Math
from pylatex.utils import bold
from string import ascii_lowercase
import numpy as np

class ExtendedTikZUserPath(TikZUserPath):

    def __init__(self, path_type, options=None, text=None):
        super().__init__(path_type, options)
        self.text = text

    def dumps(self):
        ret_str = super().dumps()
        if self.text is not None:
            ret_str += "{" + self.text + "}"
        return ret_str


class MultiCols(Environment):
    packages = [Package("multicol")]


def create_pdf(title, pdf_name, phrase_words, phrase_encoding, equations_list):

    doc = Document(page_numbers=False)

    if title is not None:
        doc.append(bold(title))

    # Print equations in  two columns
    with doc.create(MultiCols(arguments="2")):
        with doc.create(Enumerate()) as enum:
            for equation in equations_list:
                enum.add_item(Math(data=[equation], inline=True, escape=False))

    # Print the blanks
    doc.append(VerticalSpace("1cm"))
    MAX_COL = 15
    col = 0
    row = 0
    label = 0
    with doc.create(TikZ()) as pic:
        for word in phrase_words:
            if col + (1.5*len(word)) > MAX_COL:
                row -= 1.5
                col = 0
            elif col > 0:
                col += 1
            for c in word:
                label += 1
                col += 1.5
                pic.append(TikZDraw([
                    TikZCoordinate(col, row),  # "(0,0)",
                    "--",
                    "++(1,0)",
                    ExtendedTikZUserPath("node", TikZOptions(["midway", "below"]), str(label))
                ]))

    # Print the code
    doc.append(VerticalSpace("1cm"))
    with doc.create(MultiCols(arguments="3")):
        with doc.create(Enumerate(enumeration_symbol=r"\Alph*")) as enum:
            for c in ascii_lowercase:
                if c in phrase_encoding:
                    enum.add_item(phrase_encoding[c])
                else:
                    enum.add_item(np.random.randint(100))

    doc.generate_pdf(pdf_name, clean_tex=False)