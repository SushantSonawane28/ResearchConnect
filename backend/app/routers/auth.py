import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models import Organization, User
from ..schemas import LoginIn, RegisterIn, TokenOut
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
_attempts: dict[str, list[float]] = defaultdict(list)   # tiny in-memory rate limiter


def _rate_limit(key: str, limit: int = 8, window: int = 60):
    now = time.time()
    _attempts[key] = [t for t in _attempts[key] if now - t < window]
    if len(_attempts[key]) >= limit:
        raise HTTPException(429, "Too many attempts. Try again in a minute.")
    _attempts[key].append(now)


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    _rate_limit("reg:" + request.client.host)
    if db.scalar(select(User).where(User.email == body.email.lower())):
        raise HTTPException(400, "Email already registered")
    org = db.scalar(select(Organization).where(Organization.name == body.organization_name))
    if not org:
        org = Organization(name=body.organization_name, org_type=body.organization_type)
        db.add(org); db.flush()
    user = User(name=body.name, email=body.email.lower(), password_hash=hash_password(body.password),
                role=body.role, organization_id=org.id)
    db.add(user); db.commit()
    return TokenOut(access_token=create_token(user.id, user.role), role=user.role, user_id=user.id, name=user.name)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    _rate_limit("login:" + request.client.host)
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Wrong email or password")
    return TokenOut(access_token=create_token(user.id, user.role), role=user.role, user_id=user.id, name=user.name)
