from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json
from controllers.authcontroller import get_user_from_token
from models import schemas

import stripe

def create_cart(token: str, db: Session):
    user = get_user_from_token(db, token)
    cart = schemas.Cart()
    cart.created_at = datetime.utcnow()
    cart.user_id = user.id
    cart.done = False
    cart.products = "[]"
    jsonprods = json.loads(cart.products)
    cart.total = 0
    db.add(cart)
    db.commit()
    cart = db.query(schemas.Cart).filter(schemas.Cart.done ==
                                         False, schemas.Cart.user_id == user.id).first()
    user.cart_id = cart.id
    db.add(user)
    db.commit()
    return {
        "status": "success",
        "products": jsonprods,
        "total": cart.total
    }


async def get_cart(token: str, db: Session):
    user = get_user_from_token(db, token)
    if user.cart_id == -1:
        return create_cart(token, db)
    cart = db.query(schemas.Cart).filter(
        schemas.Cart.id == user.cart_id).first()
    if cart is None:
        return create_cart(token, db)
    jsonprods = json.loads(cart.products)
    return {
        "status": "success",
        "products": jsonprods,
        "total": cart.total
    }


async def end_cart(token: str, db: Session):
    user = get_user_from_token(db, token)
    cart = db.query(schemas.Cart).filter(
        schemas.Cart.id == user.cart_id).first()
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    try:
        line_items1 = []
        lst=eval(cart.products)
        for product in lst:
            line_items1.append({'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name':product.get("product_title"),
                },
                'unit_amount_decimal':product.get("price")*100 ,
            },
                'quantity': product.get("amount"),
            })
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items1,
            mode='payment',
            success_url='http://localhost:5173/user/cart/success',
            cancel_url='http://localhost:5173/user/cart/cancel',
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    cart.done = True
    user.cart_id = -1
    db.add(user)
    db.add(cart)
    db.commit()
    return {
        "status": "success",
        "location": checkout_session.url
    }


async def add_element_to_cart(product_id, amount: str, token: str, db: Session):
    amount = int(amount)
    user = get_user_from_token(db, token)
    if user.cart_id == -1 :
        create_cart(token,db)
    cart = db.query(schemas.Cart).filter(
        schemas.Cart.id == user.cart_id).first()
    product = db.query(schemas.Product).filter(
        schemas.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if cart == -1:
        raise HTTPException(status_code=404, detail="cart not found")
    prods = json.loads(cart.products)
    jsonprods = prods
    found: bool = False
    for item in prods:
        if item["product_id"] == product_id:
            found = True
            if item["amount"]+amount < 0:
                raise HTTPException(status_code=400, detail="Wrong value")
            item["amount"] += amount
            item["price"] += amount*product.price
    if amount < 0 and found == False:
        raise HTTPException(status_code=400, detail="Wrong value")
    if found == False:
        photos=eval(product.photo)
        prods.append({"product_id": product_id, "product_title": product.title,
                     "amount": amount, "price": amount*product.price , "img":photos[0]})
    prods = json.dumps(prods)
    cart.products = prods
    cart.total = cart.total + amount*product.price
    db.add(cart)
    db.commit()
    return {
        "status": "success",
        "products": jsonprods,
        "total": cart.total
    }
