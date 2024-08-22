 
import sys
sys.path.append("..")
from fastapi import Depends, APIRouter, File, Form, UploadFile, status, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.instances import CreateProduct, UpdateProduct
from controllers.productController import create_product, get_all_products, getProduct, delete_product, update_product, rate_product,suggest_products_by_image, suggest_products_by_text, recommended_products, class_image
from routers.authRouter import oauth2_bearer
router = APIRouter(
    prefix = "/product",
    tags = ["product"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product_handler(
    title: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    amount: int = Form(...),
    category: str = Form(...),
    tags: str = Form(...),
    brand: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_bearer)
):
    product: CreateProduct = {
        "title": title,
        "price": price,
        "description": description,
        "amount": amount,
        "category": category,
        "tags": tags,
        "brand": brand
    }
    return await create_product(product, db, token, file)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_all_product_handler(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page numebr"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query("", description="Search based title of products"), 
    money: int = Query(None, ge=0, description="filtering by less price"), 
    amount: int = Query(None, ge=1, description="amount of items"),
    cls: str = Query(None, description="filter by class"),
    category: str = Query(None, description="filter by category"),
    order: bool = Query(True, description="order by rate or not")
):
    try: 
        return await get_all_products(db, page, limit, search, money, amount, cls, category, order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product_handler(product_id: str, db: Session = Depends(get_db)):
    return await getProduct(product_id, db)


@router.put('/{product_id}', status_code=status.HTTP_200_OK)
async def update_product_handler(product_id: str, product: UpdateProduct, db: Session = Depends(get_db), token :str = Depends(oauth2_bearer)):
    return await update_product(db, product_id, product, token)

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product_handler(product_id: str, db: Session = Depends(get_db), token :str = Depends(oauth2_bearer)):
    return await delete_product(db, product_id, token)

@router.post('/rateProduct/{product_id}', status_code=status.HTTP_200_OK)
async def rate_product_handler(product_id: str, number_stars: int, db: Session = Depends(get_db), token :str = Depends(oauth2_bearer)):
    return await rate_product(db, product_id, number_stars, token)

@router.post('/suggestProductsByImage', status_code=status.HTTP_200_OK)
async def suggest_products_by_image_handler(db: Session = Depends(get_db), file: UploadFile = File(...)):
    return await suggest_products_by_image(db, file)

@router.post('/recommended_products/{product_id}', status_code=status.HTTP_200_OK)
async def recommended_products_handler(product_id: str, db: Session = Depends(get_db)):
    return await recommended_products(product_id, db)

@router.post('/classImage', status_code=status.HTTP_200_OK)
async def class_image_handler(file: UploadFile = File(...)):
    return await class_image(file)