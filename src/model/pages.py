from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class Page_Model(Base):
    __tablename__="pages"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]
    main_text: Mapped[Optional[str]]
    pic_path: Mapped[str | None] = mapped_column(String(500))