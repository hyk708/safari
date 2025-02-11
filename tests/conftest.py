import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    """FastAPI 테스트 클라이언트"""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth_token(client):
    """OAuth 로그인 후 JWT 토큰 가져오기"""
    response = client.get("/auth/google/login")
    assert response.status_code == 200

    login_url = response.json()["auth_url"]
    auth_response = client.get(login_url)

    assert auth_response.status_code == 200
    assert "access_token" in auth_response.json()

    return f"Bearer {auth_response.json()['access_token']}"
