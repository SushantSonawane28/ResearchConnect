"""When is a pair of researchers 'a match' worth an email?  (pure logic, easy to test)"""
from . import config


def qualifies(scores: dict, same_domain: bool, threshold: float | None = None) -> bool:
    t = config.MATCH_ALERT_THRESHOLD if threshold is None else threshold
    return scores["hybrid"] >= t or (same_domain and scores["hybrid"] >= t / 2)
