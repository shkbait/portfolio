from fastapi import FastAPI
import uvicorn
from src.api.router import main_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth.setup import setup_admin

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

setup_admin(app)

if __name__ =="main.py":
    uvicorn.run("main:app",host="127.0.0.1", port=8000, reload=True)
