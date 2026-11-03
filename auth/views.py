from starlette_admin.contrib.sqla import ModelView
from starlette.requests import Request
from src.users import current_superuser


class View(ModelView):
    fields = ["id", "title", "main_text","tags","pic_path","created_at"]
    searchable_fields = ("title", "main_text")

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "admin_user", None)
        if not user:
            return False
        return bool({"superuser", "admin", "manager"} & set(user.roles))
    def can_create(self, request):
        return True
    def can_edit(self, request):
        return True
    def can_delete(self, request):
        user = getattr(request.state, "admnin_user", None)
        if not user:
            return False
        return "superuser" in user.roles or "admin" in user.roles
    

class GalleryView(ModelView):
    fields=["id","title", "tags","photo_path","created_at"]
    searchable_fields=("id", "title", "tags","created_at")

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "admin_user", None)
        if not user:
            return False
        return bool({"superuser", "admin", "manager"} & set(user.roles))
    def can_create(self, request: Request)->bool:
        return True
    def can_edit(self, request: Request)->bool:
        return True
    def can_delete(self, request: Request)->bool:
        user=getattr(request.state, "admin_user", None)
        return "superuser" in user.roles or "admin" in user.roles

class UsersView(ModelView):
    fields=["email", "is_active", "role", "is_superuser", "is_verified"]
    searchable_fields=("email", "is_active", "role", "is_superuser", "is_verified")

    def is_accessible(self, request: Request) -> bool:
        user = getattr(request.state, "admin_user", None)
        if not user:
            return False

        return "superuser" in user.roles
    
    def can_edit(self, request: Request)->bool:
        user=getattr(request.state, "admin_user", None)
        if not user:
            return False
        
        return "superuser" in user.roles

class ContactView(ModelView):
    fields=["id", "first_name", "last_name", "your_email", "message"]
    searchable_fields=("id", "first_name", "last_name", "your_email", "message")

    def is_accessible(self, request: Request) -> bool:
        user=getattr(request.state, "admin_user", None)
        if not user:
            return False
        return bool({"superuser", "admin", "manager"} & set(user.roles))

    def can_delete(self, request: Request)->bool:
        user=getattr(request.state, "admin_user", None)
        return "superuser" in user.roles or "admin" in user.roles or "manager" in user.roles

