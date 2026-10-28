from fastapi import APIRouter
from src.api.pages import public_router as pages_public_router
from src.api.pages import admin_router as pages_admin_router
from src.api.photos import public_router as gallery_public_router
from src.api.photos import admin_router as galler_admin_router

from src.users_db import User
from src.schemas.users import UserCreate,UserRead,UserUpdate
from src.users import auth_backend,current_active_user,fastapi_users


main_router=APIRouter()

main_router.include_router(pages_admin_router)

main_router.include_router(pages_public_router)

main_router.include_router(galler_admin_router)

main_router.include_router(gallery_public_router)

main_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags = ["auth"])

main_router.include_router(fastapi_users.get_register_router(UserRead,UserCreate), prefix="/auth", tags = ["auth"])

main_router.include_router(fastapi_users.get_reset_password_router(),prefix="/auth", tags=["auth"])

main_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags= ["users"])

main_router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)