# models.py
from sqlalchemy import Column, Integer, String, Double, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()  # Ensure this is defined correctly

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    name = Column(String)
    email = Column(String, unique=True)
    address = Column(String)
    cart_id = Column(Integer,default=-1)
    role = Column(Integer, default=0)
    hashed_password = Column(String, default=None)
    is_verified = Column(Boolean, default=False)
    auth_type = Column(Integer, default=0)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
 
    user_rate_relation = relationship("Rate",back_populates="rate_user_relation")
    user_order_relation = relationship("Cart",back_populates="order_user_relation")

class Product(Base):
    __tablename__ = "product"
    id = Column(String,primary_key=True,index=True,autoincrement=False)
    title = Column(String)
    photo = Column(String)
    price = Column(Double)
    amount = Column(Integer)
    category = Column(String)
    tags = Column(String)
    cnt_voter = Column(Integer, default=0)
    sum_of_stars = Column(Integer, default=0)
    average_rate = Column(Double, default=0)
    cls = Column(String)
    brand = (String)

    product_rate_relation = relationship("Rate",back_populates="rate_product_relation")

class Rate(Base):
    __tablename__ = "rate"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    product_id = Column(Integer,ForeignKey("product.id"))
    stars = Column(Integer)

    rate_user_relation = relationship("User",back_populates="user_rate_relation")
    rate_product_relation = relationship("Product",back_populates="product_rate_relation")

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("user.id"))
    done = Column(Boolean)
    products = Column(String)
    created_at = Column(Date)
    total = Column(Integer)

    order_user_relation = relationship("User",back_populates="user_order_relation")
    # order_product_relation = relationship("Product",back_populates="product_order_relation")

