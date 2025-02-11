import pytest
from httpx import AsyncClient
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.mark.asyncio
def test_google_login():
    """구글 로그인 URL 반환 테스트"""
    response = client.get("/auth/google/login")
    assert response.status_code == 200
    assert "auth_url" in response.json()

