from starlette_admin.contrib.sqla import ModelView


class View(ModelView):
    fields = ["id", "title", "main_text", "pic_path"]
    searchable_fields = ("title", "main_text")

class GalleryView(ModelView):
    fields=["id","title", "photo_path"]
    searchable_fields=("id", "title")

class UsersView(ModelView):
    fields=["email", "is_active", "is_superuser", "is_verified"]
    searchable_fields=("email", "is_active", "is_superuser", "is_verified")

class ContactView(ModelView):
    fields=["id", "first_name", "last_name", "your_email", "message"]
    searchable_fields=("id", "first_name", "last_name", "your_email", "message")