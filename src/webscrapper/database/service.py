from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select, update

from webscrapper.database.models import Product as ProductModel
from webscrapper.database.models import ProductHistory as ProductHistoryModel
from webscrapper.database.models import Shop as ShopModel
from webscrapper.database.models import ShopProductNameClass as ShopProductNameClassModel
from webscrapper.database.models import ShopProductPriceClass as ShopProductPriceClassModel
from webscrapper.schema import Product as ProductSchema
from webscrapper.schema import ProductHistory as ProductHistorySchema
from webscrapper.schema import Shop as ShopSchema
from webscrapper.schema import ShopProductNameClass as ShopProductNameClassSchema
from webscrapper.schema import ShopProductPriceClass as ShopProductPriceClassSchema
from webscrapper.scrapper.scrap import scrap_product


class AbstractService:
    def __init__(self, session):
        self.session = session


class ProductService(AbstractService):
    def create_product(self, shop_name: str, url: str):
        shop = self.session.scalar(select(ShopModel).where(ShopModel.name == shop_name))

        product = scrap_product(url, shop)
        product = ProductModel(**product.dict())

        product_history = self._add_product_history(product)

        self.session.add(product)
        self.session.add(product_history)
        self.session.commit()
        return product.id

    def get_product_by_id(self, product_id: int):
        return self.session.scalar(select(ProductModel).where(ProductModel.id == product_id))

    def refresh_product(self, product_id: int):
        product = self.session.scalar(select(ProductModel).where(ProductModel.id == product_id))

        new_product = scrap_product(product.url, product.shop)
        self.update_product(
            product.id, details={"url": new_product.url, "price": new_product.price, "name": new_product.name}
        )
        product = self.session.scalar(select(ProductModel).where(ProductModel.id == product_id))

        product_history = self._add_product_history(product)

        self.session.add(product_history)
        self.session.commit()

    def _add_product_history(self, product):
        return ProductHistoryModel(
            created_at=datetime.now(),
            product_id=product.id,
            product=product,
            price=product.price,
        )

    def get_product_details(self, id):
        product = self.get_product_by_id(id)

        product_history = self._parse_product_history(product)

        return ProductSchema(
            id=product.id,
            name=product.name,
            url=product.url,
            price=product.price,
            shop_id=product.shop_id,
            history=product_history,
        )

    def _parse_product_history(self, product):
        return [
            ProductHistorySchema(**history.__dict__, product=product, product_id=product.id)
            for history in product.history
        ]

    def get_all_products(self):
        products = self.session.scalars(select(ProductModel))
        return [ProductSchema(**product.__dict__) for product in products]

    def update_product(self, product_id, details):
        self.session.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**details)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def delete_product(self, item_id):
        shop = self.session.scalar(select(ProductModel).where(ProductModel.id == item_id))
        self.session.delete(shop)
        self.session.commit()


class ShopService(AbstractService):
    def create_shop(
        self,
        shop_name: str,
        price_classes: Optional[list] = None,
        name_classes: Optional[list] = None,
    ):

        shop = ShopModel(name=shop_name)
        self.session.add(shop)
        if price_classes:
            for price_class in price_classes:
                shop_product_price_class = ShopProductPriceClassModel(
                    class_name=price_class, shop=shop, shop_id=shop.id
                )
                self.session.add(shop_product_price_class)
        if name_classes:
            for class_name in name_classes:
                shop_product_name_class = ShopProductNameClassModel(class_name=class_name, shop=shop, shop_id=shop.id)
                self.session.add(shop_product_name_class)
        self.session.commit()
        return shop.id

    def get_shop_by_id(self, shop_id: int):
        return self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))

    def get_product_price_class_by_id(self, item_id: int):
        return self.session.scalar(select(ShopProductPriceClassModel).where(ShopProductPriceClassModel.id == item_id))

    def get_product_name_class_by_id(self, item_id: int):
        return self.session.scalar(select(ShopProductNameClassModel).where(ShopProductNameClassModel.id == item_id))

    def _parse_shop(self, shop):
        product_name_classes = self._parse_product_name_classes(shop)
        product_price_classes = self._parse_product_price_classes(shop)

        return ShopSchema(
            id=shop.id,
            name=shop.name,
            product_name_classes=product_name_classes,
            product_price_classes=product_price_classes,
        )

    def get_all_shops(self):
        shops = self.session.scalars(select(ShopModel))
        return [self._parse_shop(shop) for shop in shops]

    def _parse_product_name_classes(self, shop):
        return [
            ShopProductNameClassSchema(**name_class.__dict__, shop=shop) for name_class in shop.product_name_classes
        ]

    def _parse_product_price_classes(self, shop):
        return [
            ShopProductPriceClassSchema(**price_class.__dict__, shop=shop) for price_class in shop.product_price_classes
        ]

    def parse_product_price_class(self, class_price: str, shop: ShopModel):
        return ShopProductPriceClassModel(class_name=class_price, shop=shop, shop_id=shop.id)

    def parse_product_name_class(self, class_name: str, shop: ShopModel):
        return ShopProductNameClassModel(class_name=class_name, shop=shop, shop_id=shop.id)

    def update_shop(self, shop_id, shop_details):
        self.session.execute(
            update(ShopModel)
            .where(ShopModel.id == shop_id)
            .values(**shop_details)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def update_price_class(self, item_id, item_details):
        self.session.execute(
            update(ShopProductPriceClassModel)
            .where(ShopProductPriceClassModel.id == item_id)
            .values(**item_details)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def update_name_class(self, item_id, item_details):
        self.session.execute(
            update(ShopProductNameClassModel)
            .where(ShopProductNameClassModel.id == item_id)
            .values(**item_details)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def delete_shop(self, shop_id):
        shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))
        self.session.delete(shop)
        self.session.commit()

    def delete_product_price_class(self, item_id):
        self.session.execute(
            delete(ShopProductPriceClassModel)
            .where(
                ShopProductPriceClassModel.id == item_id,
            )
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def delete_product_name_class(self, item_id):
        self.session.execute(
            delete(ShopProductNameClassModel)
            .where(
                ShopProductNameClassModel.id == item_id,
            )
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def search_shop(self):
        pass
