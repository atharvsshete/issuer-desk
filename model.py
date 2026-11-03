"""One-nearest-neighbour sentence-role classifier. Examples and thresholds are illustrative."""
import re
from math import sqrt

TRAIN = {
    "issuer": ["entity will issue the notes", "these notes are issued by entity", "the notes are obligations of entity"],
    "other": ["entity will guarantee the notes", "the notes are guaranteed by entity", "entity acts as trustee for the notes", "entity distributes the notes"]
}

def tokens(s):
    return set(re.findall(r"[a-z]+", s.lower()))

def similarity(a, b):
    return len(a & b) / sqrt(len(a) * len(b)) if a and b else 0

def predicts_issuer(sentence):
    words = tokens(sentence)
    scores = {role: max(similarity(words, tokens(s)) for s in examples) for role, examples in TRAIN.items()}
    return scores["issuer"] >= .70 and scores["issuer"] - scores["other"] >= .15

