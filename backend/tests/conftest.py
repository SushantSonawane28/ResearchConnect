import os
import pytest

# Ensure tests run against a local, isolated SQLite database
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.database import Base, engine, SessionLocal
from app.models import Organization, Profile, Project, User
from app.security import hash_password
from app.services import set_profile_tags, set_project_tags


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    pw = hash_password("Password123!")
    org = Organization(name="Test University", org_type="university")
    db.add(org)
    db.flush()

    # Create researcher 1
    u1 = User(name="Test Researcher 1", email="researcher1@prayas.test", password_hash=pw, role="researcher", organization_id=org.id)
    db.add(u1)
    db.flush()
    p1 = Profile(user_id=u1.id, bio="AI and NLP researcher", department="Computer Science", designation="Professor", collab_area="AI")
    db.add(p1)
    db.flush()
    set_profile_tags(db, p1, ["python", "machine learning", "nlp"], ["ai", "deep learning"], ["nlp"])

    # Create researcher 2 for matching
    u2 = User(name="Test Researcher 2", email="researcher2@prayas.test", password_hash=pw, role="researcher", organization_id=org.id)
    db.add(u2)
    db.flush()
    p2 = Profile(user_id=u2.id, bio="Machine learning expert", department="Data Science", designation="Researcher", collab_area="AI")
    db.add(p2)
    db.flush()
    set_profile_tags(db, p2, ["python", "machine learning", "computer vision"], ["ai"], ["machine learning"])

    proj = Project(owner_id=u1.id, title="Test NLP Project", description="Research in natural language processing", domain="AI")
    db.add(proj)
    db.flush()
    set_project_tags(db, proj, ["python", "nlp"])

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass
