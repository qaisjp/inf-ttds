import argparse
import sys
import os.path
import pickle
from pprint import pprint

from doc import Doc, search
from indexing import build_index, tokenize, get_file_docmap
from queries import QueryPart, read_query_file, parse_query_str
from util import get_file_lines

STOPWORDS_FILE = "englishST.txt"

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_filename", type=str,
                        help='the filename of the sample')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query_str', nargs='?', type=str,
                        help='query string to use')
    group.add_argument('--queries-from', dest='queries_filename', type=str,
                        help='file to read queries from')

    parser.add_argument("--print-doc", dest="print_doc", type=str, help="doc to print")

    return parser.parse_args()

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
            # Combine headline and text
            text = doc.headline + " " + doc.text

            # tokenize
            toks = tokenize(text, stopwords)

            # save it
            doc.tokens = list(toks)

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

    if args.print_doc is not None:
        doc = docmap[args.print_doc]
        print(doc)
        print(doc.tokens)
        return

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
