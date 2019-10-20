import argparse
import sys
import os.path
import pickle
from pprint import pprint, pformat

from doc import Doc, search, SearchResult
from indexing import build_index, tokenize, get_file_docmap, index_to_str
from queries import QueryPart, read_query_file, parse_query_str
from util import get_file_lines, safe_int, eprint

STOPWORDS_FILE = "englishST.txt"

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_filename", type=str,
                        help='the collection filename')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query_str', nargs='?', type=str,
                        help='query string to use')
    group.add_argument('--queries-from', dest='queries_filename', type=str,
                        help='file to read queries from')

    parser.add_argument("--print-doc", dest="print_doc", type=str, help="doc to print")

    parser.add_argument("--limit", default=1000, type=int, help="default number of results to return per query")
    parser.add_argument("--places", dest="decimal_places", type=int, help="decimal places for index.txt. if tfidf is set, this is 4, otherwise 0. or you can override")

    parser.add_argument("--tfidf", dest="use_tfidf", action='store_true', help="use term weighting")
    parser.add_argument("--debug", action='store_true', help="debug output")
    parser.add_argument("--refresh", action='store_true', help="refresh index")

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

        if len(results) > args.limit:
            results = list(results)[:args.limit]

        for result in results:
            print(output_format.format(key, result.doc, result.rank))

        if args.debug:
            eprint()
            eprint()


if __name__ == "__main__":
    main()
