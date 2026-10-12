from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import current_user, get_db
from ..models import CollabRequest, Notification, User
from ..schemas import RequestIn, RequestUpdate
from ..services import notify

router = APIRouter(tags=["requests"])


def _out(r: CollabRequest) -> dict:
    return {"id": r.id, "sender_id": r.sender_id, "sender": r.sender.name, "receiver_id": r.receiver_id,
            "receiver": r.receiver.name, "project_id": r.project_id, "message": r.message,
            "status": r.status, "created_at": r.created_at.isoformat()}


@router.post("/requests")
def send_request(body: RequestIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.receiver_id == user.id or not db.get(User, body.receiver_id):
        raise HTTPException(400, "Invalid receiver")
    r = CollabRequest(sender_id=user.id, receiver_id=body.receiver_id, project_id=body.project_id, message=body.message)
    db.add(r)
    notify(db, body.receiver_id, f"{user.name} ({user.organization.name}) wants to collaborate with you.", "request")
    db.commit(); db.refresh(r)
    return _out(r)


@router.get("/requests/inbox")
def inbox(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [_out(r) for r in db.query(CollabRequest).filter(CollabRequest.receiver_id == user.id).order_by(CollabRequest.id.desc())]


@router.get("/requests/sent")
def sent(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [_out(r) for r in db.query(CollabRequest).filter(CollabRequest.sender_id == user.id).order_by(CollabRequest.id.desc())]


@router.patch("/requests/{request_id}")
def answer_request(request_id: int, body: RequestUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r = db.get(CollabRequest, request_id)
    if not r or r.receiver_id != user.id:
        raise HTTPException(404, "Request not found")
    r.status = body.status
    notify(db, r.sender_id, f"{user.name} {body.status} your collaboration request.", "request_update")
    db.commit()
    return _out(r)


@router.get("/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.id.desc()).limit(50)
    return [{"id": n.id, "message": n.message, "kind": n.kind, "is_read": n.is_read,
             "created_at": n.created_at.isoformat()} for n in rows]


@router.post("/notifications/{nid}/read")
def mark_read(nid: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, nid)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Not found")
    n.is_read = True; db.commit()
    return {"ok": True}
