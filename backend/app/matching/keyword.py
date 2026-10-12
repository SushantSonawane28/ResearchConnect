"""METHOD 1 - Keyword matching (baseline).

score = shared words / all unique words.   Fast, but ML != machine learning.
"""
from .preprocess import tokenize


def keyword_set(tags: list[str], text: str) -> set[str]:
    return tokenize(" ".join(tags) + " " + text)


def keyword_score(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0
