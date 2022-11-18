from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class Product(BaseModel):
    id: Optional[int] = None
    url: AnyHttpUrl
    price: float
    name: str
    shop_id: Optional[int]
    history: Optional[list] = []

    class Config:
        orm_mode = True


class ProductHistory(BaseModel):
    id: Optional[int] = None
    created_at: datetime
    price: float
    product_id: Product


class Shop(BaseModel):
    id: Optional[int] = None
    name: str
    product_name_classes: list
    product_price_classes: list
    products: Optional[list[Product]] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ShopProductNameClass(BaseModel):
    id: Optional[int] = None
    shop_id: Optional[int]
    class_name: str

    class Config:
        orm_mode = True


class ShopProductPriceClass(BaseModel):
    id: Optional[int] = None
    shop_id: Optional[int]
    class_name: str

    class Config:
        orm_mode = True
