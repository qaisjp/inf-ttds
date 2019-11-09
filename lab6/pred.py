from collections import namedtuple

Prediction = namedtuple("Prediction", ("class_id", "scores"))

def read_preds(f):
    preds = []
    for line in f:
        parts = line.split()
        preds.append(Prediction(int(parts[0]), list(map(float, parts[1:]))))
    return preds
