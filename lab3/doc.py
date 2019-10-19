import itertools

from typing import List
from util import safe_int

class Doc():
    num : str
    headline: str
    text : str

    tokens : List[str]

    @staticmethod
    def from_xml_node(node):
        d = Doc()
        d.num = node.find("DOCNO").text
        d.headline = node.find("HEADLINE").text.strip()
        d.text = node.find("TEXT").text.strip()
        return d

    @staticmethod
    def get_xml_node_tags(doc_node):
        tags = []
        for node in doc_node:
            tags.append(node.tag.lower())
            print(node, node.tag.lower())
        return set(tags)

    def __str__(self):
        return "Doc(num=%s, headline=%s, text=[len:%d])" % (self.num, self.headline, len(self.text))

def search(docmap, index, query):
    op, parts = query

    inclusions = {}
    exclusions = {}

    for i, qpart in enumerate(parts):
        found = False
        if qpart.phrasal or (qpart.distance is not None):
            term_a, term_b = qpart.text

            # Do both these terms appear the entire sample?
            if term_a in index and term_b in index:
                entries_a = index[term_a]
                entries_b = index[term_b]

                # Pluck out position lists where docs match
                # ( doc_num, term_a_positions, term_b_positions )
                matching_docs = [
                    (doc, entries_a[doc], entries_b[doc])
                    for doc in set(entries_a.keys()) & set(entries_b.keys())
                ]

                nearby_docs = []
                for doc, positions_a, positions_b in matching_docs:
                    doc_pos_pairs = [
                        (pos_a, pos_b)
                        for pos_a in positions_a
                        for pos_b in positions_b
                    ]

                    for pos_a, pos_b in doc_pos_pairs:
                        # We don't use a list comprehension here
                        # so that we can quickly short-circuit once
                        # we have confirmed that we're near
                        if qpart.phrasal:
                            if (pos_b - pos_a) == 1:
                                nearby_docs.append(doc)
                                break
                        else:
                            if abs(pos_a - pos_b) <= qpart.distance:
                                nearby_docs.append(doc)
                                break

                docs = nearby_docs
                found = True
        elif qpart.text in index:
            docs = index[qpart.text].keys()
            found = True
        else:
            print("Term '%s' not found" % qpart.text)
            continue

        if qpart.negated:
            found = not found

        if found:
            inclusions[qpart] = docs
        else:
            exclusions[qpart] = docs

    if op == "OR":
        assert(len(exclusions) == 0)
        inclusions = itertools.chain.from_iterable(inclusions.values())
        return sorted(set(inclusions), key=safe_int)
    else:
        pass # Operation is AND

    # If inclusions is empty, but exclusions contains stuff
    # we want to set inclusions to entire document set
    if len(inclusions) == 0 and len(exclusions) > 0:
        inclusions = map(
            lambda entries: entries.keys(), index.values())
        inclusions = itertools.chain.from_iterable(inclusions)
    else:
        # Since the entire document set is a list, we need to normalise
        # our original inclusion map to be a list, to make code common
        inclusions = inclusions.values()

        # common docs
        new_inclusions = None
        for ds in inclusions:
            if new_inclusions is None:
                new_inclusions = set(ds)
            else:
                new_inclusions = new_inclusions & set(ds)
        inclusions = new_inclusions

    exclusions = itertools.chain.from_iterable(exclusions.values())

    return sorted(set(inclusions) - set(exclusions), key=safe_int)
