import requests
from bs4 import BeautifulSoup

from models import Product as ProductModel
from schema import Product as ProductSchema
from schema import Shop


def scrap_product(url: str, shop: Shop) -> ProductModel:
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, "lxml")
    float_price = 0.0

    for product_price_class in shop.product_price_classes:
        if price := soup.find("div", {"class": product_price_class.class_name}):
            price = price.get_text()
            float_price = float(price.split("zł")[0].replace(" ", "").replace(",", "."))
    name = ""
    for product_name_class in shop.product_name_classes:
        if name_class := soup.find("h1", {"class": product_name_class.class_name}):
            name = name_class.get_text()
    # Check if product already exists in database and create a product history
    product = ProductSchema(
        url=url, price=float_price, name=name, shop_id=shop.id, shop=shop
    )
    return ProductModel(**product.dict())
