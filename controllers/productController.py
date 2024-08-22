from sqlalchemy.orm import Session
from fastapi import status, HTTPException,File,UploadFile
from models.instances import CreateProduct, UpdateProduct
from controllers.authcontroller import get_admin_info, get_user_from_token
from utils.embading_images import embeding_photo
# from utils.embedding_text import embeding_text
from models import schemas
from database import get_mongodb 
from bson.objectid import ObjectId
import ast
from sqlalchemy import func
from utils.embedding_huggingface import generate_embedding_local
from utils.classification import class_photo

async def create_product(product: CreateProduct, db: Session, token: str, file: UploadFile = File(...)):
    try:
        get_admin_info(db, token)
    
        mongo_db_collection = get_mongodb()
    
        newProduct = schemas.Product()
        newProduct.title = product["title"]
        newProduct.price = product["price"]
        newProduct.amount = product["amount"]
        newProduct.category = product["category"]
        newProduct.tags = product["tags"]
        newProduct.brand = product["brand"]
    
        category_mapping = {
            'accessories': ['glasses', 'hat'],
            'bottoms': ['shorts', 'trousers'],
            'dress': ['dress'],
            'tops': ['jacket', 'shirt', 'sweater', 't-shirt', 'tank-    top'],
            'shoes': ['sandals', 'sneakers']
        }

        for cls, items in category_mapping.items():
            if newProduct.category in items:
                newProduct.cls = cls
                break
        if newProduct.cls is None:
            raise HTTPException(status_code=400, detail="category must be one of those: ['glasses', 'hat', 'shorts', 'trousers', 'dress', 'jacket', 'shirt', 'sweater', 't-shirt', 'tank-top', 'sandals', 'sneakers']")
    
        photo_info = await embeding_photo(file)
        text_info = generate_embedding_local(newProduct.title)
    
        mongo_product = mongo_db_collection.insert_one({
            "photo_embedding": photo_info[0].tolist(),
            "title_embedding": text_info
        })
        newProduct.id = str(mongo_product.inserted_id)
        newProduct.photo = "['" + photo_info[1] + "']"
        db.add(newProduct)
        db.commit()
    
        return {
            "status": "success",
            "data": {
                "id": newProduct.id,
                "title": newProduct.title,
                "photo": newProduct.photo,
                "price": newProduct.price,
                "amount": newProduct.amount,
                "category": newProduct.category,
                "tags": newProduct.tags,
                "class": newProduct.cls,
                "brand": newProduct.brand
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_all_products(db: Session, page: int, limit: int, search: str, money: int, amount: int, cls: str, category: str, order: bool):
    # Start the query
    if order:
        query = db.query(schemas.Product).order_by(schemas.Product.average_rate.desc())
    else:
        query = db.query(schemas.Product).order_by(func.random())
    
    if search:
        #Sementic Search 
        products_id = await suggest_products_by_text(search, db)
    
        arr = []
        for product_id in products_id:
            arr.append(str(product_id))
        products_id = arr
        query = query.filter(schemas.Product.id.in_(products_id))
        

    # Apply additional filters if provided
    if money is not None:
        query = query.filter(schemas.Product.price <= money)
    
    if amount is not None:
        query = query.filter(schemas.Product.amount >= amount)
    
    if cls:
        query = query.filter(schemas.Product.cls == cls)

    if category:
        query = query.filter(schemas.Product.category == category)

    # Paginate the results
    products = query.limit(limit).offset((page - 1) * limit).all()

    for product in products:
        product.photo = ast.literal_eval(product.photo)
    
    return {
        "status": "success",
        "result": len(products),
        "data": products
    }

async def getProduct(product_id: str, db: Session):
    product = db.query(schemas.Product).filter(schemas.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid ID')
        
    product.photo = ast.literal_eval(product.photo)
    return {
        "status": "success",
        "data": product
    }

async def delete_product(db: Session, product_id: str, token: str):
    get_admin_info(db, token)
    db_product = db.query(schemas.Product).filter(schemas.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='invalid ID')
    db.delete(db_product)
    db.commit()
    return {
        "status": "success",
    }

#add validaiotn
async def update_product(db: Session, product_id: str, updated_product: UpdateProduct, token: str):
    get_admin_info(db, token)
    db_product = db.query(schemas.Product).filter(schemas.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid product's ID")

    for key, value in updated_product.model_dump().items():
        print(key, value)
        if value == None:
            continue
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    db_product.photo = ast.literal_eval(db_product.photo)
    return {
        "status": "sucess",
        "data": db_product
    }

async def rate_product(db: Session, product_id: str, number_stars: int, token: str):
    user = get_user_from_token(db, token)
    exist = db.query(schemas.Rate).filter(schemas.Rate.product_id == product_id).filter(schemas.Rate.user_id == user.id).first()   
    if exist is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already voted for this product")
    
    newRate = schemas.Rate()
    newRate.product_id = product_id
    newRate.user_id = user.id
    newRate.stars = number_stars
    db.add(newRate)
    db.commit()

    db_product = db.query(schemas.Product).filter(schemas.Product.id == product_id).first()
    db_product.sum_of_stars += number_stars
    db_product.cnt_voter += 1
    db_product.average_rate = 1.0 * db_product.sum_of_stars / db_product.cnt_voter

    db.commit()
    db.refresh(db_product)

    db_product.photo = ast.literal_eval(db_product.photo)
    return {
        "status": "success",
        "data": db_product
    }

async def suggest_products_by_image(db: Session, file: UploadFile = File(...)):
    try:
        object = await embeding_photo(file)
        embedded_photo = object[0].tolist()
        mongo_db = get_mongodb()
        results = mongo_db.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": embedded_photo,
                    "path": "photo_embedding",
                    "numCandidates": 6500,
                    "limit": 40,
                    "index": "photo_index",
                }
            }  
        ])

        products_id = [document["_id"] for document in results]
        
        
        arr = []
        for product_id in products_id:
            arr.append(str(product_id))
        products_id = arr
        
        
        if products_id:  # Check if the list is not empty
            sql_results = db.query(schemas.Product).filter(schemas.Product.id.in_(products_id)).all()
        else:
            sql_results = []
            
        for product in sql_results:
            product.photo = ast.literal_eval(product.photo)
    

        return {
            "status": "success",
            "result": len(sql_results),
            "data": sql_results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def suggest_products_by_text(text: str, db: Session):
    try:
        embedded_title = generate_embedding_local(text)
        mongo_db = get_mongodb()
    
        results = mongo_db.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": embedded_title.tolist(),
                    "path": "title_embedding",
                    "numCandidates": 6500,
                    "limit": 10,
                    "index": "title_index",
                }
            }  
        ])
        
        products_id = [document["_id"] for document in results]
        return products_id

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def recommended_products(product_id: str, db: Session):
    mongo_db = get_mongodb()
    mongo_db_product = mongo_db.find_one({"_id": ObjectId(product_id)})

    if not mongo_db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if mongo_db_product.get('photo_embedding') is None:
        raise HTTPException(status_code=400, detail="Product does not have photo embedding")

    results = mongo_db.aggregate([
        {
            "$vectorSearch": {
                "queryVector": mongo_db_product.get('photo_embedding'),
                "path": "photo_embedding",
                "numCandidates": 6500,
                "limit": 10,
                "index": "photo_index",
            }
        }
    ])

    products_id = [document["_id"] for document in results]
    
    arr = []
    for p_id in products_id:
        if str(p_id) != product_id:
            arr.append(str(p_id))
    products_id = arr
        

    if products_id:  # Check if the list is not empty
        sql_results = db.query(schemas.Product).filter(schemas.Product.id.in_(products_id)).all()
    else:
        sql_results = []
        
    for product in sql_results:
            product.photo = ast.literal_eval(product.photo)

    return {
        "status": "success",
        "result": len(sql_results),
        "data": sql_results
    }
    
    
async def class_image(file: UploadFile = File(...)):
     x = await class_photo(file)
     arr = ["accessories", "bottoms", "dress", "shoes", "tops"]
     print("predicted_class:",x)
     return {
         "status": "success",
         "class": arr[int(x["predicted_class"])]
     }
