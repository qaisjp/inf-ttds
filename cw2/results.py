from collections import defaultdict, namedtuple

def read_results(f):
    queries = defaultdict(list)
    for line in f:
        parts = line.split()
        assert parts[1] == "0"
        assert parts[5] == "0"

        query_number = int(parts[0])
        queries[query_number].append({
            # key is query_number - parts[0]
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

def read_relevant(f):
    queries = {}
    for line in f:
        parts = line.split()

        assert parts[0][-1] == ":"
        query_number = int(parts[0][:-1])

        queries[query_number] = list(map(read_tuple, parts[1:]))
    return queries
