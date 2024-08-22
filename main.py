from fastapi import FastAPI, Depends
from models import schemas
from database import engine , get_db
from sqlalchemy.orm import session
from routers import authRouter, productsRouter , profileRouter , cartRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

import os
import stripe

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

app = FastAPI()

origins = [
       os.getenv("LOCAL_URL"), 
   ]

app.add_middleware(SessionMiddleware, secret_key="add any string...")
app.add_middleware(
       CORSMiddleware,
       allow_origins="*",
       allow_credentials=True,
       allow_methods=["*"],     
       allow_headers=["*"],     
   )


app.include_router(authRouter.router)
app.include_router(productsRouter.router)
app.include_router(profileRouter.router)
app.include_router(cartRouter.router)
schemas.Base.metadata.create_all(bind=engine)
