
import asyncio
from getpass import getpass

from sqlalchemy import select
from fastapi_users.db import SQLAlchemyUserDatabase

from src.db import SessionLocal
from src.users import UserManager
from src.users_db import User, UserRole


async def main():
    email = input("Email: ").strip().lower()
    password = getpass("Password: ")
    password_confirm = getpass("Confirm password: ")

    if password != password_confirm:
        print("Passwords don't match!")
        return

    if len(password) < 8:
        print("Password must contain at least 8 characters!")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            print("User already exists. Updating permissions.")

            user.is_superuser = True
            user.is_active = True
            user.is_verified = True
            user.role = UserRole.ADMIN

        else:
            user_db = SQLAlchemyUserDatabase(session, User)
            manager = UserManager(user_db)

            hashed_password = manager.password_helper.hash(password)

            user = User(
                email=email,
                hashed_password=hashed_password,
                is_superuser=True,
                is_active=True,
                is_verified=True,
                role=UserRole.ADMIN,
            )

            session.add(user)

        await session.commit()

        print(f"Superuser created/updated: {email}")


if __name__ == "__main__":
    asyncio.run(main())
