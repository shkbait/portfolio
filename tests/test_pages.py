import pytest
from httpx import AsyncClient,ASGITransport
from src.main import app
from src.model.pages import Page_Model
from src.users import current_superuser

@pytest.mark.asyncio(loop_scope="session")
async def test_id_find():
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://testserver") as ac:
        response=await ac.post(
            "/add_page",
            params={
                "title": "test",
                "main_text": "main_text_test"
            }
        )

        assert response.status_code in (401, 403)
        # PYTHONPATH=. pytest -v

@pytest.mark.asyncio(loop_scope="session")
async def test_id_find2():
    app.dependency_overrides[current_superuser]= lambda: True
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://testserver") as ac:
            response=await ac.post(
                "/add_page",
                params={
                    "title": "test",
                    "main_text": "main_text_test"
                }
            )
            print(response)
            data=response.json()
            page_id=data["page_id"]

            assert response.status_code==200, response.text
            
            assert data["page_id"]==page_id
            get = await ac.get(
                f"/get_page",
                params={
                    "page_id": page_id
                }
            )

            assert get.status_code==200, get.text

            delete = await ac.delete(
                f"/delete_page",
                params={
                    "page_id": page_id
                }

            )
            assert delete.status_code == 200, delete.text
            check = await ac.get(f"/get_page/{page_id}")
            assert check.status_code==404


    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio(loop_scope="session")
async def test_delete():
    app.dependency_overrides[current_superuser]= lambda: True
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://testserver") as ac:
            response=await ac.post(
                "/add_page",
                params={
                    "title": "test",
                    "main_text": "main_text_test"
                }
            )
            print(response)
            data=response.json()
            page_id=data["page_id"]

            assert response.status_code==200, response.text
            assert data["page_id"]==page_id

            delete = await ac.delete(
                f"/delete_page",
                params={
                    "page_id": page_id
                }
            )
            assert delete.status_code == 200, delete.text

            get = await ac.get(
                f"/get_page",
                params={
                    "page_id": page_id
                }
            )
            assert get.status_code==404

        
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio(loop_scope="session")
async def test_update_page():
    app.dependency_overrides[current_superuser] = lambda: True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.post(
            f"/add_page",
            params={
                "title": "test update",
                "main_text": "hello",
            }

        )
        print(response)
        data=response.json()
        page_id=data["page_id"]

        assert response.status_code==200

        get = await ac.get(
            f"/get_page",
            params={
                "page_id": page_id
            }
        )
        assert get.status_code==200
        update = await ac.patch(
            f"/update_page",
                params={"page_id": page_id},
                json={"main_text": "hello1199"}
        )
        assert update.status_code==200

        check = await ac.get(
            f"/get_current",
            params={
                "main_text": "hello1199"
            }
        )
        assert check.status_code==200
        delete = await ac.delete(
            f"/delete_page",
            params={
                "page_id": page_id
            }
        )
        assert delete.status_code==200

        app.dependency_overrides.clear()

@pytest.mark.asyncio(loop_scope="session")
async def test_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get(
            f"/get_page",
            params={
                "page_id": 0
            }
        )
        assert response.status_code == 404

@pytest.mark.asyncio(loop_scope="session")
async def test_empty_title():
    app.dependency_overrides[current_superuser] = lambda: True
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")as ac:
            create= await ac.post(
                f"/add_page",
                params={
                    "title": " ",
                    "main_text": "test",
                    "tags": "test tag",
                }
            )
            assert create.status_code == 422
    finally:
        app.dependency_overrides.clear()

#===============================auth==============================

@pytest.mark.asyncio(loop_scope="session")
async def test_add401():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")as ac:
            create= await ac.post(
                f"/add_page",
                params={
                    "title": "test401",
                    "main_text": "test",
                    "tags": "test tag",
                }
            )
            assert create.status_code == 401

@pytest.mark.asyncio(loop_scope="session")
async def test_delete401():
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://testserver") as ac:
            delete = await ac.delete(
                f"/delete_page",
                params={
                    "page_id": 10
                }
            )
            assert delete.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_update401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        update = await ac.patch(
            f"/update_page",
                params={"page_id": 10},
                json={"main_text": "hello1199"}
        )
        assert update.status_code == 401
