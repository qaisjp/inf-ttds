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

        negated = s.startswith("NOT ")
        if negated:
            s = s[4:]

        quoted = s.startswith("\"") and s.endswith("\"")
        if quoted:
            s = s[1:-1]

        proxim_match = re_proximity.match(s)
        if proxim_match:
            distance, text_a, text_b = proxim_match.groups()
            s = (text_a, text_b) # TODO: preprocess `text_a` and `text_b`
        else:
            distance = None
            # TODO: preprocess `s`

        parts[i] = QueryPart(s, negated, quoted, int(distance))

    return (chosen_op, parts)

class QueryPart():
    text: str
    negated: bool
    phrasal: bool
    distance: int

    def __init__(self, text, negated, phrasal, distance):
        self.text = text
        self.negated = negated
        self.phrasal = phrasal
        self.distance = distance

        if phrasal and distance is not None:
            print("Phrasal and distance are mutually exclusive fields:", self)
            sys.exit(1)
        elif distance == 0:
            print("Invalid distance 0:", self)

    def __members(self):
        return (self.text, self.negated, self.phrasal, self.distance)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self):
        return hash(self.__members())

    def __str__(self):
        s = "QueryPart("
        if self.negated:
            s += "NOT "

        if self.phrasal:
            s += "\"" + self.text + "\""
        elif self.distance is not None:
            s += "#" + str(self.distance) + "(" + self.text[0] + ", " + self.text[1] + ")"
        else:
            s += self.text

        return s + ")"

    def __repr__(self):
        return self.__str__()

def search(docmap, index, query):
    op, parts = query

    inclusions = {}
    exclusions = {}

    fullparts = [] # TODO
    nextindex = index

    for i, qpart in enumerate(parts):
        found = False
        if qpart.phrasal:
            # full text search
            fullparts.append(qpart)
            continue
        elif qpart.distance is not None:
            term_a, term_b = qpart.text

            # Do both these terms appear the entire sample?
            if term_a in index and term_b in index:
                docs_a = index[term_a]
                docs_b = index[term_b]

                # Pluck out position lists where docs match
                # ( doc_num, term_a_positions, term_b_positions )
                matching_docs = [
                    (doc_a, term_a_positions, term_b_positions)
                    for doc_a, term_a_positions in docs_a
                    for doc_b, term_b_positions in docs_b
                    if doc_a == doc_b
                ]

                nearby_docs = []
                for doc, positions_a, positions_b in matching_docs:
                    doc_pos_pairs = [
                        (pos_a, pos_b)
                        for pos_a in positions_a
                        for pos_b in positions_b
                    ]

                    for pos_a, pos_b in doc_pos_pairs:
                        # We don't use a list comprehension here
                        # so that we can quickly short-circuit once
                        # we have confirmed that we're near
                        if abs(pos_a - pos_b) <= qpart.distance:
                            nearby_docs.append(doc)
                            break

                entries = nearby_docs
                found = True

        if qpart.text in index:
            entries = [index[qpart.text]]
            found = True

        if qpart.negated:
            found = not found

        if found:
            inclusions[qpart] = entries
        else:
            exclusions[qpart] = entries

    if op == "OR":
        assert(len(exclusions) == 0)
        return inclusions
    else:
        pass # Operation is AND

    # If inclusions is empty, but exclusions contains stuff
    # we want to set inclusions to entire document set
    if len(inclusions) == 0 and len(exclusions) > 0:
        # This will not work since each value in the index is a list of entries
        # inclusions = map(lambda doc: entry.doc, index.values())
        inclusions = map(lambda doc: doc.num, docmap.values())
    else:
        inclusions = itertools.chain.from_iterable(inclusions.values())

    exclusions = itertools.chain.from_iterable(exclusions.values())

    return list(set(inclusions) - set(exclusions))

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
    for pair in queries:
        key, q = pair
        pprint(pair)
        pprint(search(docmap, index, q))
        print()

if __name__ == "__main__":
    main()
