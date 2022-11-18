from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Shop(Base):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)


class ShopProductNameClass(Base):
    __tablename__ = "shop_product_name_class"
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    shop_id = Column(Integer, ForeignKey("shop.id", ondelete="CASCADE"))
    shop = relationship(
        "Shop",
        backref=backref("product_name_classes", cascade="all, delete"),
    )

    __table_args__ = (UniqueConstraint("shop_id", "class_name", name="class_shop_uc"),)


class ShopProductPriceClass(Base):
    __tablename__ = "shop_product_price_class"
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String)
    shop_id = Column(Integer, ForeignKey("shop.id", ondelete="CASCADE"))
    shop = relationship(
        "Shop", backref=backref("product_price_classes", cascade="all, delete")
    )
    __table_args__ = (UniqueConstraint("shop_id", "class_name", name="class_shop_uc"),)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True)
    price = Column(Float)
    name = Column(String)
    shop_id = Column(Integer, ForeignKey("shop.id", ondelete="CASCADE"))
    shop = relationship("Shop", backref=backref("products", cascade="all, delete"))
    __table_args__ = (UniqueConstraint("shop_id", "url", name="url_shop_uc"),)


class ProductHistory(Base):
    __tablename__ = "product_history"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    price = Column(Float)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"))
    product = relationship("Product", backref=backref("history", cascade="all, delete"))
