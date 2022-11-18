from requests import delete
from simple_term_menu import TerminalMenu
from sqlalchemy import select, update, delete
from tabulate import tabulate
import curses

from models import (
    Product as ProductModel,
    ProductHistory as ProductHistoryModel,
    Shop as ShopModel,
    ShopProductNameClass as ShopProductNameClassModel,
    ShopProductPriceClass as ShopProductPriceClassModel,
)
from schema import (
    Shop as ShopSchema,
    Product as ProductSchema,
    ShopProductNameClass as ShopProductNameClassSchema,
    ShopProductPriceClass as ShopProductPriceClassSchema,
    ProductHistory as ProductHistorySchema,
)
from scrap import scrap_product
from datetime import datetime


class AbstractProduct:
    def __init__(self, session, main_screen):
        self.session = session
        self.main_screen = main_screen


class ProductService(AbstractProduct):
    def create_product(self):
        url = self._prompt_product_url()
        if not url:
            return
        shop_name = self._prompt_shop_name()
        shop = self.session.scalar(select(ShopModel).where(ShopModel.name == shop_name))
        product = scrap_product(url, shop)
        product_history = self._add_product_history(product)
        self.session.add(product)
        self.session.add(product_history)
        self.session.commit()
        self.main_screen.touchwin()
        self.main_screen.refresh()

    def _add_product_history(self, product):
        return ProductHistoryModel(
            created_at=datetime.now(),
            product_id=product.id,
            product=product,
            price=product.price,
        )

    def _prompt_product_url(self):
        line = 2

        tab = 6

        max_lines = 1
        max_cols = 120
        screen = curses.newwin(curses.LINES - 4, curses.COLS - 4, 2, 2)

        rectangle = screen.subwin(max_lines + 2, max_cols + 2, line + 1, tab)

        editwin = rectangle.subwin(max_lines + 1, max_cols, line + 2, tab + 1)

        while True:

            screen.clear()

            screen.addstr(0, tab - 2, "Product url:")
            editwin.clear()
            rectangle.border()

            screen.refresh()
            rectangle.refresh()
            editwin.refresh()

            curses.curs_set(1)
            curses.echo()
            text = editwin.getstr(0, 0).decode("utf-8")
            curses.noecho()
            curses.curs_set(0)

            screen.addstr(line + 3, tab, f"confirm Product url as {text}?")
            screen.addstr(line + 5, tab, "press ")
            tab += len("press ")
            screen.addstr(
                line + 5,
                tab,
                "ENTER",
                curses.A_BOLD,
            )
            tab += len("ENTER")
            screen.addstr(line + 5, tab, " to confirm, ")
            tab += len(" to confirm, ")
            screen.addstr(
                line + 5,
                tab,
                "q",
                curses.A_BOLD,
            )
            tab += len("q")
            screen.addstr(line + 5, tab, " for exit, press ")
            tab += len(" for exit, press ")
            screen.addstr(
                line + 5,
                tab,
                "any",
                curses.A_BOLD,
            )
            tab += len("any")
            screen.addstr(line + 5, tab, " other key to cancel")

            key = screen.getch()

            if key == ord("\n"):
                screen.clear()
                rectangle.clear()
                return text
            elif key == ord("q"):
                break
        del editwin
        del rectangle
        del screen
        self.main_screen.touchwin()
        self.main_screen.refresh()

    def _prompt_shop_name(self):
        line = 2

        tab = 6

        max_lines = 1
        max_cols = 60
        screen = curses.newwin(curses.LINES - 4, curses.COLS - 4, 2, 2)

        rectangle = screen.subwin(max_lines + 2, max_cols + 2, line + 1, tab)

        editwin = rectangle.subwin(max_lines + 1, max_cols, line + 2, tab + 1)

        while True:

            screen.clear()

            screen.addstr(0, tab - 2, "Shop name:")
            editwin.clear()
            rectangle.border()

            screen.refresh()
            rectangle.refresh()
            editwin.refresh()

            curses.curs_set(1)
            curses.echo()
            text = editwin.getstr(0, 0).decode("utf-8")
            curses.noecho()
            curses.curs_set(0)

            screen.addstr(line + 3, tab, f"confirm Shop name as {text}?")
            screen.addstr(line + 5, tab, "press ")
            tab += len("press ")
            screen.addstr(
                line + 5,
                tab,
                "ENTER",
                curses.A_BOLD,
            )
            tab += len("ENTER")
            screen.addstr(line + 5, tab, " to confirm, ")
            tab += len(" to confirm, ")
            screen.addstr(
                line + 5,
                tab,
                "q",
                curses.A_BOLD,
            )
            tab += len("q")
            screen.addstr(line + 5, tab, " for exit, press ")
            tab += len(" for exit, press ")
            screen.addstr(
                line + 5,
                tab,
                "any",
                curses.A_BOLD,
            )
            tab += len("any")
            screen.addstr(line + 5, tab, " other key to cancel")

            key = screen.getch()

            if key == ord("\n"):
                screen.clear()
                rectangle.clear()
                return text
            elif key == ord("q"):
                break
        del editwin
        del rectangle
        del screen
        self.main_screen.touchwin()
        self.main_screen.refresh()

    def get_product_details(self, name):
        product = self.session.scalar(
            select(ProductModel).where(ProductModel.name == name)
        )

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
            ProductHistorySchema(
                **history.__dict__, product=product, product_id=product.id
            )
            for history in product.history
        ]

    def get_all_products(self):
        products = self.session.scalars(select(ProductModel))
        return [ProductSchema(**product.__dict__) for product in products]

    def select_product(self):
        products_names = self.session.scalars(select(ProductModel.name)).all()
        product_list_menu = TerminalMenu(products_names)
        product_entry_index = product_list_menu.show()

        return products_names[product_entry_index]

    def update_product(self, details):
        product_name = self.select_product()
        self.session.execute(
            update(ProductModel)
            .where(ProductModel.name == product_name)
            .values(**details)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def delete_product(self, item_id):
        self.session.execute(
            delete(ProductModel)
            .where(ProductModel.id == item_id)
            .execution_options(synchronize_session="fetch")
        )
        self.session.commit()

    def display_product(self):
        pass

    def display_all_products(self):
        from main import Table, WindowSettings

        def refresh_product():
            products = self.get_all_products()
            return [
                (
                    product.id,
                    f"{product.url[:30]}...",
                    product.price,
                    product.name,
                    product.shop_id,
                )
                for product in products
            ]

        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )
        table = Table(
            refresh_product,
            ["ID", "URL", "PRICE", "NAME", "SHOP_ID"],
            None,
            self.delete_product,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return


class ShopService(AbstractProduct):
    def create_shop(self):
        from main import YesNoChoice

        name = self._prompt_get_shop_name()
        if not name:
            return
        shop = ShopModel(name=name)
        self.session.add(shop)
        ch = YesNoChoice(
            "Do you want to add Product price classes?", self.main_screen
        ).display()
        if ch:
            for price_class in self._prompt_price_class():
                shop_product_price_class = ShopProductPriceClassModel(
                    class_name=price_class, shop=shop, shop_id=shop.id
                )
                self.session.add(shop_product_price_class)
        ch = YesNoChoice(
            "Do you want to add Product name classes?", self.main_screen
        ).display()
        if ch:
            for class_name in self._prompt_name_class():
                shop_product_name_class = ShopProductNameClassModel(
                    class_name=class_name, shop=shop, shop_id=shop.id
                )
                self.session.add(shop_product_name_class)
        self.session.commit()
        self.main_screen.touchwin()
        self.main_screen.refresh()

    def _prompt_price_class(self):
        line = 2

        tab = 6

        max_lines = 1
        max_cols = 60
        screen = curses.newwin(curses.LINES - 4, curses.COLS - 4, 2, 2)

        rectangle = screen.subwin(max_lines + 2, max_cols + 2, line + 1, tab)

        editwin = rectangle.subwin(max_lines + 1, max_cols, line + 2, tab + 1)

        text = ""

        while True:

            screen.clear()

            screen.addstr(
                0,
                tab - 2,
                "Product price class (to add more than one just write it after comma):",
            )
            editwin.clear()
            rectangle.border()

            screen.refresh()
            rectangle.refresh()
            editwin.refresh()

            curses.curs_set(1)
            curses.echo()
            text = editwin.getstr(0, 0).decode("utf-8")
            curses.noecho()
            curses.curs_set(0)

            screen.addstr(
                line + 3,
                tab,
                f"confirm Product price classes as {text.strip().split(',')}?",
            )
            screen.addstr(line + 5, tab, "press ")
            tab += len("press ")
            screen.addstr(
                line + 5,
                tab,
                "ENTER",
                curses.A_BOLD,
            )
            tab += len("ENTER")
            screen.addstr(line + 5, tab, " to confirm, ")
            tab += len(" to confirm, ")
            screen.addstr(
                line + 5,
                tab,
                "q",
                curses.A_BOLD,
            )
            tab += len("q")
            screen.addstr(line + 5, tab, " for exit, press ")
            tab += len(" for exit, press ")
            screen.addstr(
                line + 5,
                tab,
                "any",
                curses.A_BOLD,
            )
            tab += len("any")
            screen.addstr(line + 5, tab, " other key to cancel")

            key = screen.getch()

            if key == ord("\n"):
                screen.clear()
                rectangle.clear()
                break
            elif key == ord("q"):
                break
        del editwin
        del rectangle
        del screen
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return text.strip().split(",")

    def _prompt_name_class(self):
        line = 2

        tab = 6

        max_lines = 1
        max_cols = 60
        screen = curses.newwin(curses.LINES - 4, curses.COLS - 4, 2, 2)

        rectangle = screen.subwin(max_lines + 2, max_cols + 2, line + 1, tab)

        editwin = rectangle.subwin(max_lines + 1, max_cols, line + 2, tab + 1)

        text = ""

        while True:

            screen.clear()

            screen.addstr(
                0,
                tab - 2,
                "Product name class (to add more than one just write it after comma):",
            )
            editwin.clear()
            rectangle.border()

            screen.refresh()
            rectangle.refresh()
            editwin.refresh()

            curses.curs_set(1)
            curses.echo()
            text = editwin.getstr(0, 0).decode("utf-8")
            curses.noecho()
            curses.curs_set(0)

            screen.addstr(
                line + 3,
                tab,
                f"confirm Product name classes as {text.strip().split(',')}?",
            )
            screen.addstr(line + 5, tab, "press ")
            tab += len("press ")
            screen.addstr(
                line + 5,
                tab,
                "ENTER",
                curses.A_BOLD,
            )
            tab += len("ENTER")
            screen.addstr(line + 5, tab, " to confirm, ")
            tab += len(" to confirm, ")
            screen.addstr(
                line + 5,
                tab,
                "q",
                curses.A_BOLD,
            )
            tab += len("q")
            screen.addstr(line + 5, tab, " for exit, press ")
            tab += len(" for exit, press ")
            screen.addstr(
                line + 5,
                tab,
                "any",
                curses.A_BOLD,
            )
            tab += len("any")
            screen.addstr(line + 5, tab, " other key to cancel")

            key = screen.getch()

            if key == ord("\n"):
                screen.clear()
                rectangle.clear()
                break
            elif key == ord("q"):
                break
        del editwin
        del rectangle
        del screen
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return text.strip().split(",")

    def _get_shop(self, name):
        return self.session.scalar(select(ShopModel).where(ShopModel.name == name))

    def _prompt_get_shop_name(self):
        line = 2

        tab = 6

        max_lines = 1
        max_cols = 60
        screen = curses.newwin(curses.LINES - 4, curses.COLS - 4, 2, 2)

        rectangle = screen.subwin(max_lines + 2, max_cols + 2, line + 1, tab)

        editwin = rectangle.subwin(max_lines + 1, max_cols, line + 2, tab + 1)

        while True:

            screen.clear()

            screen.addstr(0, tab - 2, "Shop name:")
            editwin.clear()
            rectangle.border()

            screen.refresh()
            rectangle.refresh()
            editwin.refresh()

            curses.curs_set(1)
            curses.echo()
            text = editwin.getstr(0, 0).decode("utf-8")
            curses.noecho()
            curses.curs_set(0)

            screen.addstr(line + 3, tab, f"confirm Shop name as {text}?")
            screen.addstr(line + 5, tab, "press ")
            tab += len("press ")
            screen.addstr(
                line + 5,
                tab,
                "ENTER",
                curses.A_BOLD,
            )
            tab += len("ENTER")
            screen.addstr(line + 5, tab, " to confirm, ")
            tab += len(" to confirm, ")
            screen.addstr(
                line + 5,
                tab,
                "q",
                curses.A_BOLD,
            )
            tab += len("q")
            screen.addstr(line + 5, tab, " for exit, press ")
            tab += len(" for exit, press ")
            screen.addstr(
                line + 5,
                tab,
                "any",
                curses.A_BOLD,
            )
            tab += len("any")
            screen.addstr(line + 5, tab, " other key to cancel")

            key = screen.getch()

            if key == ord("\n"):
                screen.clear()
                rectangle.clear()
                return text
            elif key == ord("q"):
                break
        del editwin
        del rectangle
        del screen
        self.main_screen.touchwin()
        self.main_screen.refresh()

    def get_shop_details(self):
        name = self._prompt_get_shop_name()
        return self._parse_shop(self._get_shop(name))

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
            ShopProductNameClassSchema(**name_class.__dict__, shop=shop)
            for name_class in shop.product_name_classes
        ]

    def _parse_product_price_classes(self, shop):
        return [
            ShopProductPriceClassSchema(**price_class.__dict__, shop=shop)
            for price_class in shop.product_price_classes
        ]

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

    def add_product_price_class(self, shop_id):
        class_names = self._prompt_price_class()
        shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))
        for class_name in class_names:
            shop_product_price_class = ShopProductPriceClassModel(
                class_name=class_name, shop=shop, shop_id=shop.id
            )
            self.session.add(shop_product_price_class)
        self.session.commit()

    def add_product_name_class(self, shop_id):
        class_prices = self._prompt_name_class()
        shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))
        for class_price in class_prices:
            shop_product_name_class = ShopProductNameClassModel(
                class_name=class_price, shop=shop, shop_id=shop.id
            )
            self.session.add(shop_product_name_class)
        self.session.commit()

    def search_shop(self):
        pass

    def display_shop(self, shop_id):
        from main import ItemDetails, WindowSettings

        shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))

        def refresh_product_price_classes():
            shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))
            return [
                (price_class.id, price_class.class_name)
                for price_class in shop.product_price_classes
            ]

        def refresh_product_name_classes():
            shop = self.session.scalar(select(ShopModel).where(ShopModel.id == shop_id))
            return [
                (name_class.id, name_class.class_name)
                for name_class in shop.product_name_classes
            ]

        items = [
            {
                "attribute": "name",
                "title": "Shop name:",
                "value": shop.name,
                "type": "STRING",
            },
            {
                "title": "Product name classes:",
                "type": "LIST",
                "value": {
                    "headers": ["ID", "CLASS NAME"],
                    "values": refresh_product_name_classes,
                },
                "function": self.display_all_product_name_classes,
                "add_function": self.add_product_name_class,
            },
            {
                "title": "Product price classes:",
                "type": "LIST",
                "value": {
                    "headers": ["ID", "CLASS NAME"],
                    "values": refresh_product_price_classes,
                },
                "function": self.display_all_product_price_classes,
                "add_function": self.add_product_price_class,
            },
        ]
        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )

        ItemDetails(items, settings, self.update_shop, self, shop_id).display()

    def display_all_shops(self):
        from main import Table, WindowSettings

        def refresh_shops():
            shops = self.get_all_shops()
            return [
                (
                    shop.id,
                    shop.name,
                )
                for shop in shops
            ]

        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )
        table = Table(
            refresh_shops, ["ID", "NAME"], self.display_shop, self.delete_shop, settings
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_all_product_price_classes(self, item_id):
        from main import Table, WindowSettings

        def refresh_price_classes():
            shop = self.session.scalar(select(ShopModel).where(ShopModel.id == item_id))
            return [
                (price.id, price.class_name) for price in shop.product_price_classes
            ]

        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )
        table = Table(
            refresh_price_classes,
            ["ID", "NAME"],
            self.display_product_price_class,
            self.delete_product_price_class,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_product_price_class(self, item_id):
        from main import ItemDetails, WindowSettings

        price_class = self.session.scalar(
            select(ShopProductPriceClassModel).where(
                ShopProductPriceClassModel.id == item_id
            )
        )

        items = [
            {
                "attribute": "class_name",
                "title": "Product price class name:",
                "value": price_class.class_name,
                "type": "STRING",
            },
        ]
        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )

        ItemDetails(items, settings, self.update_name_class, self, item_id).display()

    def display_all_product_name_classes(self, item_id):
        from main import Table, WindowSettings

        def refresh_price_classes():
            shop = self.session.scalar(select(ShopModel).where(ShopModel.id == item_id))
            return [(name.id, name.class_name) for name in shop.product_name_classes]

        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )
        table = Table(
            refresh_price_classes,
            ["ID", "NAME"],
            self.display_product_name_class,
            self.delete_product_name_class,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_product_name_class(self, item_id):
        from main import ItemDetails, WindowSettings

        name_class = self.session.scalar(
            select(ShopProductNameClassModel).where(
                ShopProductNameClassModel.id == item_id
            )
        )

        items = [
            {
                "attribute": "class_name",
                "title": "Product price class name:",
                "value": name_class.class_name,
                "type": "STRING",
            },
        ]
        settings = WindowSettings(
            nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2
        )

        ItemDetails(items, settings, self.update_price_class, self, item_id).display()
