from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class Product(BaseModel):
    id: Optional[int]
    url: AnyHttpUrl
    price: float
    name: str
    shop_id: Optional[int]

    class Config:
        orm_mode = True


class Shop(BaseModel):
    id: Optional[int]
    name: str
    product_name_class: str
    product_price_class: str
    products: Optional[list[Product]] = []

    class Config:
        orm_mode = True
