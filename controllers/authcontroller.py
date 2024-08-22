from fastapi import HTTPException, Depends
from datetime import timedelta, datetime
from decouple import config
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from models import schemas
from models.instances import CreateUser
from models.schemas import User
import uuid
from sqlalchemy.orm import Session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth = OAuth()

oauth.register(
    name='google',
    server_metadata_url=os.getenv('SERVER_METADATA_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int):
    de = int(os.getenv('TIME_DELTA'))
    expire_delta = timedelta(hours=de)
    exp = datetime.utcnow() + expire_delta
    encoded = {
        "id": user_id,
        "exp": exp
    }
    return jwt.encode(encoded, os.getenv("SECRET_KEY"), os.getenv('ALGORITHM'))

def get_user_from_token(db: Session, token: str):
    info = get_information_token(token)
    print(info)
    user = db.query(schemas.User).filter(
        schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_admin_info(db: Session, token: str):
    info = get_information_token(token)
    user = db.query(schemas.User).filter(
        schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role < 1:
        raise HTTPException(status_code=403, detail="You need to be an admin")
    return user

def check_admin(db: Session, token: str) -> bool:
    info = get_information_token(token)
    user = db.query(schemas.User).filter(
        schemas.User.id == info.get("user_id")).first()
    if user is None or user.role != 1:
        return False
    return True

def get_information_token(token: str):
    try:
        user = jwt.decode(token, os.getenv('SECRET_KEY'), os.getenv('ALGORITHM'))
        user_id = user.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=404, detail="User ID not found in token.")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")

def verify_user(username: str, password: str, db: Session) -> bool:
    if not username or not password:
        raise ValueError("Username and password must be provided.")

    user = db.query(schemas.User).filter(
        schemas.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return True

def send_verification_email(email: str, token: str):
    port = 1025  
    smtp_server = "localhost"
    sender_email = "noreply@example.com"  
    receiver_email = email
    
    html = f"""\
    <html>
        <body>
            <h2>Email Verification</h2>
            <p>Please verify your email by clicking the link below:</p>
            <a href="http://localhost:8000/auth/verify/{token}">Verify Email</a>
        </body>
    </html>
    """

    
    message = MIMEMultipart()
    message["Subject"] = "Email Verification"
    message["From"] = sender_email
    message["To"] = receiver_email

    
    message.attach(MIMEText(html, "html"))

    # with smtplib.SMTP(smtp_server, port) as server:
        
        # server.sendmail(sender_email, receiver_email, message.as_string())

def generate_reset_token(email: str) -> str:
    token = str(uuid.uuid4())
    return token

def send_reset_email(email: str, token: str):
    port = 1025  
    smtp_server = "localhost"
    sender_email = "noreply@example.com"
    
    html = f"""\\
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Please click the link below to reset your password:</p>
            <a href="http://localhost:8000/auth/reset/{token}">Reset Password</a>
        </body>
    </html>
    """
    
    message = f"""\\
    Subject: Password Reset Request
    From: {sender_email}
    To: {email}

    {html}
    """
    
    with smtplib.SMTP(smtp_server, port) as server:
        server.sendmail(sender_email, email, message)


async def sign_up(cur: CreateUser, db: Session):
    existing_user = db.query(schemas.User).filter(or_(
        schemas.User.email == cur.email,
        schemas.User.username == cur.username
    )).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="This email or username is already registered.")

    verification_token = str(uuid.uuid4())  

    newUser = User(
        username = cur.username,
        name = cur.name,
        email = cur.email,
        address = cur.address,
        is_verified = False, 
        verification_token = verification_token,
        auth_type = cur.auth_type
    )

    if cur.auth_type == 0:
        if not cur.password:
            raise HTTPException(status_code=400, detail="Password is required for local authentication.")
        hashed_password = get_password_hash(cur.password)
        newUser.hashed_password = hashed_password

    db.add(newUser)
    db.commit()

    
    send_verification_email(cur.email, verification_token)

    return {
        'status': 'success',
        'message': 'Please check your email to verify your account.',
        'data': {
            "username": newUser.username,
            "email": newUser.email,
            "address": newUser.address,
            "name": newUser.name
        }
    }

async def sign_in(form_data: OAuth2PasswordRequestForm , db: Session):
    user = db.query(schemas.User).filter(
        schemas.User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=404, detail="Invalid username or password.")

    token = create_access_token(user.id)

    return {
        'status': 'success',
        'access_token': token,
        'data': {
            "username": user.username,
            "email": user.email,
            "address": user.address,
            "name": user.name
        }
    }

async def changerole(second_person_id: int, token: str, db: Session):
    info = get_information_token(token)
    id = info.get("user_id")
    user = db.query(schemas.User).filter(id == schemas.User.id).first()
    second_person = db.query(schemas.User).filter(second_person_id == schemas.User.id).first()
    if user is None or second_person is None:
        raise HTTPException(status_code=404,detail="User not found!")
    if user.role >= 2:
        second_person.role ^=1
    else:
        raise HTTPException(status_code=403,detail="Unauthorized")
    db.add(second_person)
    db.commit()
    return {
        'status': 'success'
    }

async def refresh_token(token: str, db: Session):
    info = get_information_token(token)
    user = db.query(schemas.User).filter(
        schemas.User.id == info.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    refreshed_token = create_access_token(info.get("user_id"))
    return refreshed_token

async def oauth_sign_in(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

async def oauth_sign_in(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)

async def oauth_callback(request: Request, db: Session):
    try:
        googleToken = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="OAuth authorization failed: {}".format(str(e))
        )

    userInfo = googleToken.get('userinfo')
    email = userInfo.get("email")
    try:
        user = db.query(schemas.User).filter(schemas.User.email == email).first()
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query failed: {}".format(str(e))
        )

    if user:
        token = create_access_token(user.id)
        return {
            'status': 'success',
            'token': token,
            'data': {
                "username": user.username,
                "email": user.email,
                "address": user.address,
                "name": user.name
            }
        }
    else:
        try:
            newUser = schemas.User(
                username=userInfo.get("given_name"),
                email=email,
                name=userInfo.get("given_name"),
                address="Aleppo", 
                auth_type=1 
            )
            return await sign_up(newUser, db)
        except Exception as e:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR,detail="User creation failed: {}".format(str(e)))
            
    
async def verify_email(token: str, db: Session ):
    user = db.query(schemas.User).filter(schemas.User.verification_token == token).first()
    
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid verification token.")

    user.is_verified = True
    user.verification_token = None  
    db.commit()

    return {"msg": "Email verified successfully!"}

async def request_password_reset(email: str, db: Session):
    user = db.query(schemas.User).filter(schemas.User.email==email).first()
    if user:
        reset_token = generate_reset_token(email)
        
        user.reset_token = reset_token
        db.add(user)
        db.commit()        
        send_reset_email(email, reset_token)
        return {
            "status": "success",
            "message": "Password reset email sent."
        }
    
    raise HTTPException(status_code=404, detail="Email not found.")

async def reset_password(reset_token: str, new_password: str, db: Session):
    user = db.query(User).filter(User.reset_token == reset_token).first()
    
    if user:
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        db.add(user)
        db.commit()
        return {
            "status": "success",
            "message": "Password has been reset."
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
