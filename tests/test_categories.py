import pytest

CATEGORY_NAME = "테스트 카테고리"

def test_create_category(client, auth_token):
    """카테고리 생성 테스트"""
    response = client.post(
        "/categories/",
        json={"name": CATEGORY_NAME},
        headers={"Authorization": auth_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == CATEGORY_NAME

def test_get_categories(client):
    """카테고리 목록 조회 테스트"""
    response = client.get("/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
