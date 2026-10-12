"""METHOD 4 - Hybrid = weighted mix of the other three.

These starting weights are a guess. TUNE them with evaluation/run_experiments.py.
"""
DEFAULT_WEIGHTS = {"keyword": 0.25, "tag": 0.35, "tfidf": 0.40}


def hybrid_score(keyword: float, tag: float, tfidf: float, weights: dict | None = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    return w["keyword"] * keyword + w["tag"] * tag + w["tfidf"] * tfidf
