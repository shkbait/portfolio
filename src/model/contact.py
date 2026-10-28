# from src.contact_db import EmailBase 
from src.db import Base
from sqlalchemy.orm import Mapped,mapped_column

class Contact_Model(Base):
    __tablename__="contact"
    id: Mapped[int]=mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    your_email: Mapped[str]
    message: Mapped[str]
