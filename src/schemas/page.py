from pydantic import BaseModel
from typing import Optional


class AddPage_scheme(BaseModel):
    title: str
    main_text: Optional[str]=None

class Page_scheme(AddPage_scheme):
    id: int
    pic_path: Optional[str]=None
    
class Page_Update_scheme(BaseModel):
    main_text: Optional[str]=None

    
