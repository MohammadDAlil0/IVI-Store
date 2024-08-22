from starlette.requests import Request
from fastapi import  Depends, APIRouter,status
from models import schemas
from database import engine, get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models.instances import CreateUser
from controllers.authcontroller import sign_up, sign_in, oauth_sign_in, oauth_callback, changerole, refresh_token,verify_email,request_password_reset,reset_password   
schemas.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={401:{"user":"Not authurized"}}
)

@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def sign_up_handler(cur: CreateUser,db : Session = Depends(get_db)):
    return await sign_up(cur, db)

@router.post("/login",status_code=status.HTTP_200_OK)
async def sign_in_handler(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await sign_in(form_data, db)

@router.post("/changerole/{second_user_id}",status_code=status.HTTP_200_OK)
async def change_role(second_user_id,token: str = Depends(oauth2_bearer),db : Session = Depends(get_db)):
    print(token)
    return await changerole(second_user_id,token, db)

@router.post("/refresh",status_code=status.HTTP_200_OK)
async def refresh_access_token(token : str = Depends(oauth2_bearer),db : Session = Depends(get_db)):
    return await refresh_token(token, db)

@router.get("/oauth-login")
async def oauth_sign_in_handler(request: Request, status_code=status.HTTP_200_OK):
    return await oauth_sign_in(request)

@router.get('/auth-callback')
async def auth(request: Request, db: Session = Depends(get_db)):
    return await oauth_callback(request, db)

@router.get("/verify/{token}")
async def verify_email_handler(token: str, db: Session = Depends(get_db)):
    return await verify_email(token,db)

@router.post("/request-reset")
async def request_password_reset_handler(email: str, db: Session = Depends(get_db)):
    return await request_password_reset(email, db)

@router.post("/reset/{token}")
async def reset_handler(token: str, PasswordResetRequest: CreateUser , db: Session = Depends(get_db)):
    return reset_password(token, PasswordResetRequest.password, db)