import re

from indexing import tokenize

class QueryError(Exception):
    pass

class QueryOperand():
    text: str
    negated: bool
    phrasal: bool
    distance: int

    def __init__(self, text, negated, phrasal, distance):
        self.text = text
        self.negated = negated
        self.phrasal = phrasal
        self.distance = distance

        if phrasal and distance is not None:
            raise QueryError("Phrasal and distance are mutually exclusive fields: {}".format(self))
        elif distance == 0:
            raise QueryError("Invalid distance 0: {}".format(self))

    def __members(self):
        return (self.text, self.negated, self.phrasal, self.distance)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self):
        return hash(self.__members())

    def __str__(self):
        s = "QueryOperand("
        if self.negated:
            s += "NOT "

        if self.phrasal:
            s += "\"" + " ".join(self.text) + "\""
        elif self.distance is not None:
            s += "#" + str(self.distance) + "(" + self.text[0] + ", " + self.text[1] + ")"
        else:
            s += self.text

        return s + ")"

    def __repr__(self):
        return self.__str__()


def preprocess_word(s, filter_set):
    toks = tokenize(s, filter_set)
    if len(toks) != 1:
        raise QueryError("Odd s '{}', got toks: {}".format(s, toks))
    return toks[0]

def read_query_file(filename):
    with open(filename) as f:
        queries = []
        for line in f:
            key, query = line.split(" ", 1)
            queries.append(
                (key.rstrip(":").lstrip("q"), query)
            )
        return queries

def parse_query_str(query_str, stopwords, splitphrase=False):
    ops = ["OR", "AND"]
    chosen_op = None

    # Determine operation
    for op in ops:
        if op in query_str:
            if chosen_op is not None:
                raise QueryError("Multiple ops found in query: {}".format(query_str))

            chosen_op = op

            # split by op
            parts = query_str.split(" " + op + " ")
            if len(parts) != 2:
                raise QueryError("Invalid query. Should be one OP in middle of query: {}\nGot: {}".format(query_str, parts))

    if chosen_op is None:
        if splitphrase:
            parts = query_str.split()
        else:
            parts = [query_str]
        chosen_op = "OR"

    re_proximity = re.compile("^#(\d+)\((.*?), ?(.*?)\)$")

    new_parts = []
    for i, s in enumerate(parts):
        s = str.strip(s)

        negated = s.startswith("NOT ")
        if negated:
            s = s[4:]

        quoted = s.startswith("\"") and s.endswith("\"")
        distance = None
        if quoted:
            s = s[1:-1]
            s = s.split()
            if len(s) == 1:
                s = s[0]
                quoted = False
            elif len(s) == 2:
                s = (s[0], s[1])
            else:
                raise QueryError("Quoted query should have 1 or 2 words")
        else:
            proxim_match = re_proximity.match(s)
            if proxim_match:
                distance, text_a, text_b = proxim_match.groups()
                distance = int(distance)
                s = (text_a, text_b)

        if isinstance(s, tuple):
            # preprocess them
            text_a, text_b = s
            text_a = preprocess_word(text_a, stopwords)
            text_b = preprocess_word(text_b, stopwords)
            s = (text_a, text_b)
        elif s not in stopwords:
            s = preprocess_word(s, stopwords)
        elif s in stopwords:
            continue

        new_parts.append(QueryOperand(s, negated, quoted, distance))

    return (chosen_op, new_parts)
