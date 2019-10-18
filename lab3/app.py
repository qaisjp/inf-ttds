import argparse
import sys
import os.path
import itertools
import pickle
import xml.etree.ElementTree as etree
from typing import List
from pprint import pprint

from indexing import IndexEntry, build_index, tokenize
from queries import QueryPart, read_query_file, parse_query_str
from util import safe_int, get_file_lines

STOPWORDS_FILE = "englishST.txt"

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

        # tokenize
        toks = tokenize(text, filter_set)

        # save it
        self.tokens = list(toks)

    def __str__(self):
        return "Doc(num=%s, headline=%s, text=[len:%d])" % (self.num, self.headline, len(self.text))

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

def search(docmap, index, query):
    op, parts = query

    inclusions = {}
    exclusions = {}

    fullparts = [] # TODO
    nextindex = index

    for i, qpart in enumerate(parts):
        found = False
        if qpart.phrasal or (qpart.distance is not None):
            term_a, term_b = qpart.text

            # Do both these terms appear the entire sample?
            if term_a in index and term_b in index:
                entries_a = index[term_a]
                entries_b = index[term_b]

                # Pluck out position lists where docs match
                # ( doc_num, term_a_positions, term_b_positions )
                matching_docs = [
                    (doc_a, term_a_positions, term_b_positions)
                    for doc_a, term_a_positions in entries_a
                    for doc_b, term_b_positions in entries_b
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
                        if qpart.phrasal:
                            if (pos_b - pos_a) == 1:
                                nearby_docs.append(doc)
                                break
                        else:
                            if abs(pos_a - pos_b) <= qpart.distance:
                                nearby_docs.append(doc)
                                break

                docs = nearby_docs
                found = True
        elif qpart.text in index:
            docs = map(lambda entry: entry.doc, index[qpart.text])
            found = True
        else:
            print("Term '%s' not found" % qpart.text)
            continue

        if qpart.negated:
            found = not found

        if found:
            inclusions[qpart] = docs
        else:
            exclusions[qpart] = docs

    if op == "OR":
        assert(len(exclusions) == 0)
        inclusions = itertools.chain.from_iterable(inclusions.values())
        return sorted(set(inclusions), key=safe_int)
    else:
        pass # Operation is AND

    # If inclusions is empty, but exclusions contains stuff
    # we want to set inclusions to entire document set
    if len(inclusions) == 0 and len(exclusions) > 0:
        inclusions = map(
            lambda entries: [entry.doc for entry in entries], index.values())
        inclusions = itertools.chain.from_iterable(inclusions)
    else:
        # Since the entire document set is a list, we need to normalise
        # our original inclusion map to be a list, to make code common
        inclusions = inclusions.values()

        # common docs
        new_inclusions = None
        for ds in inclusions:
            if new_inclusions is None:
                new_inclusions = set(ds)
            else:
                new_inclusions = new_inclusions & set(ds)
        inclusions = new_inclusions

    exclusions = itertools.chain.from_iterable(exclusions.values())

    return sorted(set(inclusions) - set(exclusions), key=safe_int)

def main():
    stopwords = set(get_file_lines(STOPWORDS_FILE))

    args = read_args()
    if args.queries_filename:
        queries = list(map(
            lambda q: (q[0], parse_query_str(q[1], stopwords)),
            read_query_file(args.queries_filename)
        ))
    else:
        queries = [("1", parse_query_str(args.query_str, stopwords))]

    filename = args.sample_filename
    if not os.path.isfile(filename):
        print("Filename '%s' does not exist" % filename)
        return

    index_pickled_filename = filename + ".index"
    if not os.path.isfile(index_pickled_filename):
        print("Building a fresh index...")
        docmap = get_file_docmap(filename)

        for doc in docmap.values():
            doc.tokenize(stopwords)

        index = build_index(docmap)

        with open(index_pickled_filename, "wb") as f:
            print("Index built, saving to", index_pickled_filename, end="...")
            pickle.dump((docmap, index), f)
            print("done!")
    else:
        print("Reading index from", index_pickled_filename)
        print()
        with open(index_pickled_filename, "rb") as f:
            docmap, index = pickle.load(f)

    # print(docmap[3936].text)
    # print(index["pyramid"])
    for pair in queries:
        key, q = pair
        results = search(docmap, index, q)
        print(len(results), "documents, query: ", end="")
        pprint(pair)
        pprint(results)
        print()
        print()

if __name__ == "__main__":
    main()
