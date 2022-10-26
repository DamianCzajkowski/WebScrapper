from simple_term_menu import TerminalMenu
from sqlalchemy import select
from tabulate import tabulate

from database import initialize_database
from models import Product as ProductModel
from models import Shop as ShopModel
from schema import Product as ProductSchema
from schema import Shop as ShopSchema
from scrap import scrap_product


def main():
    session = initialize_database()
    options = ["Product", "Shop", "Exit"]
    terminal_menu = TerminalMenu(options)
    match terminal_menu.show():
        case 0:
            options = [
                "Add new product",
                "List products",
                "Update product",
                "Delete product",
                "Back",
            ]
            terminal_menu = TerminalMenu(options)
            match terminal_menu.show():
                case 0:
                    url = input("Provide product url: ")
                    # TODO add selection of providing new shop or select from the list of already created
                    shop = session.scalar(
                        select(ShopModel).where(ShopModel.name == "XKOM")
                    )
                    parsed_shop = ShopSchema(**shop.__dict__)
                    product = scrap_product(url, parsed_shop)
                    session.add(product)
                case 1:
                    products = session.scalars(select(ProductModel))
                    parsed_products = [
                        ProductSchema(**product.__dict__).dict() for product in products
                    ]
                    print(
                        tabulate(
                            parsed_products,
                            headers="keys",
                            tablefmt="simple_grid",
                        )
                    )
                case 2:
                    pass
                case 3:
                    pass
                case _:
                    return
        case 1:
            options = ["Add new shop", "List Shops", "Back"]
            terminal_menu = TerminalMenu(options)
            match terminal_menu.show():
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
                    pass
                case _:
                    return

        case 2:
            session.commit()
            session.close()
            return

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
