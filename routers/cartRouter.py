from fastapi import APIRouter,status,Depends
from sqlalchemy.orm import Session
from database import get_db
from controllers.cartController import add_element_to_cart, end_cart, get_cart
from routers.authRouter import oauth2_bearer

router = APIRouter(
     prefix="/cart",
    tags=["Cart"],
    responses={401:{"cart":"Not found"}}
)


@router.get("/getCart",status_code=status.HTTP_201_CREATED)
async def create_cart_handler(token : str = Depends(oauth2_bearer),db : Session = Depends(get_db)):
    return await get_cart(token,db)

@router.get("/endCart",status_code=status.HTTP_200_OK)
async def end_cart_handler(token : str = Depends(oauth2_bearer),db : Session = Depends(get_db)):
    return await end_cart(token,db)


@router.post("/addProducttToCart/{product_id}/{amount}",status_code=status.HTTP_201_CREATED)
async def add_element_to_cart_handler(product_id,amount,token : str = Depends(oauth2_bearer),db : Session = Depends(get_db)):
    return await add_element_to_cart(product_id,amount,token,db)