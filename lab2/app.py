import argparse
import sys
import os.path
import itertools
import string
import pickle
import re
import xml.etree.ElementTree as etree
from stemming.porter2 import stem
from typing import List
from functools import lru_cache
from pprint import pprint
from collections import namedtuple

@lru_cache(maxsize=4096)
def memoized_stem(word):
    return stem(word)

def get_file_lines(filename):
    with open(filename) as f:
        return [line.rstrip() for line in f]

class Doc():
    num : str
    headline: str
    text : str

    tokens : List[str]

    @staticmethod
    def from_xml_node(node):
        d = Doc()
        d.num = node.find("DOCNO").text
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

def read_query_file(filename):
    with open(filename) as f:
        queries = []
        for line in f:
            key, query = line.split(" ", 1)
            queries.append(
                (key.rstrip(":"), query)
            )
        return queries

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_filename", type=str,
                        help='the filename of the sample')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query_str', nargs='?', type=str,
                        help='query string to use')
    group.add_argument('--queries-from', dest='queries_filename', type=str,
                        help='file to read queries from')

    return parser.parse_args()

def parse_query_str(query_str):
    ops = ["OR", "AND"]
    chosen_op = None

    # Determine operation
    for op in ops:
        if op in query_str:
            if chosen_op is not None:
                print("Multiple ops found in query:", query_str)
                sys.exit(1)

            chosen_op = op

            # split by op
            parts = query_str.split(op)
            if len(parts) != 2:
                print("Invalid query. Should be one OP in middle of query:", query_str)
                sys.exit(1)

    if chosen_op is None:
        parts = [query_str]
        chosen_op = "AND"

    re_proximity = re.compile("#(\d+)\((.*?), (.*?)\)")

    for i, s in enumerate(parts):
        s = str.strip(s)

        notted = s.startswith("NOT ")
        if notted:
            s = s[4:]

        quoted = s.startswith("\"") and s.endswith("\"")
        if quoted:
            s = s[1:-1]

        proxim_match = re_proximity.match(s)
        if proxim_match:
            distance, text_a, text_b = proxim_match.groups()
            s = {text_a, text_b} # TODO: preprocess `text_a` and `text_b`
        else:
            distance = None
            # TODO: preprocess `s`

        parts[i] = {
            "text": s,
            "not": notted,
            "fullphrase": quoted,
            "distance": distance,
        }

    return (chosen_op, parts)

def main():
    args = read_args()
    if args.queries_filename:
        queries = list(map(
            lambda q: (q[0], parse_query_str(q[1])),
            read_query_file(args.queries_filename)
        ))
    else:
        queries = [("1", parse_query_str(args.query_str))]

    filename = args.sample_filename
    if not os.path.isfile(filename):
        print("Filename '%s' does not exist" % filename)
        return

    index_pickled_filename = filename + ".index"
    if not os.path.isfile(index_pickled_filename):
        docmap = get_file_docmap(filename)
        stopwords = set(get_file_lines("englishST.txt"))

        for doc in docmap.values():
            doc.tokenize(stopwords)

        index = build_index(docmap)

        with open(index_pickled_filename, "wb") as f:
            pickle.dump((docmap, index), f)
    else:
        with open(index_pickled_filename, "rb") as f:
            docmap, index = pickle.load(f)

    # print(docmap[3936].text)
    # print(index["pyramid"])
    pprint(queries)

if __name__ == "__main__":
    main()
