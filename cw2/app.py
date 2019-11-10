import argparse
import os.path
import sys

from collections import defaultdict
from results import read_results, read_relevant
from util import eprint

class TTDS():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='TTDS Coursework 2',
            usage='''app.py <command> [<args>]

The most commonly used commands are:
    parse   Parse dem files
''')

        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)(sys.argv[2:])

    def parse(self, args):
        parser = argparse.ArgumentParser(
            description='parse dem files')

        # parser.add_argument('tweetfile', help="prefix file to use")
        # parser.add_argument('--refresh-dic', action='store_true')

        args = parser.parse_args(args)

        with open("S1.results", "r") as f:
            retrieved = read_results(f)
        with open("qrels.txt") as f:
            relevant = read_relevant(f)

        assert len(retrieved) == len(relevant)

        means = defaultdict(float)
        columns = ["", "P@10", "R@50", "r-Precision", "AP", "nDCG@10", "nDCG@20"]
        for col in columns:
            if col != "":
                print("\t" + col, end="")
        print()

        for q in retrieved.keys():
            scores = get_scores(retrieved[q], relevant[q])
            # eprint("scores for", q, "is", scores)
            for col in columns:
                if col == "":
                    print(q, end="")
                else:
                    score = scores[col]
                    means[col] += score
                    print("\t{0:.2f}".format(score), end="")
            print()

        for col in columns:
            if col == "":
                print("mean", end="")
            else:
                score = means[col] / len(retrieved)
                print("\t{0:.2f}".format(score), end="")
        print()



def precision_at_k(retrieved, relevant, k):
    retrieved_docids = list(map(lambda d: d["doc_number"], retrieved))
    relevant_docids = list(map(lambda t: t[0], relevant))

    intersection_k = set(retrieved_docids[:k]).intersection(set(relevant_docids))
    precision = len(intersection_k) / len(retrieved)
    return precision

def average_precision(retrieved, relevant):
    retrieved_docids = list(map(lambda d: d["doc_number"], retrieved))
    relevant_docids = list(map(lambda t: t[0], relevant))

    ps = 0
    for d in retrieved:
        docnum = d["doc_number"]
        rank = d["doc_rank"]
        if docnum in relevant_docids:
            ps += precision_at_k(retrieved, relevant, rank)
    return ps / len(relevant_docids)


def get_scores(retrieved, relevant):
    retrieved_docids = list(map(lambda d: d["doc_number"], retrieved))
    relevant_docids = list(map(lambda t: t[0], relevant))

    precision_10 = precision_at_k(retrieved, relevant, 10)
    precision_r = precision_at_k(retrieved, relevant, len(relevant))

    intersection_50 = set(retrieved_docids[:50]).intersection(set(relevant_docids))
    recall = len(intersection_50) / len(relevant)

    ap = average_precision(retrieved, relevant)

    return {
        "P@10": precision_10,
        "R@50": recall,
        # "f1": (2 * precision * recall) / (precision + recall)
        "r-Precision": precision_r,
        "AP": ap,
        "nDCG@10": 1,
        "nDCG@20": 1
    }



if __name__ == "__main__":
    TTDS()
