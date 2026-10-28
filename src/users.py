import uuid

from fastapi import Depends, Request
from fastapi_users import BaseUserManager,FastAPIUsers,UUIDIDMixin,models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from src.users_db import User,get_user_db

from src.api.repository import email_auth

from dotenv import load_dotenv
import os

load_dotenv()
SECRET=os.getenv("SECRET")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")
        await self.request_verify(user, request)

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None):
        verify_url = "http://127.0.0.1:5500/verify.html"
        email_body = (
            f"Для подтверждения почты откройте страницу: {verify_url}\n"
            f"Токен подтверждения: {token}"
        )
        if request and "background_tasks" in request.scope:
            bg_tasks = request.scope["background_tasks"]

            bg_tasks.add_task(
                email_auth,
                to_email=user.email,
                subject="Подтверждение почты",
                body=email_body,

            )
        else:
            email_auth(
                to_email=user.email,
                subject="Подтверждение почты",
                body=email_body,
            )

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport=BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy()-> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend=AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user=fastapi_users.current_user(active=True)
current_superuser= fastapi_users.current_user(
    active=True,
    superuser=True,
)