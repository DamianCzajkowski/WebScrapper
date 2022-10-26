from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()


class Shop(Base):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    product_name_class = Column(String)
    product_price_class = Column(String)
    products = relationship("Product", back_populates="shop")


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    price = Column(Float)
    name = Column(String)
    shop_id = Column(Integer, ForeignKey("shop.id"))
    shop = relationship("Shop", back_populates="products")
