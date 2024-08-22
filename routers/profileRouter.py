from fastapi import APIRouter,status,Depends
from sqlalchemy.orm import session
from database import get_db
from models.instances import UpdateUser
from controllers.authcontroller import check_admin
from controllers.profileController import get_info_handler,edit_info_handler,delete_user_handler
from routers.authRouter import oauth2_bearer

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    responses={404:{"user":"Not Found!"}}
)

@router.get("/myprofile",status_code=status.HTTP_200_OK)
async def get_info(token :str = Depends(oauth2_bearer),db: session = Depends(get_db)):
    return get_info_handler(token,db)


@router.put("/editmyprofile",status_code=status.HTTP_200_OK)
async def edit_info(updated_info: UpdateUser,token :str = Depends(oauth2_bearer),db: session = Depends(get_db)):
    return edit_info_handler(updated_info,token,db)

@router.delete("/deleteuser",status_code=status.HTTP_200_OK)
async def delete_user(token :str = Depends(oauth2_bearer),db: session = Depends(get_db)):
    return delete_user_handler(token,db)

@router.get("/checkadmin",status_code=status.HTTP_200_OK)
async def check_if_admin(token :str = Depends(oauth2_bearer),db: session = Depends(get_db)):
    return check_admin(token,db)
