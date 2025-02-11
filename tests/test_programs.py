import pytest

@pytest.mark.asyncio
def test_create_program(test_client):
    """프로그램 생성 테스트"""
    response = test_client.post("/programs/", json={"name": "테스트 프로그램"})
    assert response.status_code == 200
    assert response.json()["name"] == "테스트 프로그램"

@pytest.mark.asyncio
def test_get_programs(test_client):
    """프로그램 목록 조회 테스트"""
    response = test_client.get("/programs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
