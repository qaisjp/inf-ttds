import argparse
import os.path
import sys

from collections import defaultdict
from math import log2
from results import read_results, read_relevant
from util import eprint

class TTDS():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='TTDS Coursework 2',
            usage='''app.py <command> [<args>]

The most commonly used commands are:
    parse   Parse files
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
            description='parse files')

        # parser.add_argument('tweetfile', help="prefix file to use")
        # parser.add_argument('--refresh-dic', action='store_true')

        args = parser.parse_args(args)

        with open("qrels.txt") as f:
            relevant = read_relevant(f)

        columns = ["", "P@10", "R@50", "r-Precision", "AP", "nDCG@10", "nDCG@20"]

        orig_stdout = sys.stdout
        max_s = 6
        averages = defaultdict(list)
        for num in range(1, max_s + 1):
            fname = "S" + str(num)
            with open(fname + ".results", "r") as f:
                retrieved = read_results(f)
                assert len(retrieved) == len(relevant)

            outfile = open(fname + ".eval", "w")
            sys.stdout = outfile

            print("\t".join(columns))

            total = defaultdict(float)
            for q in retrieved.keys():
                scores = get_scores(retrieved[q], relevant[q])
                # eprint("scores for", q, "is", scores)
                for col in columns:
                    if col == "":
                        print(q, end="")
                    else:
                        score = scores[col]
                        total[col] += score
                        print("\t{0:.3f}".format(score), end="")
                print()

            for col in columns:
                if col == "":
                    print("mean", end="")
                    averages[fname].append(fname)
                else:
                    score = total[col] / len(retrieved)
                    score_str = "{0:.3f}".format(score)
                    averages[fname].append(score_str)
                    print("\t" + score_str, end="")
            print()
            outfile.close()

        with open("All.eval", "w") as f:
            sys.stdout = f
            print("\t".join(columns))

            for num in range(1, max_s + 1):
                key = "S" + str(num)
                print("\t".join(averages[key]))

        sys.stdout = orig_stdout

def precision_at_k(retrieved, relevant, k):
    retrieved_docids = list(map(lambda d: d["doc_number"], retrieved))
    relevant_docids = list(map(lambda t: t[0], relevant))

    intersection_k = set(retrieved_docids[:k]).intersection(set(relevant_docids))
    precision = len(intersection_k) / len(retrieved[:k])
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

def ndcg_at_k(retrieved, relevant, k):
    relevances = dict(relevant)

    # each item in relevant is a tuple (docnum, relevance)
    # relevant = sorted(relevant, key=lambda x: x[1], reverse=True)
    idcg_k = relevant[0][1]
    for i, t in enumerate(relevant[:k]):
        if i == 0:
            continue
        idcg_k += t[1] / log2(i + 1)

    relevant_ids = list(map(lambda x: x[0], relevant))

    # each item in retrieved is a dict {"doc_number": x, "doc_rank": y, "score": z}
    retrieved = sorted(retrieved, key=lambda x: x["doc_rank"])

    dcg_k = 0
    for i, t in enumerate(retrieved[:k]):
        docnum = t["doc_number"]
        if docnum not in relevant_ids:
            continue
        if i == 0:
            dcg_k += relevances[docnum]
        else:
            dcg_k += relevances[docnum] / log2(i + 1)

    ncdg_k = dcg_k / idcg_k
    return ncdg_k

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
        "nDCG@10": ndcg_at_k(retrieved, relevant, 10),
        "nDCG@20": ndcg_at_k(retrieved, relevant, 20)
    }



if __name__ == "__main__":
    TTDS()
