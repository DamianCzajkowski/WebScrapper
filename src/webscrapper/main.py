import curses
from curses import panel
from database import initialize_database
from service import ProductService, ShopService
from pydantic import BaseModel
from typing import Callable


class Menu:
    def __init__(self, items):
        self.window = curses.newwin(7, 20, 2, curses.COLS // 2 - 10)
        self.window.keypad(True)
        self.window.bkgd(curses.color_pair(1))
        self.window.refresh()

        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

        self.position = 0
        self.items = items
        self.items.append(("exit", "exit"))

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display(self, *args, **kwargs):
        self.panel.top()
        self.panel.show()
        self.window.clear()

        while True:
            self.window.border()
            self.window.refresh()
            curses.doupdate()

            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                    self.window.addstr(index + 1, 1, "-> ")
                else:
                    mode = curses.A_NORMAL
                    self.window.addstr(index + 1, 1, "  ")

                self.window.addstr(index + 1, 4, item[0], mode)

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord("\n")]:
                if self.position == len(self.items) - 1:
                    break
                self.items[self.position][1]()
                self.window.touchwin()

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()


class WindowSettings(BaseModel):
    nlines: int
    ncols: int
    beginx: int
    beginy: int


class Table:
    def __init__(
        self,
        get_items,
        headers: list,
        edit_function: Callable,
        delete_function: Callable,
        settings: WindowSettings,
    ):
        self.window = curses.newwin(
            settings.nlines, settings.ncols, settings.beginy, settings.beginx
        )
        self.window.keypad(True)
        self.window.refresh()

        self.max_cols = settings.ncols
        self.max_lines = settings.beginy + settings.nlines
        self.begin_y = settings.beginy
        self.begin_x = settings.beginx

        self.settings = settings

        self.row_height = 3
        self.header_height = 0

        if isinstance(get_items, Callable):
            self.items = get_items()
        else:
            self.items = get_items
        self.get_items = get_items
        self.headers = headers
        len_headers = len(headers)
        for i in range(1, len_headers + len_headers - 1, 2):
            self.headers.insert(i, "|")
        self.edit_function = edit_function
        self.delete_function = delete_function

        self.position = 0
        self.refresh_pad = 0
        self.max_y, self.max_x = self.window.getmaxyx()
        self.refresh_pad_stop = (self.max_y - 2) // 4
        self.max_items = (self.max_y - 2) // 2

    def navigate(self, n):
        self.position += n
        if n < 0:
            self.position_check = self.position - n
        else:
            self.position_check = self.position
        if self.position_check >= self.refresh_pad_stop:
            if (len(self.items) - self.position_check - 1) >= (
                self.max_items - self.refresh_pad_stop
            ):
                self.refresh_pad += n * 2
        if self.position < 0:
            self.position = 0
            self.refresh_pad = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1
            self.refresh_pad = (len(self.items) - self.max_items) * 2

    def show(self):
        self.items = (
            self.get_items() if isinstance(self.get_items, Callable) else self.get_items
        )
        pad = curses.newpad(
            self.row_height * (len(self.items) or 1),
            self.max_cols,
        )

        splitted_x = self.max_x / (len(self.headers) + 1)
        for idx, header in enumerate(self.headers):
            self.window.addstr(
                self.header_height,
                round(splitted_x * (idx + 1)) - len(header) // 2 - 1,
                header,
                curses.A_BOLD,
            )
        splitted_y = 1
        for item in self.items:
            for idx, value in enumerate(item):
                pad.addstr(
                    splitted_y,
                    round(splitted_x + splitted_x * idx * 2) - len(str(value)) // 2 - 1,
                    str(value),
                )
            splitted_y += 2

        pad.refresh(
            self.refresh_pad,
            0,
            self.begin_y + 1,
            self.begin_x,
            self.max_lines,
            self.max_cols + 1,
        )
        self.window.refresh()

    def context_menu(self, selected_item):
        new_pad = curses.newpad(5, 45)
        new_pad.border()
        new_pad.addstr(1, 4, "What do you want to do with this item?")
        self.edit_position = 0

        def navigate(n):
            self.edit_position += n
            if self.edit_position < 0:
                self.edit_position = 0
            elif self.edit_position >= 3:
                self.edit_position = 2

        while True:
            for index, item in enumerate([("Cancel", 4), ("Edit", 20), ("Delete", 33)]):
                if index == self.edit_position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                new_pad.addstr(3, item[1], item[0], mode)
            new_pad.bkgd(curses.color_pair(2))
            new_pad.refresh(
                0,
                0,
                curses.LINES // 2 - 5,
                curses.COLS // 2 - 22,
                curses.LINES // 2 + 5,
                curses.COLS // 2 + 40,
            )
            self.window.refresh()
            new_key = self.window.getch()
            if new_key in [curses.KEY_ENTER, ord("\n")]:
                if self.edit_position == 0:
                    break
                elif self.edit_position == 1:
                    self.edit_function(selected_item[0])
                    self.window.touchwin()
                    break
                elif self.edit_position == 2:
                    self.delete_function(selected_item[0])
                    self.window.touchwin()
                    break
            elif new_key == curses.KEY_RIGHT:
                navigate(1)
            elif new_key == curses.KEY_LEFT:
                navigate(-1)
            elif new_key == ord("q"):
                break
        del new_pad
        self.window.touchwin()
        self.window.refresh()

    def display(self, *args, **kwargs):
        self.window.clear()
        self.window.touchwin()

        while True:
            pad = curses.newpad(
                self.row_height * (len(self.items) or 1),
                self.max_cols,
            )
            self.window.refresh()

            splitted_x = self.max_x / (len(self.headers) + 1)
            for idx, header in enumerate(self.headers):
                self.window.addstr(
                    self.header_height,
                    round(splitted_x * (idx + 1)) - len(header) // 2 - 1,
                    header,
                    curses.A_BOLD,
                )
            splitted_y = 1
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                    pad.addstr(splitted_y, 1, "-> ")
                else:
                    mode = curses.A_NORMAL
                    pad.addstr(splitted_y, 1, "   ")
                for idx, value in enumerate(item):
                    pad.addstr(
                        splitted_y,
                        round(splitted_x + splitted_x * idx * 2)
                        - len(str(value)) // 2
                        - 1,
                        str(value),
                        mode,
                    )
                splitted_y += 2

            pad.refresh(
                self.refresh_pad,
                0,
                self.begin_y + 1,
                self.begin_x,
                self.max_lines,
                self.max_cols + 1,
            )

            self.window.refresh()

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord("\n")]:
                self.context_menu(self.items[self.position])
                self.items = (
                    self.get_items()
                    if isinstance(self.get_items, Callable)
                    else self.get_items
                )

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)
            elif key == ord("q"):
                break
            del pad
        self.window.clear()


class ItemDetails:
    def __init__(
        self, items: list, settings: WindowSettings, update_function, service, item_id
    ):
        self.window = curses.newwin(
            settings.nlines, settings.ncols, settings.beginy, settings.beginx
        )
        self.window.keypad(True)
        self.window.refresh()
        self.window_settings = settings

        self.max_cols = settings.ncols
        self.max_lines = settings.beginy + settings.nlines
        self.begin_y = settings.beginy
        self.begin_x = settings.beginx

        self.row_height = 3
        self.header_height = 0

        self.service = service
        self.update_function = update_function
        self.item_id = item_id

        self.items = items

        self.position = 0
        self.refresh_pad = 0
        self.max_y, self.max_x = self.window.getmaxyx()
        self.refresh_pad_stop = (self.max_y - 2) // 4
        self.max_items = (self.max_y - 2) // 2

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
            self.refresh_pad = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def display_string(self, value: str, settings: WindowSettings):
        name_window = curses.newwin(
            settings.nlines, settings.ncols, settings.beginy, settings.beginx
        )
        edit_name_window = name_window.subwin(
            settings.nlines, settings.ncols, settings.beginy, settings.beginx
        )

        name_window.clear()
        name_window.border()
        name_window.refresh()

        edit_name_window.addstr(1, 1, value)
        edit_name_window.refresh()
        return edit_name_window

    def edit_text(self, item):
        curses.curs_set(1)
        curses.echo()
        window = item["edit_window"]
        window.addstr(1, 1, " " * 30)
        text = window.getstr(1, 1).decode("utf-8")
        self.update_function(self.item_id, {item["attribute"]: text})
        item["value"] = text
        curses.noecho()
        curses.curs_set(0)

    def display(self, *args, **kwargs):
        self.window.clear()
        self.window.touchwin()

        while True:
            self.window.refresh()
            start_y = 1
            for index, item in enumerate(self.items):
                if index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                match item["type"]:
                    case "STRING":
                        self.window.addstr(start_y, 1, item["title"], mode)
                        start_y += 3
                        settings = WindowSettings(
                            nlines=3, ncols=60, beginx=2, beginy=start_y
                        )
                        item["edit_window"] = self.display_string(
                            item["value"], settings
                        )
                        start_y += 1
                    case "LIST":
                        self.window.addstr(start_y, 1, item["title"], mode)
                        start_y += 3
                        settings = WindowSettings(
                            nlines=3, ncols=60, beginx=2, beginy=start_y
                        )
                        if item["value"]["values"]:
                            if not item.get("table"):
                                item["table"] = Table(
                                    item["value"]["values"](),
                                    item["value"]["headers"],
                                    exit,
                                    exit,
                                    settings,
                                )
                            item["table"].get_items = item["value"]["values"]()
                            item["table"].show()
                            start_y += 3

            self.window.refresh()

            key = self.window.getch()
            if key in [curses.KEY_ENTER, ord("\n")]:
                if self.items[self.position]["type"] == "STRING":
                    self.edit_text(self.items[self.position])
                elif self.items[self.position]["type"] == "LIST":
                    ch = YesNoChoice(
                        f"What you want to do with {item['title']}",
                        self.service.main_screen,
                        ["Edit", "Add new"],
                    ).display()
                    if ch:
                        self.items[self.position]["function"](self.item_id)
                    else:
                        self.items[self.position]["add_function"](self.item_id)
                self.window.touchwin()
                self.window.refresh()

            if key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)
            if key == ord("q"):
                break
        self.window.clear()


class YesNoChoice:
    def __init__(self, text: str, window, custom_choices=["Yes", "No"]):
        self.text = text
        self.window = window
        self.custom_choices = custom_choices

    def display(self):
        new_pad = curses.newpad(5, 55)
        new_pad.border()
        new_pad.addstr(1, 4, self.text)
        self.edit_position = 0
        self.window.refresh()

        def navigate(n):
            self.edit_position += n
            if self.edit_position < 0:
                self.edit_position = 0
            elif self.edit_position >= 2:
                self.edit_position = 2

        while True:
            for index, item in enumerate(
                [
                    (self.custom_choices[0], 50 // 4 - 1),
                    (self.custom_choices[1], (50 // 4) * 3 - 1),
                ]
            ):
                if index == self.edit_position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                new_pad.addstr(3, item[1], item[0], mode)
            new_pad.refresh(
                0,
                0,
                curses.LINES // 2 - 5,
                curses.COLS // 2 - 25,
                curses.LINES // 2 + 5,
                curses.COLS // 2 + 40,
            )
            self.window.refresh()
            new_key = self.window.getch()
            if new_key in [curses.KEY_ENTER, ord("\n")]:
                if self.edit_position == 0:
                    self.window.touchwin()
                    del new_pad
                    return True
                elif self.edit_position == 1:
                    self.window.touchwin()
                    del new_pad
                    return False
            elif new_key == curses.KEY_RIGHT:
                navigate(1)
            elif new_key == curses.KEY_LEFT:
                navigate(-1)


TITLE = "WEBSCRAPPER"


class MyApp:
    def __init__(self, stdscreen):
        self.session = initialize_database()
        self.screen = stdscreen

        self.shop_service = ShopService(self.session, self.screen)
        self.product_service = ProductService(self.session, self.screen)

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_YELLOW)

        WHITE_AND_BLUE = curses.color_pair(2)
        self.screen.bkgd(WHITE_AND_BLUE)
        curses.curs_set(0)

        self.screen.addstr(1, curses.COLS // 2 - len(TITLE) // 2, TITLE, curses.A_BOLD)
        self.screen.refresh()

        shop_submenu_items = [
            ("Add shop", self.shop_service.create_shop),
            ("List shops", self.shop_service.display_all_shops),
        ]
        shop_submenu = Menu(shop_submenu_items)

        product_submenu_items = [
            ("Add product", self.product_service.create_product),
            ("List products", self.product_service.display_all_products),
        ]
        product_submenu = Menu(product_submenu_items)

        main_menu_items = [
            ("Product", product_submenu.display, ""),
            ("Shops", shop_submenu.display, ""),
            ("Settings", "", ""),
            ("Help", "", ""),
        ]
        main_menu = Menu(main_menu_items)
        main_menu.display()
        self.screen.touchwin()
        self.screen.refresh()


if __name__ == "__main__":
    curses.wrapper(MyApp)
