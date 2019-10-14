import sys
import os.path
import itertools
import string
from stemming.porter2 import stem
from typing import List
from functools import lru_cache
import xml.etree.ElementTree as etree

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

def get_file_docs(filename):
    with open(filename) as f:
        xml = etree.fromstring("<root>" + f.read() + "</root>")

    docs = []
    for node in xml.iter("DOC"):
        d = Doc.from_xml_node(node)
        docs.append(d)

    return docs

    # ts = set()
    # for doc in xml.iter("DOC"):
    #     ts = ts.union(Doc.get_xml_node_tags(doc))
    # print(ts)

def main():
    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print("Filename '%s' does not exist" % filename)
        return

    docs = get_file_docs(filename)
    stopwords = set(get_file_lines("englishST.txt"))

    for doc in docs:
        doc.tokenize(stopwords)
        print(doc, doc.tokens)

    # tokens = get_file_tokens(filename, filter_set=stopwords)
    # print(len(tokens))

if __name__ == "__main__":
    main()