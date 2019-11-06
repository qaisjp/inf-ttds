import argparse
import functools
import os.path
import sys

from feats import create_feats_dic, read_feats_dic, create_feats

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
                featdic = create_feats_dic(f, tweets)
        else:
            with open("feats.dic", "r") as f:
                featdic = read_feats_dic(f)

        with open("feats.train", "w") as f:
            create_feats(f, train_tweets, featdic)

        with open("feats.test", "w") as f:
            create_feats(f, test_tweets, featdic, filter_missing=True)


def strip_alpha(word, hashtags=None):
    hashtag = False
    if word.startswith("#"):
        hashtag = True
        word = word[1:]

    word = "".join(map(lambda l: l.isalpha() and l or "", word))

    if hashtags and hashtag:
        hashtags.append(word)
    return word

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
        text = parts[1].strip().lower()

        # Split by contiguous whitespace
        tokens = text.split()

        # Filter tokens that start with http or https (NOTE: could also exclude ftp urls or other URI schema in the future)
        tokens = filter(lambda text: not text.startswith("https://") and not text.startswith("http://") , tokens)

        # Strip non-alphabetic characters from all tokens (except for words with leading pound signs)
        hashtags = []
        tokens = map(functools.partial(strip_alpha, hashtags=hashtags), tokens)
        tokens = filter(lambda word: word != "", tokens)

        line['tokens'] = list(tokens)
        line['hashtags'] = hashtags
        lines.append(line)
    return lines

if __name__ == "__main__":
    TTDS()
