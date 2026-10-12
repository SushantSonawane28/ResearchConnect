from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..deps import get_db, require_roles
from ..models import CollabRequest, Opportunity, Organization, ProfileTag, Project, Tag, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats(_: User = Depends(require_roles("admin", "coordinator")), db: Session = Depends(get_db)):
    top = (db.query(Tag.name, func.count(ProfileTag.profile_id)).join(ProfileTag, ProfileTag.tag_id == Tag.id)
           .group_by(Tag.name).order_by(func.count(ProfileTag.profile_id).desc()).limit(10).all())
    by_org = Counter(o.org_type for o in db.query(Organization).all())
    return {"researchers": db.query(User).filter(User.role == "researcher").count(),
            "organizations": db.query(Organization).count(), "organizations_by_type": dict(by_org),
            "projects": db.query(Project).count(), "opportunities": db.query(Opportunity).count(),
            "collaboration_requests": db.query(CollabRequest).count(),
            "accepted_collaborations": db.query(CollabRequest).filter(CollabRequest.status == "accepted").count(),
            "top_tags": [{"tag": n, "count": c} for n, c in top]}
