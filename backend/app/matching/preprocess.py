"""STEP 1 of matching: clean and normalise text.

Two levels of cleaning are used on purpose:
- tokenize()      -> plain words only (used by the KEYWORD baseline, no synonyms)
- normalize_tag() -> whole phrases with acronyms expanded (used by TAG and TF-IDF)
"""
import re

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it",
    "of", "on", "or", "that", "the", "to", "with", "works", "work", "working", "using",
    "use", "interested", "applications", "research", "based", "into", "his", "her",
    "their", "has", "have", "also", "new", "our", "we", "i",
}

# Acronym -> full phrase. Add more as your dataset grows.
SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "iot": "internet of things",
    "llm": "large language models",
    "llms": "large language models",
    "ocr": "optical character recognition",
    "genai": "generative ai",
}


def tokenize(text: str) -> set[str]:
    """Lower-case words, no stop-words, NO synonym handling (keyword baseline)."""
    words = re.findall(r"[a-z0-9+#]+", (text or "").lower())
    return {w for w in words if len(w) > 1 and w not in STOP_WORDS}


def normalize_tag(tag: str) -> str:
    """'ML' -> 'machine learning', '  Deep-Learning ' -> 'deep learning'."""
    t = re.sub(r"[^a-z0-9+# ]+", " ", (tag or "").lower())
    t = re.sub(r"\s+", " ", t).strip()
    return SYNONYMS.get(t, t)


def expand_synonyms(text: str) -> str:
    """Replace acronyms inside free text so TF-IDF treats ML and machine learning alike."""
    words = re.findall(r"[a-z0-9+#]+", (text or "").lower())
    return " ".join(SYNONYMS.get(w, w) for w in words)
