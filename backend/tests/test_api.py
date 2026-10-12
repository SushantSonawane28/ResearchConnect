from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "docs": "/docs"}


def test_login_success():
    res = client.post("/auth/login", json={"email": "researcher1@prayas.test", "password": "Password123!"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "researcher"


def test_login_invalid_password():
    res = client.post("/auth/login", json={"email": "researcher1@prayas.test", "password": "WrongPassword!"})
    assert res.status_code == 401


def test_profile_and_matching():
    login_res = client.post("/auth/login", json={"email": "researcher1@prayas.test", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_res = client.get("/profiles/me", headers=headers)
    assert profile_res.status_code == 200
    assert "name" in profile_res.json()

    match_res = client.get("/match/researchers?method=hybrid&scope=all", headers=headers)
    assert match_res.status_code == 200
    matches = match_res.json()
    assert isinstance(matches, list)
    if matches:
        assert "percent" in matches[0]
        assert "explanation" in matches[0]
