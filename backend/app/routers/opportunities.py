from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import current_user, get_db, require_roles
from ..models import Opportunity, User
from ..schemas import OpportunityIn
from ..services import can_see

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _out(o: Opportunity) -> dict:
    return {"id": o.id, "title": o.title, "description": o.description, "domain": o.domain, "type": o.opp_type,
            "deadline": o.deadline.isoformat() if o.deadline else None,
            "posted_by": o.poster.name, "organization": o.poster.organization.name}


@router.post("")
def create(body: OpportunityIn, user: User = Depends(require_roles("coordinator", "industry", "admin")),
           db: Session = Depends(get_db)):
    o = Opportunity(posted_by=user.id, **body.model_dump())
    db.add(o); db.commit(); db.refresh(o)
    return _out(o)


@router.get("")
def list_all(opp_type: str = "", user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = db.query(Opportunity)
    if opp_type:
        q = q.filter(Opportunity.opp_type == opp_type)
    rows = [o for o in q.order_by(Opportunity.deadline.is_(None), Opportunity.deadline).all()
            if can_see(user, o.poster.organization_id, o.visibility)
            and (not o.deadline or o.deadline >= datetime.utcnow())]
    return [_out(o) for o in rows]
