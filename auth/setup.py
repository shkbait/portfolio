import os

from starlette_admin.contrib.sqla import Admin
from src.model.pages import Page_Model
from src.model.photos import Photos_model
from src.model.contact import Contact_Model

from dotenv import load_dotenv

from starlette.middleware.sessions import SessionMiddleware
from auth.admin_auth import AdminAuthProvider

from src.db import engine
from auth.views import View, UsersView, GalleryView, ContactView
from src.users_db import User

load_dotenv()

def setup_admin(app):
    SESSION_SECRET = os.getenv("ADMIN_SESSION_SECRET")

    app.add_middleware(
        SessionMiddleware,
        secret_key=SESSION_SECRET,
        same_site="lax",
        https_only=False,
    )

    admin = Admin(
        engine,
        title="Portfolio Admin",
        secret_key=SESSION_SECRET,
        auth_provider=AdminAuthProvider(),
    )

    admin.add_view(
        ContactView(Contact_Model, icon="fa fa-newspaper")
    )

    admin.add_view(
        GalleryView(Photos_model, icon="fa fa-newspaper")
    )
    admin.add_view(
        View(Page_Model, icon="fa fa-newspaper")
    )
    admin.add_view(
        UsersView(User, icon="fa fa-newspaper")
    )

    admin.mount_to(app)
