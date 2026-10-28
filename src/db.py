import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.orm import DeclarativeBase

DATABASE_URL= os.getenv(
    "DATABASE_URL",
     
    "postgresql+asyncpg://portfolio_user:portfolio_dev_123@localhost:5432/portfolio",
)

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_session():
    async with SessionLocal() as session:
        yield session

