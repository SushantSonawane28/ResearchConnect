"""Small helpers shared by the routers."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from .matching import MatchProfile
from .models import Notification, Profile, Project, ProjectTag, ProfileTag, Tag, User


def clean_names(names: list[str]) -> list[str]:
    seen, out = set(), []
    for n in names:
        n = " ".join((n or "").split())[:100]
        if n and n.lower() not in seen:
            seen.add(n.lower()); out.append(n)
    return out


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.scalar(select(Tag).where(Tag.name == name.lower()))
    if not tag:
        tag = Tag(name=name.lower()); db.add(tag); db.flush()
    return tag


def set_profile_tags(db: Session, profile: Profile, skills, interests, expertise):
    profile.tags.clear(); db.flush()
    for kind, names in (("skill", skills), ("interest", interests), ("expertise", expertise)):
        for n in clean_names(names):
            profile.tags.append(ProfileTag(tag=get_or_create_tag(db, n), kind=kind))


def set_project_tags(db: Session, project: Project, names):
    project.tags.clear(); db.flush()
    for n in clean_names(names):
        project.tags.append(ProjectTag(tag=get_or_create_tag(db, n)))


def to_match_researcher(profile: Profile, projects: list[Project]) -> MatchProfile:
    tags = [pt.tag.name for pt in profile.tags]
    text = profile.bio + " " + " ".join(p.title + " " + p.description for p in projects)
    domain = projects[0].domain if projects and projects[0].domain else profile.department
    return MatchProfile(id=f"r:{profile.user_id}", name=profile.user.name, tags=tags, text=text,
                        domain=domain, org_id=profile.user.organization_id)


def to_match_project(project: Project) -> MatchProfile:
    return MatchProfile(id=f"p:{project.id}", name=project.title,
                        tags=[t.tag.name for t in project.tags], text=project.description,
                        domain=project.domain, org_id=project.owner.organization_id)


def can_see(viewer: User, owner_org_id: int, visibility: str) -> bool:
    """Visibility rule: public = everyone, org = only people in the same organisation."""
    return visibility == "public" or viewer.organization_id == owner_org_id


def notify(db: Session, user_id: int, message: str, kind: str = "info"):
    db.add(Notification(user_id=user_id, message=message[:300], kind=kind))
