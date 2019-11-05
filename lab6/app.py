import argparse
import os.path
import functools

from functools import reduce
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

def read_args():
    parser = argparse.ArgumentParser()

    return parser.parse_args()

def main():
    args = read_args()

    with open("Tweets.14cat.train", "r", errors="ignore") as f:
        lines = extract_bow(f)

    if not os.path.isfile("feats.dic"):
        eprint("Creating feats.dic...")
        with open("feats.dic", "w") as f:
            featdic = create_feats_dic(f, lines)

    with open("feats.dic", "r") as f:
        featdic2 = read_feats_dic(f)

    import json
    featdic = json.dumps(featdic, sort_keys=True)
    featdic2 = json.dumps(featdic2, sort_keys=True)

    print(featdic == featdic2)

def read_feats_dic(f):
    d = {}
    for line in f:
        parts = line.split()
        if len(parts) > 1:
            n = parts[1]
            s = parts[0]
            d[n] = s
            d[s] = n
    return d

def create_feats_dic(f, lines):
    tokens = sorted(reduce(lambda x,y: x.union(set(y['tokens'])), lines, set()))
    d = {}
    for i, token in enumerate(tokens):
        f.write(token + " " + str(i+1) + "\n")
        d[i+1] = token
        d[token] = i+1
    return d


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
    main()
