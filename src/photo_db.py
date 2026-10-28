from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.db import Base, engine, SessionLocal, get_session

from starlette_admin.contrib.sqla import Admin, ModelView

new_session=SessionLocal
