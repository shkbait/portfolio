from pydantic import BaseModel
from typing import Optional

class Photo_add_scheme(BaseModel):
    title: str

class Photo_scheme(Photo_add_scheme):
        id: int
        photo_path: str
class Photo_Update_scheme(BaseModel):
      title: Optional[str]=None