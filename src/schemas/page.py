from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AddPage_scheme(BaseModel):
    title: str
    main_text: Optional[str]=None
    tags: Optional[str]=None

class Page_scheme(AddPage_scheme):
    id: int
    pic_path: Optional[str]=None
    created_at: datetime
    
class Page_Update_scheme(BaseModel):
    main_text: Optional[str]=None
    tags: Optional[str]=None

    
