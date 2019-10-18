import string

from collections import namedtuple
from functools import lru_cache
from stemming.porter2 import stem

IndexEntry = namedtuple("IndexEntry", ("doc", "positions"))

@lru_cache(maxsize=4096)
def memoized_stem(word):
    return stem(word)

def build_index(docmap):
    index = {}
    for doc in docmap.values():
        doctoks = {}

        for idx, token in enumerate(doc.tokens):
            if token not in doctoks:
                doctoks[token] = []

            doctoks[token].append(idx)

        for token, positions in doctoks.items():
            if token not in index:
                index[token] = []

            entry = IndexEntry(doc.num, positions)
            index[token].append(entry)

    return index

def tokenize(text, filter_set=[]):
    # To lower
    toks = text.lower()

    # Strip punctuation
    #
    # When doing a search for `#1(san, francisco)`,
    # a doc containing "San Francisco-based" was missing
    # so I decided to put spaces in place of punctuation instead of ""
    spaces = len(string.punctuation) * " "
    toks = toks.translate(str.maketrans(string.punctuation, spaces))

    # Actually be list of words
    toks = toks.split()

    # Filter out certain toks
    toks = filter(lambda t: t not in filter_set, toks)

    # stemmed tokens
    toks = map(memoized_stem, toks)

    return list(toks)
