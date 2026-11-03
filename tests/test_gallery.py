import pytest
from httpx import AsyncClient,ASGITransport
from src.main import app
from src.users import current_superuser
from pathlib import Path



@pytest.mark.asyncio(loop_scope="session")
async def test_upload():
    app.dependency_overrides[current_superuser] = lambda: True
    try:
        file_path= Path(__file__).parent / "test.png"
        with open(file_path, "rb") as file:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
                response = await ac.post(
                    f"/gallery/upload_photo",
                    params={
                        "title": "test title",
                        "tags": "test tag",
                    },
                    files={
                        "file": (
                            file_path.name,
                            file,
                            "image/png",
                        )
                    }
                )
                print(response)
                data = response.json()
                photo_id=data["photo_id"]
                assert response.status_code == 200

                get = await ac.get(
                    f"/current_photo",
                    params={
                        "photo_id": photo_id
                    }
                )

                assert get.status_code == 200

                delete = await ac.delete(
                    f"/gallery/delete_photo",
                    params={
                        "photo_id": photo_id,
                    }
                )
                assert delete.status_code == 200
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio(loop_scope="session")
async def test_update():
    app.dependency_overrides[current_superuser] = lambda: True
    try:
        file_path= Path(__file__).parent / "test.png"
        with open(file_path, "rb") as file:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
                response = await ac.post(
                    f"/gallery/upload_photo",
                    params={
                        "title": "test title",
                        "tags": "test tag",
                    },
                    files={
                        "file": (
                            file_path.name,
                            file,
                            "image/png",
                        )
                    }
                )
                print(response)
                data = response.json()
                photo_id=data["photo_id"]
                assert response.status_code == 200

                get = await ac.get(
                    f"/current_photo",
                    params={
                        "photo_id": photo_id
                    }
                )

                assert get.status_code == 200

                update = await ac.patch(
                    f"/gallery/update_photo",
                    params={
                        "photo_id": photo_id,
                        "title": "updated title",
                        "tags": "updated tag",
                    },
                    files={
                        "file": (
                            file_path.name,
                            file,
                            "image/png",
                        )
                    }
                )
                assert update.status_code == 200

                delete = await ac.delete(
                    f"/gallery/delete_photo",
                    params={
                        "photo_id": photo_id,
                    }
                )
                assert delete.status_code == 200
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio(loop_scope="session")
async def test_upload_401():
    file_path=Path(__file__).parent / "test.png"
    with open(file_path, "rb") as file:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            response = await ac.post(
                f"/gallery/upload_photo",
                params={
                    "title": "test title",
                    "tags": "test tag",
                },
                files={
                    "file": (
                        file_path.name,
                        file,
                        "image/png",
                    )
                }
            )
            print(response)
            assert response.status_code == 401

            delete = await ac.delete(
                f"/gallery/delete_photo",
                params={
                    "photo_id": 3
                }
            )

            assert delete.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_update_401():
    file_path=Path(__file__).parent / "test.png"
    with open(file_path, "rb") as file:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            response = await ac.post(
                f"/gallery/upload_photo",
                params={
                    "title": "test title",
                    "tags": "test tag",
                },
                files={
                    "file": (
                        file_path.name,
                        file,
                        "image/png",
                    )
                }
            )
            print(response)
            assert response.status_code == 401

            update = await ac.patch(
                f"/gallery/update_photo",
                params={
                    "photo_id": 3,
                    "title": "updated title",
                    "tags": "updated tag",
                }
            )
            assert update.status_code == 401

            delete = await ac.delete(
                f"/gallery/delete_photo",
                params={
                    "photo_id": 3
                }
            )

            assert delete.status_code == 401


