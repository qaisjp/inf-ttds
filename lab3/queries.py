import re

from indexing import tokenize

class QueryPart():
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
            print("Phrasal and distance are mutually exclusive fields:", self)
            sys.exit(1)
        elif distance == 0:
            print("Invalid distance 0:", self)

    def __members(self):
        return (self.text, self.negated, self.phrasal, self.distance)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self):
        return hash(self.__members())

    def __str__(self):
        s = "QueryPart("
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
        print("Odd s '{}', got toks: {}".format(s, toks))
        sys.exit(1)
    return toks[0]

def read_query_file(filename):
    with open(filename) as f:
        queries = []
        for line in f:
            key, query = line.split(" ", 1)
            queries.append(
                (key.rstrip(":"), query)
            )
        return queries

def parse_query_str(query_str, stopwords):
    ops = ["OR", "AND"]
    chosen_op = None

    # Determine operation
    for op in ops:
        if op in query_str:
            if chosen_op is not None:
                print("Multiple ops found in query:", query_str)
                sys.exit(1)

            chosen_op = op

            # split by op
            parts = query_str.split(" " + op + " ")
            if len(parts) != 2:
                print("Invalid query. Should be one OP in middle of query:", query_str)
                print("Got", parts)
                sys.exit(1)

    if chosen_op is None:
        parts = [query_str]
        chosen_op = "AND"

    re_proximity = re.compile("^#(\d+)\((.*?), ?(.*?)\)$")

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
                print("Quoted query should have 1 or 2 words")
                sys.exit(1)
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
        else:
            s = preprocess_word(s, stopwords)

        parts[i] = QueryPart(s, negated, quoted, distance)

    return (chosen_op, parts)
