"""The matching endpoints. They load data, call the engine, and return ranked results."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..matching import METHODS, MatchingEngine
from ..models import Profile, Project, User
from ..services import can_see, to_match_project, to_match_researcher

router = APIRouter(prefix="/match", tags=["matching"])


def _my_match_profile(user: User, db: Session):
    if not user.profile:
        raise HTTPException(400, "Create your profile first")
    mine = db.query(Project).filter(Project.owner_id == user.id).all()
    return to_match_researcher(user.profile, mine)


def _visible_researchers(user: User, db: Session, scope: str):
    from collections import defaultdict
    projs_by_owner = defaultdict(list)
    for pr in db.query(Project).all():
        projs_by_owner[pr.owner_id].append(pr)

    out = []
    for p in db.query(Profile).filter(Profile.user_id != user.id).all():
        if scope == "org" and p.user.organization_id != user.organization_id:
            continue
        if scope == "industry" and p.user.organization.org_type != "company":
            continue
        if scope == "academia" and p.user.organization.org_type == "company":
            continue
        if not can_see(user, p.user.organization_id, p.visibility):
            continue
        out.append(to_match_researcher(p, projs_by_owner[p.user_id]))
    return out


@router.get("/researchers")
def match_researchers(method: str = Query("hybrid"), scope: str = Query("all", pattern="^(org|all|industry|academia)$"),
                      top_k: int = Query(10, le=50), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if method not in METHODS:
        raise HTTPException(400, f"method must be one of {METHODS}")
    me = _my_match_profile(user, db)
    others = _visible_researchers(user, db, scope)
    if not others:
        return []
    engine = MatchingEngine([me] + others)
    results = engine.rank(me.id, method, top_k)
    for r in results:
        r["user_id"] = int(r.pop("id").split(":")[1])
    return results


@router.get("/projects")
def match_projects(method: str = Query("hybrid"), top_k: int = Query(10, le=50),
                   user: User = Depends(current_user), db: Session = Depends(get_db)):
    me = _my_match_profile(user, db)
    projects = [p for p in db.query(Project).filter(Project.owner_id != user.id).all()
                if can_see(user, p.owner.organization_id, p.visibility)]
    if not projects:
        return []
    engine = MatchingEngine([me] + [to_match_project(p) for p in projects])
    results = engine.rank(me.id, method, top_k)
    for r in results:
        r["project_id"] = int(r.pop("id").split(":")[1])
    return results


@router.get("/compare")
def compare_methods(top_k: int = Query(5, le=20), user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Top results for ALL four methods side by side (great for demos and your report)."""
    me = _my_match_profile(user, db)
    others = _visible_researchers(user, db, "all")
    if not others:
        return {}
    engine = MatchingEngine([me] + others)
    return {m: [{"user_id": int(r["id"].split(":")[1]), "name": r["name"], "percent": r["percent"]}
                for r in engine.rank(me.id, m, top_k)] for m in METHODS}
