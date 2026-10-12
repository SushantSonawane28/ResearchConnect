"""Load the synthetic dataset into the database (so you can log in and try the app).

Run from the backend folder:   python -m seed.data_gen   then   python -m seed.seed_db
All seeded users have the password:  Password123!   (change/delete before real use)
Also creates an admin:  admin@prayas.test / Password123!
"""
import json

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Organization, Profile, Project, User
from app.security import hash_password
from app.services import set_profile_tags, set_project_tags
from seed.data_gen import DATA_DIR, ORGS

PW = hash_password("Password123!")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    orgs = {}
    for name, typ in ORGS:
        o = db.scalar(select(Organization).where(Organization.name == name)) or Organization(name=name, org_type=typ)
        db.add(o); db.flush(); orgs[name] = o
    admin = User(name="Admin", email="admin@prayas.test", password_hash=PW, role="admin",
                 organization_id=orgs[ORGS[0][0]].id)
    if not db.scalar(select(User).where(User.email == admin.email)):
        db.add(admin)
    id_map = {}
    for r in json.loads((DATA_DIR / "researchers.json").read_text()):
        email = f"researcher{r['id']}@prayas.test"
        u = db.scalar(select(User).where(User.email == email))
        if not u:
            role = "industry" if r["org_type"] == "company" else "researcher"
            u = User(name=r["name"], email=email, password_hash=PW, role=role, organization_id=orgs[r["organization"]].id)
            db.add(u); db.flush()
            p = Profile(user_id=u.id, bio=r["bio"], department=r["department"], designation="Researcher",
                        collab_area=r["primary_domain"])
            db.add(p); db.flush()
            set_profile_tags(db, p, r["skills"], r["interests"], r["expertise"])
        id_map[r["id"]] = u.id
    for pr in json.loads((DATA_DIR / "projects.json").read_text()):
        proj = Project(owner_id=id_map[pr["owner_id"]], title=pr["title"], description=pr["description"], domain=pr["domain"])
        db.add(proj); db.flush()
        set_project_tags(db, proj, pr["tags"])
    db.commit(); db.close()
    print("Seeded. Login e.g. researcher1@prayas.test / Password123!")


if __name__ == "__main__":
    main()
