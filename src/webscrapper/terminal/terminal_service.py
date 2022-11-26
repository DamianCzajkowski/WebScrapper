import curses

from webscrapper.database.service import ProductService, ShopService


class AbstractTerminalService:
    def __init__(self, session, main_screen):
        self.session = session
        self.main_screen = main_screen


class TerminalProductService(AbstractTerminalService):
    def __init__(self, session, main_screen):
        super().__init__(session, main_screen)
        self.service = ProductService(session)

    def create_product(self):
        url = self._prompt_product_url()
        if not url:
            return
        shop_name = self._prompt_shop_name()
        if not shop_name:
            return

        self.service.create_product(shop_name, url)

        self.main_screen.touchwin()
        self.main_screen.refresh()

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

    def display_product(self):
        pass

    def display_all_products(self):
        from webscrapper.terminal.main import Table, WindowSettings

        def refresh_product():
            products = self.service.get_all_products()
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

        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)
        table = Table(
            refresh_product,
            ["ID", "URL", "PRICE", "NAME", "SHOP_ID"],
            self.display_product,
            self.service.delete_product,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return


class TerminalShopService(AbstractTerminalService):
    def __init__(self, session, main_screen):
        super().__init__(session, main_screen)
        self.service = ShopService(session)

    def create_shop(self):
        from webscrapper.terminal.main import YesNoChoice

        name = self._prompt_get_shop_name()
        if not name:
            return

        price_classes_choice = YesNoChoice("Do you want to add Product price classes?", self.main_screen).display()
        price_classes = self._prompt_price_class() if price_classes_choice else []

        name_classes_choice = YesNoChoice("Do you want to add Product name classes?", self.main_screen).display()
        name_classes = self._prompt_name_class() if name_classes_choice else []

        self.service.create_shop(name, price_classes, name_classes)

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

    def add_product_price_class(self, shop_id):
        class_names = self._prompt_price_class()
        shop = self.service.get_shop_by_id(shop_id)
        for class_price in class_names:
            shop_product_price_class = self.service.parse_product_price_class(class_price, shop)
            self.session.add(shop_product_price_class)
        self.session.commit()

    def add_product_name_class(self, shop_id):
        class_prices = self._prompt_name_class()
        shop = self.service.get_shop_by_id(shop_id)
        for class_name in class_prices:
            shop_product_name_class = self.service.parse_product_name_class(class_name, shop)
            self.session.add(shop_product_name_class)
        self.session.commit()

    def display_shop(self, shop_id):
        from webscrapper.terminal.main import ItemDetails, WindowSettings

        shop = self.service.get_shop_by_id(shop_id)

        def refresh_product_price_classes():
            shop = self.service.get_shop_by_id(shop_id)
            return [(price_class.id, price_class.class_name) for price_class in shop.product_price_classes]

        def refresh_product_name_classes():
            shop = self.service.get_shop_by_id(shop_id)
            return [(name_class.id, name_class.class_name) for name_class in shop.product_name_classes]

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
        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)

        ItemDetails(items, settings, self.service.update_shop, self, shop_id).display()

    def display_all_shops(self):
        from webscrapper.terminal.main import Table, WindowSettings

        def refresh_shops():
            shops = self.service.get_all_shops()
            return [
                (
                    shop.id,
                    shop.name,
                )
                for shop in shops
            ]

        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)
        table = Table(refresh_shops, ["ID", "NAME"], self.display_shop, self.service.delete_shop, settings)
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_all_product_price_classes(self, item_id):
        from webscrapper.terminal.main import Table, WindowSettings

        def refresh_price_classes():
            shop = self.service.get_shop_by_id(item_id)
            return [(price.id, price.class_name) for price in shop.product_price_classes]

        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)
        table = Table(
            refresh_price_classes,
            ["ID", "NAME"],
            self.display_product_price_class,
            self.service.delete_product_price_class,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_product_price_class(self, item_id):
        from webscrapper.terminal.main import ItemDetails, WindowSettings

        price_class = self.service.get_product_price_class_by_id(item_id)

        items = [
            {
                "attribute": "class_name",
                "title": "Product price class name:",
                "value": price_class.class_name,
                "type": "STRING",
            },
        ]
        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)

        ItemDetails(items, settings, self.service.update_name_class, self, item_id).display()

    def display_all_product_name_classes(self, item_id):
        from webscrapper.terminal.main import Table, WindowSettings

        def refresh_name_classes():
            shop = self.service.get_shop_by_id(item_id)
            return [(name.id, name.class_name) for name in shop.product_name_classes]

        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)
        table = Table(
            refresh_name_classes,
            ["ID", "NAME"],
            self.display_product_name_class,
            self.service.delete_product_name_class,
            settings,
        )
        table.display()
        self.main_screen.touchwin()
        self.main_screen.refresh()
        return

    def display_product_name_class(self, item_id):
        from webscrapper.terminal.main import ItemDetails, WindowSettings

        name_class = self.service.get_product_name_class_by_id(item_id)

        items = [
            {
                "attribute": "class_name",
                "title": "Product price class name:",
                "value": name_class.class_name,
                "type": "STRING",
            },
        ]
        settings = WindowSettings(nlines=curses.LINES - 4, ncols=curses.COLS - 4, beginx=2, beginy=2)

        ItemDetails(items, settings, self.service.update_price_class, self, item_id).display()
