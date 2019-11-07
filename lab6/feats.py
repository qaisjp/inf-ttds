from functools import reduce

def read_feats_dic(f):
    d = {}
    for line in f:
        parts = line.split()
        assert len(parts) == 2
        n = int(parts[1])
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

def create_feats(f, tweets, featdic, filter_missing=False):
    for tweet in tweets:
        if filter_missing:
            features = filter(lambda t: t in featdic, tweet['tokens'])
        else:
            features = tweet['tokens']

        features = map(lambda t: featdic[t], features)

        # remove duplicates
        features = list(set(features))

        # sort the features
        features = sorted(features)

        features = " ".join(map(lambda n: str(n)+":1", features))
        f.write("{} {} #{}\n".format(tweet['class'], features, tweet['id']))