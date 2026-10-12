from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..alerts import run_match_alerts
from ..deps import current_user, get_db
from ..models import Project, User
from ..schemas import ProjectIn
from ..services import can_see, set_project_tags

router = APIRouter(prefix="/projects", tags=["projects"])


def _out(p: Project) -> dict:
    return {"id": p.id, "owner_id": p.owner_id, "owner": p.owner.name, "organization": p.owner.organization.name,
            "title": p.title, "description": p.description, "domain": p.domain, "status": p.status,
            "visibility": p.visibility, "tags": [t.tag.name for t in p.tags]}


@router.post("")
def create_project(body: ProjectIn, background: BackgroundTasks, user: User = Depends(current_user),
                   db: Session = Depends(get_db)):
    p = Project(owner_id=user.id, title=body.title, description=body.description, domain=body.domain,
                status=body.status, visibility=body.visibility)
    db.add(p); db.flush()
    set_project_tags(db, p, body.tags)
    db.commit(); db.refresh(p)
    background.add_task(run_match_alerts, user.id)   # a new project may create new matches
    return _out(p)


@router.get("")
def list_projects(q: str = "", domain: str = "", user: User = Depends(current_user),
                  db: Session = Depends(get_db), limit: int = Query(50, le=100), offset: int = 0):
    query = db.query(Project)
    if domain:
        query = query.filter(Project.domain.ilike(f"%{domain}%"))
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%") | Project.description.ilike(f"%{q}%"))
    rows = [p for p in query.order_by(Project.id.desc()).all() if can_see(user, p.owner.organization_id, p.visibility)]
    return [_out(p) for p in rows[offset: offset + limit]]


@router.get("/mine")
def my_projects(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [_out(p) for p in db.query(Project).filter(Project.owner_id == user.id).all()]


@router.delete("/{project_id}")
def delete_project(project_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = db.get(Project, project_id)
    if not p or (p.owner_id != user.id and user.role != "admin"):
        raise HTTPException(404, "Project not found")
    db.delete(p); db.commit()
    return {"deleted": project_id}
