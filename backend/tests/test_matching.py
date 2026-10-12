"""Run with:  pytest   (from the backend folder)"""
from app.matching import MatchingEngine, MatchProfile
from app.matching.preprocess import normalize_tag
from app.matching.tags import jaccard


def test_normalize_acronyms():
    assert normalize_tag("ML") == "machine learning"
    assert normalize_tag("  Deep-Learning ") == "deep learning"


def test_jaccard_example_from_proposal():
    a = {"ai", "ml", "healthcare", "nlp", "python"}
    b = {"ai", "ml", "healthcare", "ocr", "python"}
    assert round(jaccard(a, b), 3) == 0.667


def _profiles():
    return [
        MatchProfile("r:1", "A", ["ML", "NLP", "healthcare"], "medical document classification", "Healthcare AI"),
        MatchProfile("r:2", "B", ["machine learning", "OCR", "healthcare"], "medical document extraction", "Healthcare AI"),
        MatchProfile("r:3", "C", ["bridge design", "concrete"], "structural analysis of bridges", "Structural"),
    ]


def test_similar_researcher_ranks_first_for_every_method():
    engine = MatchingEngine(_profiles())
    for method in ("keyword", "tag", "tfidf", "hybrid"):
        assert engine.rank("r:1", method)[0]["id"] == "r:2"


def test_explanation_has_reasons():
    top = MatchingEngine(_profiles()).rank("r:1", "hybrid")[0]
    assert top["explanation"]["reasons"]
