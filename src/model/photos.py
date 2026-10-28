from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
# from src.photo_db import Base
from src.db import Base

class Photos_model(Base):
    __tablename__="photos"
    id: Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]
    photo_path:Mapped[str]=mapped_column(String(500))