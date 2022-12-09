"""PyCalc is a simple calculator built with Python and PyQt."""

import sys
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QDockWidget,
)
from webscrapper.database.database import initialize_database
from webscrapper.database.service import ShopService, ProductService
from webscrapper.terminal.main import Table, WindowSettings


class Window(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setFixedSize(1000, 255)
        self.setWindowTitle("WebScrapper")
        self.generalLayout = QGridLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createButtons()
        self._createMainPanel()

    def _createButtons(self):
        self.buttonMap = {}
        buttonsLayout = QVBoxLayout()
        keyBoard = ["Products", "Shops", "Settings", "Help", "Exit"]

        for value in keyBoard:
            button = QPushButton(value)
            button.clicked.connect(getattr(self, f"display{value}"))
            self.buttonMap[value] = button
            buttonsLayout.addWidget(self.buttonMap[value], 0)

        self.generalLayout.addLayout(buttonsLayout, 0, 0)

    def _createMainPanel(self):
        self.mainPanelLayout = QGridLayout()

        self.generalLayout.addLayout(self.mainPanelLayout, 0, 1)

    def displayShops(self):
        self.clearLayout()
        shops = ShopDisplayService(view=self, session=self.session)
        table = shops._create_table()
        self.mainPanelLayout.addWidget(table)
        shops._creation_form()

    def displayProducts(self):
        self.clearLayout()
        shops = ProductDisplayService(view=self, session=self.session)
        table = shops._create_table()
        self.mainPanelLayout.addWidget(table)

    def displaySettings(self):
        self.clearLayout()
        pass

    def displayHelp(self):
        self.clearLayout()
        pass

    def displayExit(self):
        self.clearLayout()
        self.close()

    def clearLayout(self):
        for i in reversed(range(self.mainPanelLayout.count())):
            self.mainPanelLayout.itemAt(i).widget().deleteLater()


class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def setData(self):
        horHeaders = []
        for n, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                newitem.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(m, n, newitem)

        self.setHorizontalHeaderLabels(horHeaders)

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable


class ShopDisplayService:
    def __init__(self, view, session):
        self._view = view
        self.service = ShopService(session)

    # def _slotDoubleClicked(self, *args, **kwargs):
    #     breakpoint()

    def _buildExpression(self, subExpression):
        pass

    def _connectSignalsAndSlots(self):
        pass
        # for keySymbol, button in self._view.buttonMap.items():
        #     if keySymbol not in {"=", "C"}:
        #         button.clicked.connect(partial(self._buildExpression, keySymbol))
        # self._view.buttonMap["="].clicked.connect(self._calculateResult)
        # self._view.display.returnPressed.connect(self._calculateResult)
        # self._view.buttonMap["C"].clicked.connect(self._view.clearDisplay)

    def _creation_form(self):
        dock = QDockWidget("New Shop")
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self._view.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        form = QWidget()
        layout = QFormLayout(form)
        form.setLayout(layout)

        self.shop_name = QLineEdit(form)

        layout.addRow("Shop Name:", self.shop_name)

        btn_add = QPushButton("Add")
        # btn_add.clicked.connect(self.add_employee)
        layout.addRow(btn_add)

        dock.setWidget(form)

    def _create_table(self):
        shops = self.service.get_all_shops()
        data = {"id": [], "name": []}
        for shop in shops:
            data["id"].append(str(shop.id))
            data["name"].append(shop.name)
        # breakpoint()
        table = TableView(data, len(data["id"]), 2)
        table.setData()
        # table.doubleClicked.connect(self._slotDoubleClicked)
        return table


class ProductDisplayService:
    def __init__(self, view, session):
        self._view = view
        self.service = ProductService(session)

    # def _slotDoubleClicked(self, *args, **kwargs):
    #     breakpoint()

    def _buildExpression(self, subExpression):
        pass

    def _connectSignalsAndSlots(self):
        pass
        # for keySymbol, button in self._view.buttonMap.items():
        #     if keySymbol not in {"=", "C"}:
        #         button.clicked.connect(partial(self._buildExpression, keySymbol))
        # self._view.buttonMap["="].clicked.connect(self._calculateResult)
        # self._view.display.returnPressed.connect(self._calculateResult)
        # self._view.buttonMap["C"].clicked.connect(self._view.clearDisplay)

    def _create_table(self):
        products = self.service.get_all_products()
        data = {"id": [], "name": [], "url": [], "price": []}
        for product in products:
            data["id"].append(str(product.id))
            data["name"].append(product.name)
            data["url"].append(product.url)
            data["price"].append(str(product.price))

        # breakpoint()
        table = TableView(data, len(data["id"]), 4)
        table.setData()
        # table.doubleClicked.connect(self._slotDoubleClicked)
        return table


def main():
    """PyCalc's main function."""
    session = initialize_database()
    pycalcApp = QApplication([])
    window = Window(session)
    window.show()
    sys.exit(pycalcApp.exec())


if __name__ == "__main__":
    main()
