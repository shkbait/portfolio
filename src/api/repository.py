import os
import uuid
import socket
from pathlib import Path
import aiofiles
from fastapi import UploadFile
from sqlalchemy import select

from src.users_db import User
from src.schemas.page import AddPage_scheme,Page_scheme,Page_Update_scheme
from src.schemas.photo import Photo_add_scheme,Photo_scheme,Photo_Update_scheme
from src.model.pages import Page_Model
from src.model.photos import Photos_model
from src.photo_db import new_session as photo_session

from src.model.contact import Contact_Model
from src.schemas.contact import Contact_scheme

from src.contact_db import engine as contact_engine
from src.contact_db import new_session as contact_session
# =================email======================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from src.db import Base,engine, SessionLocal, get_session

new_session=SessionLocal

load_dotenv()
SENDER_EMAIL=os.getenv("SENDER_EMAIL")
APP_PASSWORD=os.getenv("APP_PASSWORD")
ADMIN_EMAIL=os.getenv("ADMIN_EMAIL")
SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT", 465))

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def send_email(email: Contact_scheme):
    try:
        smtp_server = socket.getaddrinfo(SMTP_HOST, SMTP_PORT, socket.AF_INET)[0][4][0]
    except Exception:
        smtp_server = SMTP_HOST
    port=465
    sender_email=SENDER_EMAIL
    password=APP_PASSWORD

    message=MIMEMultipart()
    message['From']=sender_email
    message['To']=email.your_email
    message['Subject']="idk"
    message.attach(MIMEText("Hello twin", "plain", "utf-8"))


    
    with smtplib.SMTP_SSL(smtp_server, SMTP_PORT) as server:
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email,email.your_email,message.as_string())

def admin_notification(email: Contact_scheme):
    try:
        smtp_server = socket.getaddrinfo(SMTP_HOST, SMTP_PORT, socket.AF_INET)[0][4][0]
    except Exception:
        smtp_server = SMTP_HOST
    port=465
    sender_email=SENDER_EMAIL
    password=APP_PASSWORD
    
    admin_email=ADMIN_EMAIL
    
    message=MIMEMultipart()
    message['From']=sender_email
    message['To']=admin_email
    message['Subject']=f"from {email.your_email}, {email.first_name} {email.last_name}"
    message.attach(MIMEText(email.message, "plain", "utf-8"))  
    with smtplib.SMTP_SSL(smtp_server, SMTP_PORT) as server:
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email,admin_email,message.as_string())

def email_auth(to_email: str, subject: str, body: str):
    try:
        smtp_server = socket.getaddrinfo(SMTP_HOST, SMTP_PORT, socket.AF_INET)[0][4][0]
    except Exception:
        smtp_server = SMTP_HOST
    port=465
    sender_email=SENDER_EMAIL
    password=APP_PASSWORD

    message=MIMEMultipart()
    message['From']=sender_email
    message['To']=to_email
    message['Subject']=subject
    message.attach(MIMEText(body, "plain", "utf-8"))


    
    with smtplib.SMTP_SSL(smtp_server, SMTP_PORT) as server:
        server.ehlo()
        server.login(sender_email,password)
        server.sendmail(sender_email,to_email,message.as_string())

class PagesRepo:
    @classmethod
    async def add_page(cls, data: AddPage_scheme)->int:
        async with new_session() as session:
            page_dict = data.model_dump()

            new_page=Page_Model(**page_dict)

            session.add(new_page)
            await session.flush()
            await session.commit()

            return new_page.id

    @classmethod
    async def upload_photo(cls,data: Photo_add_scheme, file: UploadFile)->int:
        async with photo_session() as session:
            file_ext=os.path.splitext(file.filename)[1] 
            unique_suffix = uuid.uuid4().hex[:8]
            file_name=f"{data.title}_{unique_suffix}{file_ext}"
            file_path=os.path.join(UPLOAD_DIR, file_name)

            os.makedirs(UPLOAD_DIR, exist_ok=True)

            async with aiofiles.open(file_path, "wb") as buffer:
                while content := await file.read(1024*1024):
                    await buffer.write(content)
            photo_dict = data.model_dump()
            photo_dict["photo_path"]=f"/uploads/{file_name}"
            new_photo=Photos_model(**photo_dict)
            session.add(new_photo)
            await session.flush()
            await session.commit()
            return new_photo.id

    @classmethod
    async def get_photo(cls)->list[Photo_scheme]:
        async with photo_session() as session:
            query=select(Photos_model)
            result=await session.execute(query)
            photos=result.scalars().all()
            if photos is None:
                return None
            photo_scheme=[Photo_scheme.model_validate(photo,from_attributes=True)
                    for photo in photos
            ]
            return photo_scheme
        
    @classmethod
    async def update_photo(cls,photo_id: int, data: Photo_Update_scheme, file: UploadFile):
        async with photo_session() as session:
            photo=await session.get(Photos_model, photo_id)
            if photo is None:
                return None
            file_ext=os.path.splitext(file.filename)[1]
            unique_suffix = uuid.uuid4().hex[:8]
            file_name=f"{data.title}_{unique_suffix}{file_ext}"
            file_path=os.path.join(UPLOAD_DIR, file_name)

            os.makedirs(UPLOAD_DIR, exist_ok=True)
            Path(photo.photo_path).unlink(missing_ok=True)
            async with aiofiles.open(file_path,"wb") as buffer:
                while content := await file.read(1024*1024):
                    await buffer.write(content)

            photo_data = data.model_dump(exclude_unset=True) | {"photo_path": f"/uploads/{file_name}"}

            for field, value in photo_data.items():
                setattr(photo, field, value) 

            await session.commit()
            return Photo_scheme.model_validate(photo, from_attributes=True)
        
    @classmethod
    async def get_one_photo(cls, photo_id:int):
        async with photo_session() as session:
            query=select(Photos_model).where(Photos_model.id==photo_id)
            result = await session.execute(query)
            photo_model=result.scalars().one_or_none()
            if photo_model is None:
                return None
            return Photo_scheme.model_validate(photo_model, from_attributes=True)



    @classmethod
    async def get_page(cls, page_id: int):
        async with new_session() as session:
            query= select(Page_Model).where(Page_Model.id==page_id)
            result = await session.execute(query)
            page_model=result.scalars().one_or_none()
            if page_model is None:
                return None
            return Page_scheme.model_validate(page_model, from_attributes=True)

    @classmethod
    async def get_current_page(cls, page_id: int, title: str | None, main_text: str | None)->list[Page_scheme]:
        async with new_session() as session:
            query = select(Page_Model)
            if page_id is not None:
                query=query.where(Page_Model.id==page_id)
            if title is not None:
                query=query.where(Page_Model.title.ilike(f"%{title}%"))
            if main_text is not None:
                query=query.where(Page_Model.main_text.ilike(f"%{main_text}%"))
            result = await session.execute(query)
            page_models= result.scalars().all()
            return [Page_scheme.model_validate(page, from_attributes=True)
                    for page in page_models
            ]
    @classmethod
    async def about(cls):
        async with new_session() as session:
            query=select(Page_Model).where(Page_Model.title=="about")
            result= await session.execute(query)
            about_model= result.scalars().one_or_none()
            if about_model is None:
                return None
            return about_model

    @classmethod
    async def update(cls, page_id: int, data: Page_Update_scheme):
        async with new_session() as session:
            page=await session.get(Page_Model, page_id)
            if page is None:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(page, field, value)
            await session.commit()
            return Page_scheme.model_validate(page, from_attributes=True)

    @classmethod
    async def upload_picture(cls,page_id: int,file: UploadFile)->bool:
        async with new_session() as session:
            result=await session.execute(select(Page_Model).where(Page_Model.id==page_id))
            page=result.scalars().one_or_none()
            if page is None:
                return False

            file_ext=os.path.splitext(file.filename)[1] 
            unique_suffix = uuid.uuid4().hex[:8]
            file_name=f"{page_id}_{unique_suffix}{file_ext}"
            file_path=os.path.join(UPLOAD_DIR, file_name) 

            os.makedirs(UPLOAD_DIR, exist_ok=True)

            async with aiofiles.open(file_path,"wb") as buffer:
                while content := await file.read(1024*1024):
                    await buffer.write(content)
            page.pic_path=file_path
            await session.commit()
            return True
              
        
    @classmethod
    async def contact(cls,data: Contact_scheme):
        async with contact_session() as session:
            form_dict=data.model_dump()
            new_request=Contact_Model(**form_dict)

            session.add(new_request)

            

            await session.flush()
            await session.commit()

            return new_request.id

    
    
    
    @classmethod
    async def delete_photo(cls,photo_id: int)->bool:
        async with photo_session() as session:
            photo=await session.get(Photos_model,photo_id)
            if photo is None:
                return False
            if photo.photo_path is not None:
                Path(photo.photo_path).unlink(missing_ok=True)
            await session.delete(photo)
            await session.commit()
            return True
    @classmethod
    async def delete_page(cls,page_id: int)->bool:
        async with new_session() as session:
            page=await session.get(Page_Model,page_id)
            if page is None:
                return False
            if page.pic_path is not None:
                Path(page.pic_path).unlink(missing_ok=True)
            await session.delete(page)
            await session.commit()
            return True
    