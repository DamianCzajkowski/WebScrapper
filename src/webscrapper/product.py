from pydantic import BaseModel, AnyHttpUrl


class Product(BaseModel):
    url: AnyHttpUrl
    price: float
