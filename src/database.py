from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends
# ======================starlette-admin============
from starlette_admin.contrib.sqla import Admin, ModelView



engine=create_async_engine('sqlite+aiosqlite:///./pages.db')

new_session=async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

class Base(DeclarativeBase):
    pass

class View(ModelView):
    fields = ["id", "title", "main_text", "pic_path"]
    searchable_fields = ("title", "main_text")

    

