"""The matching engine. It knows nothing about the web or the database:
give it a list of MatchProfile objects and it ranks them.
(A 'MatchProfile' can be a researcher OR a project, so we can match both ways.)
"""
from dataclasses import dataclass, field

from .hybrid import DEFAULT_WEIGHTS, hybrid_score
from .keyword import keyword_score, keyword_set
from .preprocess import normalize_tag
from .tags import jaccard, tag_set
from .tfidf import build_tfidf_matrix

METHODS = ("keyword", "tag", "tfidf", "hybrid")


@dataclass
class MatchProfile:
    id: str                      # e.g. "r:12" for researcher 12, "p:3" for project 3
    name: str
    tags: list[str]              # skills + interests + expertise (or project tags)
    text: str = ""               # bio + project descriptions
    domain: str = ""
    org_id: int | None = None
    extra: dict = field(default_factory=dict)


class MatchingEngine:
    def __init__(self, profiles: list[MatchProfile], weights: dict | None = None):
        self.profiles = profiles
        self.weights = weights or DEFAULT_WEIGHTS
        self.pos = {p.id: i for i, p in enumerate(profiles)}
        self._kw = [keyword_set(p.tags, p.text) for p in profiles]
        self._tags = [tag_set(p.tags) for p in profiles]
        docs = [" ".join(p.tags) + " " + p.domain + " " + p.text for p in profiles]
        self._cos = build_tfidf_matrix(docs)  # computed once, reused for every query

    # ---- scoring -------------------------------------------------------
    def pair_scores(self, i: int, j: int) -> dict:
        kw = keyword_score(self._kw[i], self._kw[j])
        tg = jaccard(self._tags[i], self._tags[j])
        tf = float(self._cos[i, j])
        return {"keyword": kw, "tag": tg, "tfidf": tf,
                "hybrid": hybrid_score(kw, tg, tf, self.weights)}

    def rank(self, query_id: str, method: str = "hybrid", top_k: int = 10,
             candidate_ids: list[str] | None = None) -> list[dict]:
        if method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        qi = self.pos[query_id]
        ids = candidate_ids if candidate_ids is not None else [p.id for p in self.profiles]
        results = []
        for cid in ids:
            if cid == query_id:
                continue
            cj = self.pos[cid]
            s = self.pair_scores(qi, cj)
            results.append({"id": cid, "name": self.profiles[cj].name,
                            "score": round(s[method], 4),
                            "percent": round(s[method] * 100, 1),
                            "all_scores": {k: round(v, 4) for k, v in s.items()},
                            "explanation": self.explain(qi, cj, s)})
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    # ---- explanation ---------------------------------------------------
    def explain(self, i: int, j: int, scores: dict | None = None) -> dict:
        a, b = self.profiles[i], self.profiles[j]
        scores = scores or self.pair_scores(i, j)
        shared_tags = sorted(self._tags[i] & self._tags[j])
        covered = {w for t in shared_tags for w in t.split()}
        shared_words = sorted((self._kw[i] & self._kw[j]) - covered)
        reasons = []
        if shared_tags:
            reasons.append(f"{len(shared_tags)} shared topics/skills: " + ", ".join(shared_tags[:5]))
        if a.domain and normalize_tag(a.domain) == normalize_tag(b.domain):
            reasons.append(f"Same research domain: {a.domain}")
        if shared_words:
            reasons.append("Common terms in their work: " + ", ".join(shared_words[:5]))
        if scores["tfidf"] >= 0.3:
            reasons.append(f"Similar descriptions (text similarity {round(scores['tfidf'] * 100)}%)")
        if a.org_id is not None and b.org_id is not None and a.org_id != b.org_id:
            reasons.append("Cross-organisation collaboration opportunity")
        if not reasons:
            reasons.append("Weak overlap - shown because few better matches exist")
        return {"shared_tags": shared_tags, "shared_terms": shared_words[:8], "reasons": reasons}
