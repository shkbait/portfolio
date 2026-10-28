from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends
# ======================starlette-admin============
from starlette_admin.contrib.sqla import Admin, ModelView

from src.db import Base, engine, SessionLocal, get_session

new_session=SessionLocal


    

