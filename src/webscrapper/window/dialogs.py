from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout


class CustomDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.dialogLayout = QVBoxLayout()
        self.setLayout(self.dialogLayout)
        self.data = None

        self.setupUI()

    def setupUI(self):
        raise NotImplementedError()

    def accept(self):
        super().accept()


class AddShopDialog(CustomDialog):
    def __init__(self, parent=None):
        super().__init__("Add shop", parent)

    def setupUI(self):
        """Setup the Add Contact dialog's GUI."""
        # Create line edits for data fields
        self.nameField = QLineEdit()
        self.nameField.setObjectName("Shop name")
        self.nameClass = QLineEdit()
        self.nameClass.setObjectName("Name classes")
        self.priceClass = QLineEdit()
        self.priceClass.setObjectName("Price classes")

        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Name:", self.nameField)
        layout.addRow("Price class:", self.priceClass)
        layout.addRow("Name class:", self.nameClass)

        self.dialogLayout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.dialogLayout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = {}
        for field in (self.nameField, self.nameClass, self.priceClass):
            if not field.text():
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"You must provide a shop's {field.objectName()}",
                )
                self.data = None  # Reset .data
                return

            self.data[field.objectName().lower().replace(" ", "_")] = field.text()

        if not self.data:
            return

        super().accept()


class EditShopDialog(CustomDialog):
    def __init__(self, shop, parent=None):
        self.shop = shop
        super().__init__("Edit shop", parent)

    def setupUI(self):
        # Create line edits for data fields
        self.nameField = QLineEdit()
        self.nameField.setObjectName("Name")
        self.nameField.setText(self.shop.name)
        self.nameClass = QLineEdit()
        self.nameClass.setObjectName("Name classes")
        self.nameClass.setText(self.shop.product_name_classes[0].class_name)
        self.priceClass = QLineEdit()
        self.priceClass.setObjectName("Price classes")
        self.priceClass.setText(self.shop.product_price_classes[0].class_name)

        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Name:", self.nameField)
        layout.addRow("Price class:", self.priceClass)
        layout.addRow("Name class:", self.nameClass)

        self.dialogLayout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.dialogLayout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = {}
        for field in (self.nameField, self.nameClass, self.priceClass):
            if not field.text():
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"You must provide a shop's {field.objectName()}",
                )
                self.data = None  # Reset .data
                return

            self.data[field.objectName().lower().replace(" ", "_")] = field.text()

        if not self.data:
            return

        super().accept()


class AddProductDialog(CustomDialog):
    def __init__(self, shops, parent=None):
        self.shops = shops
        super().__init__("Add product", parent)

    def setupUI(self):
        # Create line edits for data fields
        self.urlField = QLineEdit()
        self.urlField.setObjectName("Url")
        self.shopField = QComboBox()
        self.shopField.setObjectName("Shop")
        self.shopField.addItems(self.shops)

        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Product url:", self.urlField)
        layout.addRow("Shop:", self.shopField)

        self.dialogLayout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.dialogLayout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = {}
        if not self.urlField.text():
            QMessageBox.critical(
                self,
                "Error!",
                f"You must provide a product's {self.urlField.objectName()}",
            )
            self.data = None  # Reset .data
            return

        self.data[self.urlField.objectName().lower().replace(" ", "_")] = self.urlField.text()

        if not self.shopField.currentText():
            QMessageBox.critical(
                self,
                "Error!",
                f"You must provide a product's {self.shopField.objectName()}",
            )
            self.data = None  # Reset .data
            return

        self.data[self.shopField.objectName().lower().replace(" ", "_")] = self.shopField.currentText()

        if not self.data:
            return

        super().accept()


class EditProductDialog(CustomDialog):
    def __init__(self, product, parent=None):
        self.product = product
        super().__init__("Edit product", parent)

    def setupUI(self):
        """Setup the Add Contact dialog's GUI."""
        # Create line edits for data fields
        self.urlField = QLineEdit()
        self.urlField.setObjectName("Url")
        self.urlField.setText(self.product.url)

        # Lay out the data fields
        layout = QFormLayout()
        layout.addRow("Product url:", self.urlField)

        self.dialogLayout.addLayout(layout)
        # Add standard buttons to the dialog and connect them
        self.buttonsBox = QDialogButtonBox(self)
        self.buttonsBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonsBox.accepted.connect(self.accept)
        self.buttonsBox.rejected.connect(self.reject)
        self.dialogLayout.addWidget(self.buttonsBox)

    def accept(self):
        """Accept the data provided through the dialog."""
        self.data = {}
        for field in (self.urlField,):
            if not field.text():
                QMessageBox.critical(
                    self,
                    "Error!",
                    f"You must provide a shop's {field.objectName()}",
                )
                self.data = None  # Reset .data
                return

            self.data[field.objectName().lower().replace(" ", "_")] = field.text()

        if not self.data:
            return

        super().accept()
