from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..alerts import run_match_alerts
from ..deps import current_user, get_db
from ..models import MatchAlert, User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/run")
def run_now(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Check for matches right now and email both sides of any NEW match."""
    return {"new_matches_emailed": run_match_alerts(user.id, db)}


@router.get("")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(MatchAlert).filter((MatchAlert.user_low == user.id) | (MatchAlert.user_high == user.id)) \
             .order_by(MatchAlert.id.desc()).limit(50)
    out = []
    for a in rows:
        other = db.get(User, a.user_high if a.user_low == user.id else a.user_low)
        out.append({"with": other.name, "organization": other.organization.name,
                    "score_percent": round(a.score * 100, 1), "sent_at": a.sent_at.isoformat()})
    return out
