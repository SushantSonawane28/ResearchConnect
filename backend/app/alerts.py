"""Match alerts: when two researchers match, BOTH get an email describing the other and why.

Runs in the background after a profile is saved or a project is created.
Rules (all must be true):
  1. both people have email_alerts switched on (consent)
  2. each can see the other's profile (visibility rules)
  3. hybrid score >= MATCH_ALERT_THRESHOLD, or same domain and score >= half the threshold
  4. this pair was never emailed before (match_alerts table)
  5. at most MATCH_ALERT_MAX new alerts per trigger (no spam)
The other person's email address is included only if BOTH profiles are 'public'.
"""
from collections import defaultdict
import logging

from sqlalchemy import select

from . import config
from .database import SessionLocal
from .alert_rules import qualifies
from .email_service import build_match_email, send_email
from .matching import MatchingEngine
from .matching.preprocess import normalize_tag
from .models import MatchAlert, Profile, Project
from .services import can_see, notify, to_match_researcher

log = logging.getLogger(__name__)


def _other_info(p: Profile, domain: str, include_email: bool) -> dict:
    info = {"name": p.user.name, "organization": p.user.organization.name,
            "department": p.department, "domain": domain}
    if include_email:
        info["email"] = p.user.email
    return info


def _related_projects(projs_by_owner: dict, owner_id: int, my_tags: set[str]) -> list[str]:
    out = []
    for pr in projs_by_owner.get(owner_id, []):
        tags = {normalize_tag(t.tag.name) for t in pr.tags}
        if tags & my_tags or not my_tags:
            out.append(pr.title)
    return out


def run_match_alerts(user_id: int, db=None) -> int:
    """Returns how many NEW pairs were emailed."""
    own_session = db is None
    db = db or SessionLocal()
    sent = 0
    try:
        me = db.scalar(select(Profile).where(Profile.user_id == user_id))
        if not me or not me.email_alerts:
            return 0

        all_projects = db.query(Project).all()
        projs_by_owner = defaultdict(list)
        for pr in all_projects:
            projs_by_owner[pr.owner_id].append(pr)

        my_projects = projs_by_owner[user_id]
        me_mp = to_match_researcher(me, my_projects)
        candidates = []
        for p in db.query(Profile).filter(Profile.user_id != user_id, Profile.email_alerts.is_(True)).all():
            if can_see(me.user, p.user.organization_id, p.visibility) and \
               can_see(p.user, me.user.organization_id, me.visibility):
                candidates.append((p, to_match_researcher(p, projs_by_owner[p.user_id])))
        if not candidates:
            return 0
        engine = MatchingEngine([me_mp] + [mp for _, mp in candidates])
        by_id = {mp.id: (p, mp) for p, mp in candidates}
        my_tags = {normalize_tag(t) for t in me_mp.tags}
        for r in engine.rank(me_mp.id, "hybrid", top_k=20):
            if sent >= config.MATCH_ALERT_MAX:
                break
            other, other_mp = by_id[r["id"]]
            same_domain = bool(me_mp.domain) and normalize_tag(me_mp.domain) == normalize_tag(other_mp.domain)
            if not qualifies(r["all_scores"], same_domain):
                continue
            low, high = sorted((user_id, other.user_id))
            if db.scalar(select(MatchAlert).where(MatchAlert.user_low == low, MatchAlert.user_high == high)):
                continue
            both_public = me.visibility == "public" and other.visibility == "public"
            reasons, shared = r["explanation"]["reasons"], r["explanation"]["shared_tags"]
            their_tags = {normalize_tag(t) for t in other_mp.tags}
            statuses = []
            # email 1: to me, about them
            subj, text, html = build_match_email(me.user.name, _other_info(other, other_mp.domain, both_public),
                                                 r["percent"], reasons, shared,
                                                 _related_projects(projs_by_owner, other.user_id, my_tags), config.APP_URL)
            statuses.append(send_email(me.user.email, subj, text, html))
            # email 2: to them, about me
            subj, text, html = build_match_email(other.user.name, _other_info(me, me_mp.domain, both_public),
                                                 r["percent"], reasons, shared,
                                                 _related_projects(projs_by_owner, user_id, their_tags), config.APP_URL)
            statuses.append(send_email(other.user.email, subj, text, html))
            db.add(MatchAlert(user_low=low, user_high=high, score=r["score"], email_status=",".join(statuses)))
            notify(db, user_id, f"New match: {other.user.name} ({round(r['percent'])}%). Check your email.", "match")
            notify(db, other.user_id, f"New match: {me.user.name} ({round(r['percent'])}%). Check your email.", "match")
            db.commit()
            sent += 1
        return sent
    except Exception:
        log.exception("match alert run failed")
        db.rollback()
        return sent
    finally:
        if own_session:
            db.close()
