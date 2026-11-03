from collections.abc import AsyncGenerator
import enum
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from starlette_admin.contrib.sqla import Admin, ModelView
import sqlalchemy as sa
from src.db import Base, engine, SessionLocal, get_session

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(SQLAlchemyBaseUserTableUUID, Base):
    role = sa.Column(sa.Enum(UserRole), default=UserRole.USER, nullable=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
