"""METHOD 2 - Tag similarity (Jaccard).

J(A, B) = |A intersect B| / |A union B|, on normalised tag phrases.
"""
from .preprocess import normalize_tag


def tag_set(tags: list[str]) -> set[str]:
    return {normalize_tag(t) for t in tags if t and t.strip()}


def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0
