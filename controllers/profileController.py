from fastapi import HTTPException
from sqlalchemy.orm import Session
from controllers.authcontroller import get_information_token,create_access_token
from models import schemas
from models.instances import CreateUser, UpdateUser
def get_info_handler(token :str,db: Session):
    info = get_information_token(token)
    user = db.query(schemas.User).filter(schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")
    return {
        'status': 'success',
        'token': token,
        'data': {
            "username": user.username,
            "email": user.email,
            "address": user.address,
            "name": user.name,
            "role" : user.role
        }   
    }

def edit_info_handler(updated_info : UpdateUser,token :str,db: Session):
    info = get_information_token(token)
    user = db.query(schemas.User).filter(schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")
    user.username = updated_info.username
    user.name = updated_info.name
    user.address = updated_info.address
    db.add(user)
    db.commit()
    token = create_access_token(user.id)
    return {
        'status': 'success',
        'token': token,
        'data': {
            "username": user.username,
            "email": user.email,
            "address": user.address,
            "name": user.name,
        }   
    }


def delete_user_handler(token :str,db: Session):
    info = get_information_token(token)
    user = db.query(schemas.User).filter(schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")
    db.delete(user)
    db.commit()
    return {
        'status': 'success', 
    }
