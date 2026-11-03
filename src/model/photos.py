from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
# from src.photo_db import Base
from src.db import Base
from datetime import datetime, timezone
from typing import Optional

class Photos_model(Base):
    __tablename__="photos"
    id: Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]
    tags: Mapped[Optional[str]]
    photo_path:Mapped[str]=mapped_column(String(500))
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )