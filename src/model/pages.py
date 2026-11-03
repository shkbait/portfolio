from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
# from src.database import Base
from sqlalchemy import DateTime, func
from src.db import Base
from datetime import datetime, timezone

class Page_Model(Base):
    __tablename__="pages"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]
    main_text: Mapped[Optional[str]]
    tags: Mapped[Optional[str]]
    pic_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )