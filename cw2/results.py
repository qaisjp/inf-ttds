from collections import namedtuple

Qrel = namedtuple("Qrel", ("query_number", "scores"))

def read_results(f):
    queries = []
    for line in f:
        parts = line.split()
        assert parts[1] == "0"
        assert parts[5] == "0"
        queries.append({
            "query_number": int(parts[0]),
            # 0 - parts[1]
            "doc_number": int(parts[2]),
            "doc_rank": int(parts[3]),
            "score": float(parts[4]),
            # 0 - parts[5]
        })
    return queries

# converts "(9093,3)" to (9093, 3)
def read_tuple(s):
    assert s[0] == "("
    assert s[-1] == ")"
    parts = s[1:-1].split(",")
    parts = list(map(int, parts))
    return tuple(parts)

def read_relevants(f):
    qrels = []
    for line in f:
        parts = line.split()
        query_number = parts[0]
        assert query_number[-1] == ":"
        query_number = int(query_number[:-1])
        tuples = list(map(read_tuple, parts[1:]))

        qrels.append(Qrel(query_number, tuples))
    return qrels