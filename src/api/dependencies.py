from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, Field
from src.database import AsyncSession,get_session

SessionDep=Annotated[AsyncSession,Depends(get_session)]

class PaginationParams(BaseModel):
    limit: int=Field(20,ge=0,le=100,description="Pieces")
    offset: int=Field(0,ge=0,description="Offset")

PaginationDep=Annotated[PaginationParams, Depends(PaginationParams)]