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
)
from webscrapper.database.database import initialize_database
from webscrapper.database.service import ShopService
from webscrapper.terminal.main import Table, WindowSettings


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 255)
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
            self.buttonMap[value] = QPushButton(value)
            buttonsLayout.addWidget(self.buttonMap[value], 0)

        self.generalLayout.addLayout(buttonsLayout, 0, 0)

    def _createMainPanel(self):
        self.mainPanelLayout = QGridLayout()

        self.generalLayout.addLayout(self.mainPanelLayout, 0, 1)

    def displayTable(self, table):
        self.mainPanelLayout.addWidget(table)


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
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


class PyCalc:
    """PyCalc's controller class."""

    def __init__(self, view, session):
        self._view = view
        self.service = ShopService(session)

    def _slotDoubleClicked(self, *args, **kwargs):
        breakpoint()

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

    def _display_shops(self):
        shops = self.service.get_all_shops()
        data = {"id": [], "name": []}
        for shop in shops:
            data["id"].append(str(shop.id))
            data["name"].append(shop.name)
        # breakpoint()
        table = TableView(data, len(data["id"]), 2)
        table.setData()
        table.doubleClicked.connect(self._slotDoubleClicked)
        self._view.displayTable(table)


def main():
    """PyCalc's main function."""
    session = initialize_database()
    pycalcApp = QApplication([])
    window = Window()
    window.show()
    aa = PyCalc(view=window, session=session)
    aa._display_shops()
    sys.exit(pycalcApp.exec())


if __name__ == "__main__":
    main()
