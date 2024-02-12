import pytest
from httpx import AsyncClient

from src.api.main import app


def test_that_this_passes():
    assert 1 == 1


@pytest.mark.anyio
async def test_build_item(async_client):
    item = {"title": "Foo", "description": "There goes my hero"}
    response = await async_client.post("/build-item/", json=item)
    assert response.status_code == 200
    assert {**response.json(), "id": "foo"} == {"id": "foo", **item}


@pytest.mark.anyio
async def test_read_item(async_client):
    await async_client.post(
        "/items/",
        json={"title": "Foo Bar", "description": "The Foo Barters"},
    )
    response = await async_client.get(
        "/items/1",
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Foo Bar",
        "description": "The Foo Barters",
    }


# @pytest.mark.anyio
# async def test_read_inexistent_item(async_client):
#     response = await async_client.get(
#         "/items/999",
#     )
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Item not found"}


@pytest.mark.anyio
async def test_create_item(async_client):
    response = await async_client.post(
        "/items/",
        json={"title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Foo Bar"
    assert response.json()["description"] == "The Foo Barters"
