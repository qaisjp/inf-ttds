import argparse
import sys
import os.path
import pickle
from pprint import pprint, pformat

from doc import Doc, search, SearchResult
from indexing import build_index, tokenize, get_file_docmap, index_to_str
from queries import read_query_file, parse_query_str
from util import get_file_lines, safe_int, eprint

STOPWORDS_FILE = "englishST.txt"

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_filename", type=str,
                        help="Filename for the collection")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("query_str", nargs="?", type=str,
                        help="Query to use")
    group.add_argument("-f", "--queries-from", dest="queries_filename", type=str,
                        help="File to read queries from")

    parser.add_argument("-d", "--print-doc", dest="print_doc", type=str, help="Print the document associated with the number and immediately return. Query input is ignored but required")

    parser.add_argument("-l", "--limit", dest="limit", default=1000, type=int, help="Results to return per query. Negative values return all. Default: 1000")
    parser.add_argument("-p", "--places", dest="decimal_places", type=int, help="Decimal places to round to for rank output. Negative values don't round. Default: with tfidf, -1, otherwise 0")

    parser.add_argument("-t", "--tfidf", dest="use_tfidf", action="store_true", help="Enable term weighting (necessary for queries.ranked.txt)")
    parser.add_argument("-v", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-r", "--refresh", action="store_true", help="Forcefully refresh the index")

    return parser.parse_args()

def main():
    stopwords = set(get_file_lines(STOPWORDS_FILE))

    args = read_args()
    if args.queries_filename:
        queries = list(map(
            lambda q: (q[0], parse_query_str(q[1], stopwords, splitphrase=args.use_tfidf)),
            read_query_file(args.queries_filename)
        ))
    else:
        queries = [("1", parse_query_str(args.query_str, stopwords, splitphrase=args.use_tfidf))]

    filename = args.collection_filename
    if not os.path.isfile(filename):
        eprint("Filename '%s' does not exist" % filename)
        return

    index_pickled_filename = filename + ".index"
    if args.refresh or not os.path.isfile(index_pickled_filename):
        eprint("Building a fresh index...")
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
            eprint("Index built, saving to", index_pickled_filename, end="...")
            pickle.dump((docmap, index), f)
            eprint("done!")

        with open(index_pickled_filename+".txt", "w") as f:
            f.write(index_to_str(index) + "\n")
            eprint(index_pickled_filename+".txt", "updated!")

    else:
        eprint("Reading index from", index_pickled_filename)
        eprint()
        with open(index_pickled_filename, "rb") as f:
            docmap, index = pickle.load(f)

    if args.print_doc is not None:
        doc = docmap[args.print_doc]
        print(doc)
        print(doc.tokens)
        return

    if args.decimal_places is None:
        if args.use_tfidf:
            args.decimal_places = -1
        else:
            args.decimal_places = 0

    if args.decimal_places == -1:
        output_format = "{} 0 {} 0 {} 0"
    else:
        output_format = "{} 0 {} 0 {:." + str(args.decimal_places) + "f} 0"

    for pair in queries:
        key, q = pair
        results = search(docmap, index, q, args.use_tfidf)
        results = sorted(
            # sort by doc num ASC
            sorted(results, key=lambda d: safe_int(d.doc)),

            # and then by score DESC
            key=SearchResult.rank.fget, reverse=True
        )

        if args.debug:
            eprint(len(results), "documents, query: ", end="")
            eprint(pformat(pair))

        if args.limit >= 0 and len(results) > args.limit:
            results = list(results)[:args.limit]

        for result in results:
            print(output_format.format(key, result.doc, result.rank))

        if args.debug:
            eprint()
            eprint()


if __name__ == "__main__":
    main()
