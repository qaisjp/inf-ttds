import string
import xml.etree.ElementTree as etree

from collections import namedtuple
from doc import Doc
from functools import lru_cache
from stemming.porter2 import stem
from util import safe_int

@lru_cache(maxsize=4096)
def memoized_stem(word):
    return stem(word)

def build_index(docmap):
    index = {}
    for doc in docmap.values():
        positions = {}

        for idx, token in enumerate(doc.tokens):
            if token not in positions:
                positions[token] = []

            positions[token].append(idx)

        for token, positions in positions.items():
            if token not in index:
                index[token] = {}

            index[token][doc.num] = positions

    return index

def non_alpha_to_space(l):
    if l.isalpha():
        return l
    else:
        return " "

def tokenize(text, filter_set=[]):
    # To lower
    toks = text.lower()

    # Strip punctuation
    #
    # When doing a search for `#1(san, francisco)`,
    # a doc containing "San Francisco-based" was missing
    # so I decided to put spaces in place of punctuation instead of ""
    # spaces = len(string.punctuation) * " "
    # toks = toks.translate(str.maketrans(string.punctuation, spaces))
    #
    # Also decided to just only keep letters rather than numbers too
    toks = "".join(map(non_alpha_to_space, toks))

    # Actually be list of words
    toks = toks.split()

    # Filter out certain toks
    toks = filter(lambda t: t not in filter_set, toks)

    # stemmed tokens
    toks = map(memoized_stem, toks)

    return list(toks)

def get_file_docmap(filename):
    with open(filename) as f:
        xml = etree.fromstring("<root>" + f.read() + "</root>")

    docs = {}
    for node in xml.iter("DOC"):
        d = Doc.from_xml_node(node)

        if d.num in docs:
            print("Clash d.num in docs, %d" % d.num)
            sys.exit(1)

        docs[d.num] = d

    return docs

    # ts = set()
    # for doc in xml.iter("DOC"):
    #     ts = ts.union(Doc.get_xml_node_tags(doc))
    # print(ts)

def index_to_str(index):
    lines = []
    for token in sorted(index.keys()):
        lines.append(token + ":")

        docpos = index[token]
        docs = sorted(docpos.keys(), key=safe_int)
        for doc in docs:
            positions = ",".join(map(str,sorted(docpos[doc])))
            lines.append("\t{}: {}".format(doc, positions))
    return "\n".join(lines)
