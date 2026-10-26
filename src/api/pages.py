from typing import Annotated
from src.users_db import User
from src.api.dependencies import PaginationDep
from src.api.repository import PagesRepo
from src.api import router
from src.database import Base, engine
from src.photo_db import Base as photo_Base
from src.photo_db import engine as photo_engine
from fastapi import APIRouter, Depends, UploadFile, File
from src.schemas.page import AddPage_scheme,Page_scheme,Page_Update_scheme
from src.schemas.contact import Contact_scheme
from fastapi import HTTPException,BackgroundTasks
from src.contact_db import new_session as contact_session
from src.contact_db import engine as contact_engine
from src.contact_db import EmailBase
from src.api.repository import send_email
from src.api.repository import admin_notification
from src.users_db import engine as users_engine
from src.users_db import Base as UsersBase

from src.users import current_active_user, current_superuser


public_router=APIRouter()

admin_router=APIRouter(
    dependencies=[Depends(current_superuser)]
)

@admin_router.post("/setup_database", tags=["setup database"])
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return {"ok": True, "message": "Database setup complete successfully"}

@admin_router.post("/setup_photos_db", tags=["setup database"])
async def setup_photos_db():
    async with photo_engine.begin() as conn:
        await conn.run_sync(photo_Base.metadata.create_all)
    return {"ok": True, "message": "Database setup complete successfully"}   

@admin_router.post("/setup_contact_db", tags=["setup database"])
async def setup_contact_db():
    async with contact_engine.begin() as conn:
        await conn.run_sync(EmailBase.metadata.create_all)
    return {"ok": True, "message": "Database setup complete successfully"}  

@admin_router.post("/setup_user_db", tags=["setup database"])
async def setup_database():
    async with users_engine.begin() as conn:
        await conn.run_sync(UsersBase.metadata.create_all)
    return {"ok": True, "message": "Database setup complete successfully"} 

@admin_router.post("/add_page", tags=["pages"])
async def add_page(data: Annotated[AddPage_scheme,Depends()])->dict:
    page_id=await PagesRepo.add_page(data)
    return {"ok": True, "page_id": page_id}

@admin_router.post("/upload_picture", tags=["pages"])
async def upload_picture(page_id:int, file: UploadFile):
    if file.filename is None:
        raise HTTPException(status_code=400)
    
    page=await PagesRepo.upload_picture(page_id,file)
    if page is None:
        raise HTTPException(status_code=404)
    return {"ok": True}

@admin_router.delete("/delete_page", tags=["pages"])
async def delete_page(page_id:int):
    deleted=await PagesRepo.delete_page(page_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Page not Found")
    return {"ok":True}

@public_router.get("/get_page", tags=["pages"])
async def get_page(page_id: int):
    page= await PagesRepo.get_page(page_id)
    return page

@public_router.get("/get_current", tags=["pages"])
async def get_current(
    pagination: PaginationDep,
    page_id: int | None = None,
    title: str | None = None,
    main_text: str | None=None
)->list[Page_scheme]:
    result = await PagesRepo.get_current_page(page_id, title, main_text)
    return result[pagination.offset : pagination.offset + pagination.limit]

@public_router.get("/about")
async def about():
    about = await PagesRepo.about()
    return about

@public_router.post("/contact")
def contact(email: Annotated[Contact_scheme,Depends()], background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    background_tasks.add_task(PagesRepo.contact, email)
    background_tasks.add_task(admin_notification, email)
    return {"status": "success", "message": "Email in process"}

@admin_router.patch("/update_page", tags=["pages"])
async def patch(page_id:int, data: Annotated[Page_Update_scheme,Depends()])->Page_scheme:
    result = await PagesRepo.update(page_id,data)
    if result is None:
        raise HTTPException(status_code=404, detail="page not found")
    return result

@public_router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}