from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from ..alerts import run_match_alerts
from ..deps import current_user, get_db
from ..models import Profile, User
from ..schemas import ProfileIn
from ..services import can_see, set_profile_tags

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _out(p: Profile) -> dict:
    by = lambda k: [pt.tag.name for pt in p.tags if pt.kind == k]
    return {"user_id": p.user_id, "name": p.user.name, "organization": p.user.organization.name,
            "org_type": p.user.organization.org_type, "role": p.user.role, "bio": p.bio,
            "department": p.department, "designation": p.designation, "visibility": p.visibility,
            "looking_for_collab": p.looking_for_collab, "collab_area": p.collab_area,
            "email_alerts": p.email_alerts,
            "skills": by("skill"), "interests": by("interest"), "expertise": by("expertise"),
            "completeness": _completeness(p)}


def _completeness(p: Profile) -> int:
    checks = [bool(p.bio), bool(p.department), bool(p.designation), bool(p.collab_area),
              any(t.kind == "skill" for t in p.tags), any(t.kind == "interest" for t in p.tags),
              any(t.kind == "expertise" for t in p.tags)]
    return round(100 * sum(checks) / len(checks))


@router.get("/me")
def my_profile(user: User = Depends(current_user)):
    if not user.profile:
        return {"user_id": user.id, "name": user.name, "organization": user.organization.name,
                "org_type": user.organization.org_type, "role": user.role, "bio": "", "department": "",
                "designation": "", "visibility": "public", "looking_for_collab": True, "collab_area": "",
                "email_alerts": True, "skills": [], "interests": [], "expertise": [], "completeness": 0}
    return _out(user.profile)


@router.put("/me")
def save_my_profile(body: ProfileIn, background: BackgroundTasks, user: User = Depends(current_user),
                    db: Session = Depends(get_db)):
    p = user.profile
    if not p:
        p = Profile(user_id=user.id); db.add(p); db.flush()
    p.bio, p.department, p.designation = body.bio, body.department, body.designation
    p.visibility, p.looking_for_collab, p.collab_area = body.visibility, body.looking_for_collab, body.collab_area
    p.email_alerts = body.email_alerts
    set_profile_tags(db, p, body.skills, body.interests, body.expertise)
    db.commit(); db.refresh(p)
    background.add_task(run_match_alerts, user.id)   # email both people if a new match is found
    return _out(p)


@router.get("/{user_id}")
def view_profile(user_id: int, viewer: User = Depends(current_user), db: Session = Depends(get_db)):
    p = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not p or not can_see(viewer, p.user.organization_id, p.visibility):
        raise HTTPException(404, "Profile not found")
    return _out(p)
