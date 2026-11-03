import pytest
from httpx import AsyncClient,ASGITransport
from src.main import app
from src.model.pages import Page_Model
from src.users import current_superuser

@pytest.mark.asyncio(loop_scope="session")
async def test_contact():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.post(
            f"/contact",
            params={
                "first_name": "test name",
                "last_name": "test las name",
                "your_email": "shrkbaitt@gmail.com",
                "message": "test message",
            }
        )
        print(response)
        data=response.json()
        # contact_id=data["id"]

        assert response.status_code == 200
        # assert data["id"] == contact_id

