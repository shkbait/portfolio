import os
from uuid import UUID

from fastapi import Request
from sqlalchemy import select
from starlette_admin.auth import AdminUser, AuthProvider, LoginFailed

from src.users import UserManager
from src.users_db import User, async_session_maker


class AdminAuthProvider(AuthProvider):

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
    ) -> None:
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == username)
            )
            user = result.scalar_one_or_none()

            if user is None or not user.is_active or not user.is_superuser:
                raise LoginFailed("Неверный логин или пароль")

            from fastapi_users.db import SQLAlchemyUserDatabase

            user_db = SQLAlchemyUserDatabase(session, User)
            manager = UserManager(user_db)

            password_valid, _ = manager.password_helper.verify_and_update(
                password,
                user.hashed_password,
            )

            if not password_valid:
                raise LoginFailed("Неверный логин или пароль")

            request.session["admin_user_id"] = str(user.id)

    async def authenticate(self, request: Request) -> AdminUser | None:
        user_id = request.session.get("admin_user_id")

        if not user_id:
            return None

        try:
            parsed_id = UUID(user_id)
        except (ValueError, TypeError):
            request.session.clear()
            return None

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == parsed_id)
            )
            user = result.scalar_one_or_none()

            if user is None or not user.is_active or not user.is_superuser:
                request.session.clear()
                return None

            return AdminUser(username=user.email)

    async def logout(self, request: Request) -> None:
        request.session.clear()