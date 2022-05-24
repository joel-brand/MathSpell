from pylatex.base_classes import Environment, LatexObject
from pylatex.package import Package
from pylatex import Document, Enumerate, TikZ, TikZDraw, TikZCoordinate, TikZUserPath, TikZOptions
from pylatex.math import Math


class ExtendedTikZUserPath(TikZUserPath):

    def __init__(self, path_type, options=None, text=None):
        super().__init__(path_type, options)
        self.text = text

    def dumps(self):
        """Return path command representation."""
        ret_str = super().dumps()
        if self.text is not None:
            ret_str += "{" + self.text + "}"
        return ret_str


class MultiCols(Environment):
    packages = [Package("multicol")]


def create_pdf(phrase_encoding, equations_list):

    doc = Document()

    # Print equations in  two columns
    with doc.create(MultiCols(arguments="2")):
        with doc.create(Enumerate()) as enum:
            for equation in equations_list:
                enum.add_item(Math(data=[equation], inline=True))

    # Print the encoding
    # with doc.create(TikZ()) as pic:
    #     pic.append(TikZDraw([
    #         TikZCoordinate(0, 0),  # "(0,0)",
    #         "--",
    #         "++(1,0)",
    #         ExtendedTikZUserPath("node", TikZOptions(["midway", "below"]), "test")
    #     ]))

    doc.generate_pdf("test", clean_tex=False)