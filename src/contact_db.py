from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


from src.db import Base, engine, SessionLocal, get_session

EmailBase=Base

new_session=SessionLocal
