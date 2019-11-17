import argparse
import functools
import os.path
import sys

from feats import create_feats_dic, read_feats_dic, read_feats, create_feats
from pred import read_preds, Prediction

from pprint import pprint, pformat
from util import eprint

# From https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab6/classIDs.txt
classes = {
    "Autos & Vehicles": 1,
    "Comedy": 2,
    "Education": 3,
    "Entertainment": 4,
    "Film & Animation": 5,
    "Gaming": 6,
    "Howto & Style": 7,
    "Music": 8,
    "News & Politics": 9,
    "Nonprofits & Activism": 10,
    "Pets & Animals": 11,
    "Science & Technology": 12,
    "Sports": 13,
    "Travel & Events": 14,

    1: "Autos & Vehicles",
    2: "Comedy",
    3: "Education",
    4: "Entertainment",
    5: "Film & Animation",
    6: "Gaming",
    7: "Howto & Style",
    8: "Music",
    9: "News & Politics",
    10: "Nonprofits & Activism",
    11: "Pets & Animals",
    12: "Science & Technology",
    13: "Sports",
    14: "Travel & Events",
}

class TTDS():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='TTDS Coursework 2',
            usage='''app.py <command> [<args>]

The most commonly used commands are:
    feats   Build feats files (and dict)
''')

        parser.add_argument('command', help='Subcommand to run')

        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)

        getattr(self, args.command)(sys.argv[2:])

    def feats(self, args):
        parser = argparse.ArgumentParser(
            description='generate feats stuff')

        parser.add_argument('tweetfile', help="prefix file to use")
        parser.add_argument('--refresh-dic', action='store_true')

        args = parser.parse_args(args)

        train_fpath = args.tweetfile + ".train"
        test_fpath = args.tweetfile + ".test"

        if not os.path.isfile(train_fpath):
            print("{} is missing".format(train_fpath))
            exit(1)
        elif not os.path.isfile(test_fpath):
            print("{} is missing".format(test_fpath))
            exit(1)

        with open(train_fpath, "r", errors="ignore") as f:
            train_tweets = extract_bow(f)

        with open(test_fpath, "r", errors="ignore") as f:
            test_tweets = extract_bow(f)

        if args.refresh_dic or not os.path.isfile("feats.dic"):
            eprint("Creating feats.dic...")
            with open("feats.dic", "w") as f:
                featdic = create_feats_dic(f, train_tweets)
        else:
            with open("feats.dic", "r") as f:
                featdic = read_feats_dic(f)

        with open("feats.train", "w") as f:
            create_feats(f, train_tweets, featdic)

        with open("feats.test", "w") as f:
            create_feats(f, test_tweets, featdic, filter_missing=True)

    def eval(self, args):
        parser = argparse.ArgumentParser(
            description='generate eval txt files')

        parser.add_argument('feats', help="the feats.test file")
        parser.add_argument('pred', help="the pred.out file")
        parser.add_argument('eval', help="the eval.txt file")

        args = parser.parse_args(args)

        if not os.path.isfile(args.feats):
            eprint("{} is missing".format(args.feats))
        elif not os.path.isfile(args.pred):
            eprint("{} is missing".format(args.pred))


        with open(args.feats, "r") as f:
            tweet_feats = read_feats(f)

        with open(args.pred, "r") as f:
            preds = read_preds(f)

        with open(args.eval, "w") as f:
            create_eval(f, tweet_feats, preds)


def strip_alpha(word, hashtags=None):
    hashtag = False
    if word.startswith("#"):
        hashtags.append(word)
        hashtag = True

    word = "".join(map(lambda l: l.isalpha() and l or "", word))
    return word

from urllib.parse import urlparse
# from unshortenit import UnshortenIt
# unshortener = UnshortenIt()
def strip_urls(text, urls=None):
    if not text.startswith("https://") and not text.startswith("http://"):
        return True
    # # print(text)
    # # text = unshortener.unshorten(text)
    # # print(text)
    # # print()
    # if urls is not None:
    #     try:
    #         urls.append(urlparse(text))
    #     except ValueError as e:
    #         print(e)
    #         pass
    return False

def extract_bow(f):
    lines = []
    for line in f:
        line = line.rstrip()
        if line == "":
            continue

        parts = line.split("\t")
        assert len(parts) == 3

        line = {}

        # Convert ID to int, and ensure no overflow madness
        assert parts[0] == str(int(parts[0]))
        line['id'] = int(parts[0])

        # Convert class to class ID
        line['class'] = classes[parts[2]]

        # Apply some simple preprocessing to the whole text
        text = parts[1].strip()


        # Split by contiguous whitespace
        tokens = text.split()

        # Filter tokens that start with http or https (NOTE: could also exclude ftp urls or other URI schema in the future)
        urls = []
        tokens = filter(functools.partial(strip_urls, urls=urls), tokens)

        # for url in urls:
        #     tokens.append(url.netloc)
        #     print(url.netloc)

        tokens = map(lambda t: t.lower(), tokens)

        # Strip non-alphabetic characters from all tokens (except for words with leading pound signs)
        hashtags = []
        tokens = map(functools.partial(strip_alpha, hashtags=hashtags), tokens)
        tokens = filter(lambda word: word != "", tokens)
        tokens = list(tokens)
        # print(hashtags)
        tokens.extend(hashtags)

        line['tokens'] = tokens
        line['hashtags'] = hashtags
        lines.append(line)
    return lines

from collections import defaultdict
# from sklearn.metrics import f1_score

def create_eval(f, tweet_feats, preds):
    accuracy = 0
    macro_f1 = 0

    assert len(tweet_feats) == len(preds)

    # maps from class to doc numbers
    relevant = defaultdict(list)
    retrieved = defaultdict(list)
    metrics = []

    for i, real in enumerate(tweet_feats):
        pred = preds[i]
        # print("pred", pred, "real", real)
        pred_class = pred.class_id
        real_class = real['class']
        doc_id = real['id']

        assert pred_class >= 1
        assert pred_class <= 14
        assert real_class >= 1
        assert real_class <= 14

        if pred_class == real_class:
            accuracy += 1
        retrieved[pred_class].append(doc_id)
        relevant[real_class].append(doc_id)

    accuracy /= len(tweet_feats)

    for c_id in range(1, 14 + 1):
        rels = relevant[c_id]
        retr = retrieved[c_id]

        inters = set(retr).intersection(set(rels))
        precision = len(inters) / len(retr)
        recall = len(inters) / len(rels)
        f1 = (2 * precision * recall) / (precision + recall)

        #print(c_id)
        #print("rels:", len(rels), rels)
        ##print("retr: ", len(retr), retr)
        ##print("inters", len(inters), list(inters))
        #print()


        # sk_f1 = f1_score(rels, retr)
        # print("ours", f1, "theirs", sk_f1)

        macro_f1 += f1

        metrics.append({
            "precision": precision,
            "recall": recall,
            "f1": f1
        })

    macro_f1 = macro_f1 / 14


    f.write("Accuracy = {0:.3f}\n".format(accuracy))
    f.write("Macro-F1 = {0:.3f}\n".format(macro_f1))
    f.write("Results per class:\n")

    for i, metric in enumerate(metrics):
        precision = metric['precision']
        recall = metric['recall']
        f1 = metric['f1']

        f.write("{}: P={} R={} F={}\n".format(i + 1, precision, recall, f1))



if __name__ == "__main__":
    TTDS()
