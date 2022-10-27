from requests import delete
from simple_term_menu import TerminalMenu
from sqlalchemy import select, update, delete
from tabulate import tabulate

from database import initialize_database
from models import Product as ProductModel
from models import Shop as ShopModel
from schema import Product as ProductSchema
from schema import Shop as ShopSchema
from scrap import scrap_product


def main():
    session = initialize_database()
    main_menu_exit = False
    main_menu_options = ["Product", "Shop", "Exit"]
    main_menu = TerminalMenu(main_menu_options)
    while not main_menu_exit:
        match main_menu.show():
            case 0:
                product_menu_back = False
                product_menu_options = [
                    "Add new product",
                    "List products",
                    "Delete product",
                    "Back",
                ]
                product_menu = TerminalMenu(product_menu_options)
                while not product_menu_back:
                    match product_menu.show():
                        case 0:  # Adding new product
                            print(
                                "Select the store from which you want to add the product: "
                            )
                            shops = session.scalars(select(ShopModel))
                            all_shops = shops.all()
                            shop_names = [shop.name for shop in all_shops]
                            shop_list_menu = TerminalMenu(shop_names)
                            shop_entry_index = shop_list_menu.show()
                            url = input("Provide product url: ")
                            parsed_shop = ShopSchema(
                                **all_shops[shop_entry_index].__dict__
                            )
                            product = scrap_product(url, parsed_shop)
                            session.add(product)
                        case 1:  # Listing products
                            products = session.scalars(select(ProductModel))
                            parsed_products = [
                                ProductSchema(**product.__dict__).dict()
                                for product in products
                            ]
                            print(
                                tabulate(
                                    parsed_products,
                                    headers="keys",
                                    tablefmt="simple_grid",
                                )
                            )
                        case 2:  # delete product
                            products = session.scalars(select(ProductModel))
                            parsed_products = [
                                ProductSchema(**product.__dict__).dict()
                                for product in products
                            ]
                            print(
                                tabulate(
                                    parsed_products,
                                    headers="keys",
                                    tablefmt="simple_grid",
                                )
                            )
                            product_id = int(
                                input("Provide product id that you want to delete: ")
                            )
                            session.execute(
                                delete(ShopModel)
                                .where(ShopModel.id == product_id)
                                .execution_options(synchronize_session="fetch")
                            )
                        case 3:
                            product_menu_back = True
            case 1:
                shop_menu_back = False
                shop_menu_options = ["Add new shop", "List Shops", "Back"]
                shop_menu = TerminalMenu(shop_menu_options)
                while not shop_menu_back:
                    match shop_menu.show():
                        case 0:
                            name = input("Provide shop name: ")
                            class_price = input("Provide price class: ")
                            class_name = input("Provide product class name: ")
                            shop = ShopSchema(
                                name=name,
                                product_name_class=class_name,
                                product_price_class=class_price,
                            )
                            session.add(ShopModel(**shop.dict()))
                        case 1:
                            shops = session.scalars(select(ShopModel))
                            parsed_shops = [
                                ShopSchema(**shop.__dict__).dict() for shop in shops
                            ]
                            print(
                                tabulate(
                                    parsed_shops,
                                    headers="keys",
                                    tablefmt="simple_grid",
                                )
                            )
                        case 2:
                            shop_menu_back = True
            case 2:
                session.commit()
                session.close()
                main_menu_exit = True


if __name__ == "__main__":
    main()
