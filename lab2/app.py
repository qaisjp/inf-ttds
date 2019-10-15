import sys
import os.path
import itertools
import string
from stemming.porter2 import stem
from typing import List
from functools import lru_cache
import xml.etree.ElementTree as etree
from collections import namedtuple

@lru_cache(maxsize=4096)
def memoized_stem(word):
    return stem(word)

def get_file_lines(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]

class Doc():
    num : int
    headline: str
    text : str

    tokens : List[str]

    @staticmethod
    def from_xml_node(node):
        d = Doc()
        d.num = int(node.find("DOCNO").text)
        d.headline = node.find("HEADLINE").text.strip()
        d.text = node.find("TEXT").text.strip()
        return d

    @staticmethod
    def get_xml_node_tags(doc_node):
        tags = []
        for node in doc_node:
            tags.append(node.tag.lower())
            print(node, node.tag.lower())
        return set(tags)

    def tokenize(self, filter_set=[]):
        # Combine headline and text
        text = self.headline + " " + self.text

        # To lower
        toks = text.lower()

        # Strip punctuation
        toks = toks.translate(
            str.maketrans('', '', string.punctuation)
        )

        # Actually be list of words
        toks = toks.split()

        # Filter out certain toks
        toks = filter(lambda t: t not in filter_set, toks)

        # stemmed tokens
        toks = map(memoized_stem, toks)

        # save it
        self.tokens = list(toks)

    def __str__(self):
        return "Doc(num=%d, headline=%s, text=[len:%d])" % (self.num, self.headline, len(self.text))

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

IndexEntry = namedtuple("IndexEntry", ("doc", "positions"))

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

def main():
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Filename '%s' does not exist" % filename)
        return

    docmap = get_file_docmap(filename)
    stopwords = set(get_file_lines("englishST.txt"))

    for doc in docmap.values():
        doc.tokenize(stopwords)

    index = build_index(docmap)
    # print(len(docmap.keys()))
    # print(docmap[3936].text)
    # print(index)

    # tokens = get_file_tokens(filename, filter_set=stopwords)
    # print(len(tokens))

if __name__ == "__main__":
    main()
