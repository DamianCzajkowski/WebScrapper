import matplotlib
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


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
                newitem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.setItem(m, n, newitem)

        self.setHorizontalHeaderLabels(horHeaders)


class ProductHistoryView(QWidget):
    def __init__(self, product):
        super().__init__()

        layout = QVBoxLayout()
        graphWidget = MplCanvas(self, width=5, height=4, dpi=100)
        self.label = QLabel(f"Product History {product.name}")
        layout.addWidget(self.label)
        layout.addWidget(graphWidget)
        self.setLayout(layout)

        graphWidget.axes.plot(
            [history.created_at for history in product.history],
            [history.price for history in product.history],
        )
        self.windowWidth = 1000
        self.windowHeight = 400
        self.resize(self.windowWidth, self.windowHeight)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
