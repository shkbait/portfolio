from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Photo_add_scheme(BaseModel):
    title: str
    tags: Optional[str]=None

class Photo_scheme(Photo_add_scheme):
        id: int
        photo_path: str
        created_at: datetime
class Photo_Update_scheme(BaseModel):
      title: Optional[str]=None
      tags: Optional[str]=None