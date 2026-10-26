from fastapi import FastAPI
import uvicorn
from src.api.router import main_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette_admin.contrib.sqla import Admin
from src.database import engine,View
from src.model.pages import Page_Model
import os

from starlette.middleware.sessions import SessionMiddleware
from src.admin_auth import AdminAuthProvider

app=FastAPI()

app.include_router(main_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

SESSION_SECRET = os.getenv(
    "ADMIN_SESSION_SECRET",
    "local-development-secret-change-before-deployment",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False,
)

pages_admin = Admin(
    engine,
    title="Pages Admin",
    secret_key=SESSION_SECRET,
    auth_provider=AdminAuthProvider(),
)

pages_admin.add_view(
    View(Page_Model, icon="fa fa-newspaper")
)

pages_admin.mount_to(app)

if __name__ =="main.py":
    uvicorn.run("main:app",host="127.0.0.1", port=8000, reload=True)
