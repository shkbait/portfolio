from typing import Annotated

from src.api.dependencies import PaginationDep
from src.api.repository import PagesRepo
from src.api import router
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from src.schemas.photo import Photo_add_scheme,Photo_scheme,Photo_Update_scheme

from src.users import current_active_user,current_superuser

admin_router=APIRouter(
    prefix="/gallery",
    dependencies=[Depends(current_superuser)]
)

public_router=APIRouter()

@admin_router.post("/upload_photo", tags=["gallery"])
async def upload_photo(data: Annotated[Photo_add_scheme,Depends()], file: UploadFile=File(...)):
    photo_id=await PagesRepo.upload_photo(data,file)
    return {"ok": True, "photo_id": photo_id}

@public_router.get("/get_photos", tags=["gallery"])
async def get_photos(pagination: PaginationDep)->list[Photo_scheme]:
    photos=await PagesRepo.get_photo()
    return photos[pagination.offset : pagination.offset + pagination.limit]

@public_router.get("/current_photo", tags=["gallery"])
async def get_photos_by_id(photo_id: int):
    photos=await PagesRepo.get_one_photo(photo_id)
    return photos



@admin_router.patch("/update_photo", tags=["gallery"])
async def update_photo(photo_id: int, data: Annotated[Photo_Update_scheme,Depends()], file: UploadFile)->Photo_scheme:
    result=await PagesRepo.update_photo(photo_id, data, file)
    if result is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return result

            # photo=await session.get(Photos_model,photo_id)
            # if photo is None:
            #     return False
            # if photo.photo_path is not None:
            #     Path(photo.photo_path).unlink(missing_ok=True)
            # await session.delete(photo)
            # await session.commit()
            # return True

@admin_router.delete("/delete_photo", tags=["gallery"])
async def delete_photo(photo_id:int):
    deleted=await PagesRepo.delete_photo(photo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Photo not Found")
    return {"ok":True}