import sys
import os.path
import itertools
import string
from stemming.porter2 import stem
from functools import lru_cache

@lru_cache(maxsize=4096)
def memoized_stem(word):
    return stem(word)

def get_file_lines(filename):
    with open(filename) as f:
        return [line.rstrip("\n") for line in f]

# Excludes punctuation too
def get_file_tokens(filename, filter_set=None):
    lines = []
    with open(filename) as f:
        tokLists = map(lambda l:
            # Case folding, strip punctuation, and split by spaces
            l.lower().translate(
                str.maketrans('', '', string.punctuation)
            ).split(),
            f
        )

        toks = set(itertools.chain.from_iterable(tokLists))

        if filter_set:
            toks = filter(lambda t: t not in filter_set, toks)

        return list(map(memoized_stem, toks))

def main():
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Filename '%s' does not exist" % filename)
        return

    stopwords = set(get_file_lines("englishST.txt"))

    tokens = get_file_tokens(filename, filter_set=stopwords)
    print(len(tokens))

if __name__ == "__main__":
    main()