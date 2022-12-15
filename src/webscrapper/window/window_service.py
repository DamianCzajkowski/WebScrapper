from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from webscrapper.database.service import ProductService, ShopService
from webscrapper.window.dialogs import AddProductDialog, AddShopDialog, EditProductDialog, EditShopDialog
from webscrapper.window.views import ProductHistoryView, TableView


class ShopDisplayService(QWidget):
    def __init__(self, view, session):
        super().__init__()
        self._view = view
        self.service = ShopService(session)
        self.table = None

        self.setupUI()

    def setupUI(self):
        self.mainLayout = QVBoxLayout()
        table = self._create_table()
        crudButtons = self._createCrudButtons()
        self.query = QLineEdit()
        self.query.setPlaceholderText("Search...")
        self.query.textChanged.connect(self.search)

        self.mainLayout.addWidget(self.query)
        self.mainLayout.addWidget(table)
        self.mainLayout.addWidget(crudButtons)

        self.setLayout(self.mainLayout)

    def search(self, s):
        # clear current selection.
        self.table.setCurrentItem(None)

        if not s:
            # Empty string, don't search.
            return

        matching_items = self.table.findItems(s, Qt.MatchFlag.MatchContains)
        # breakpoint()
        if matching_items:

            # we have found something
            item = matching_items[0]  # take the first
            self.table.setCurrentItem(item)

    def _createCrudButtons(self):
        widget = QWidget()
        layout = QHBoxLayout()

        btnList = ["Add", "Edit", "Delete"]

        for name in btnList:
            btn = QPushButton(name)
            btn.clicked.connect(getattr(self, f"display{name}View"))
            layout.addWidget(btn)

        widget.setLayout(layout)

        return widget

    def displayAddView(self):
        dialog = AddShopDialog(self)
        if dialog.exec():
            shop_id = self.service.create_shop(
                shop_name=dialog.data["shop_name"],
                price_classes=[dialog.data["price_classes"]],
                name_classes=[dialog.data["name_classes"]],
            )
            shop = self.service.get_shop_by_id(shop_id)
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            self.table.setItem(rowPosition, 0, QTableWidgetItem(str(shop_id)))
            self.table.setItem(rowPosition, 1, QTableWidgetItem(shop.name))
            self.table.setItem(rowPosition, 2, QTableWidgetItem(shop.product_name_classes[0].class_name))
            self.table.setItem(rowPosition, 3, QTableWidgetItem(shop.product_price_classes[0].class_name))

    def displayEditView(self):
        row = self.table.currentIndex().row()
        if row < 0:
            return
        itemId = self.table.item(row, 0).text()

        shop = self.service.get_shop_by_id(itemId)
        dialog = EditShopDialog(shop, self)
        if dialog.exec():
            self.service.update_shop(itemId, {"name": dialog.data["name"]})
            self.service.update_name_class(shop.product_name_classes[0].id, {"class_name": dialog.data["name_classes"]})
            self.service.update_price_class(
                shop.product_price_classes[0].id, {"class_name": dialog.data["price_classes"]}
            )
            shop = self.service.get_shop_by_id(itemId)
            self.table.item(row, 1).setText(shop.name)
            self.table.item(row, 2).setText(shop.product_name_classes[0].class_name)
            self.table.item(row, 3).setText(shop.product_price_classes[0].class_name)

    def displayDeleteView(self):
        row = self.table.currentIndex().row()
        if row < 0:
            return

        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want to remove the selected shop?",
        )
        if messageBox:
            self.service.delete_shop(self.table.takeItem(row, 0).text())
            self.table.removeRow(row)

    def _create_table(self):
        shops = self.service.get_all_shops()
        data = {"id": [], "name": [], "name_classes": [], "price_classes": []}
        for shop in shops:
            data["id"].append(str(shop.id))
            data["name"].append(shop.name)
            data["name_classes"].append(shop.product_name_classes[0].class_name)
            data["price_classes"].append(shop.product_price_classes[0].class_name)
        self.table = TableView(data, len(data["id"]), 4)
        self.table.setData()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        return self.table


class ProductDisplayService(QWidget):
    def __init__(self, view, session):
        super().__init__()
        self._view = view
        self.service = ProductService(session)
        self.shop_service = ShopService(session)
        self.table = None

        self.setupUI()

    def setupUI(self):
        self.mainLayout = QVBoxLayout()
        table = self._create_table()
        crudButtons = self._createCrudButtons()
        self.query = QLineEdit()
        self.query.setPlaceholderText("Search...")
        self.query.textChanged.connect(self.search)

        self.mainLayout.addWidget(self.query)
        self.mainLayout.addWidget(table)
        self.mainLayout.addWidget(crudButtons)

        self.setLayout(self.mainLayout)

    def search(self, s):
        # clear current selection.
        self.table.setCurrentItem(None)

        if not s:
            # Empty string, don't search.
            return

        matching_items = self.table.findItems(s, Qt.MatchFlag.MatchContains)
        # breakpoint()
        if matching_items:

            # we have found something
            item = matching_items[0]  # take the first
            self.table.setCurrentItem(item)

    def _createCrudButtons(self):
        widget = QWidget()
        layout = QHBoxLayout()

        btnList = ["Add", "Edit", "Delete", "Refresh", "History"]

        for name in btnList:
            btn = QPushButton(name)
            btn.clicked.connect(getattr(self, f"display{name}View"))
            layout.addWidget(btn)

        widget.setLayout(layout)

        return widget

    def displayAddView(self):
        shops = self.shop_service.get_all_shops()
        shops_name = [shop.name for shop in shops]
        dialog = AddProductDialog(shops_name, self)
        if dialog.exec():
            product_id = self.service.create_product(shop_name=dialog.data["shop"], url=dialog.data["url"])
            product = self.service.get_product_by_id(product_id)
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            self.table.setItem(rowPosition, 0, QTableWidgetItem(str(product_id)))
            self.table.setItem(rowPosition, 1, QTableWidgetItem(product.name))
            self.table.setItem(rowPosition, 2, QTableWidgetItem(product.url))
            self.table.setItem(rowPosition, 3, QTableWidgetItem(str(product.price)))

    def displayEditView(self):
        row = self.table.currentIndex().row()
        if row < 0:
            return
        itemId = self.table.item(row, 0).text()

        product = self.service.get_product_by_id(itemId)
        dialog = EditProductDialog(product, self)
        if dialog.exec():
            self.service.update_product(product.id, {"url": dialog.data["url"]})
            product = self.service.get_product_by_id(itemId)
            self.table.item(row, 1).setText(product.name)
            self.table.item(row, 2).setText(product.url)
            self.table.item(row, 3).setText(str(product.price))

    def displayDeleteView(self):
        row = self.table.currentIndex().row()
        if row < 0:
            return

        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want to remove the selected product?",
        )
        if messageBox:
            self.service.delete_product(self.table.takeItem(row, 0).text())
            self.table.removeRow(row)

    def displayRefreshView(self):
        row = self.table.currentIndex().row()
        if row < 0:
            return

        itemId = self.table.item(row, 0).text()

        messageBox = QMessageBox.warning(
            self,
            "Warning!",
            "Do you want to refresh the selected product?",
        )
        if messageBox:
            self.service.refresh_product(itemId)

            product = self.service.get_product_by_id(itemId)
            self.table.item(row, 1).setText(product.name)
            self.table.item(row, 2).setText(product.url)
            self.table.item(row, 3).setText(str(product.price))

    def displayHistoryView(self, checked):
        row = self.table.currentIndex().row()
        if row < 0:
            return

        itemId = self.table.item(row, 0).text()
        product = self.service.get_product_by_id(itemId)

        self.historyView = ProductHistoryView(product)
        self.historyView.show()

    def _create_table(self):
        products = self.service.get_all_products()
        data = {"id": [], "name": [], "url": [], "price": []}
        for product in products:
            data["id"].append(str(product.id))
            data["name"].append(product.name)
            data["url"].append(product.url)
            data["price"].append(str(product.price))

        self.table = TableView(data, len(data["id"]), 4)
        self.table.setData()

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        return self.table
