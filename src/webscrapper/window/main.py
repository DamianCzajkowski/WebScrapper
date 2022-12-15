from functools import partial

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from webscrapper.database.database import initialize_database
from webscrapper.window.window_service import ProductDisplayService, ShopDisplayService


class Window(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.restartAsTerminal = False
        self.setWindowTitle("WebScrapper")

        self.windowWidth = 1200
        self.windowHeight = int(0.618 * self.windowWidth)
        self.resize(self.windowWidth, self.windowHeight)

        self.setupUI()

    def setupUI(self):
        # MENU
        self.menuButtonsLayout = QVBoxLayout()
        self.menuButtonsWidget = QWidget()

        self.buttonMap = {}
        keyBoard = ["Products", "Shops", "Settings", "Help"]
        self.tabs = []

        for idx, value in enumerate(keyBoard):
            button = QPushButton(value, self)
            self.tabs.append(getattr(self, f"display{value}")())
            button.clicked.connect(partial(self.setTabIndex, idx))
            self.buttonMap[value] = button
            self.menuButtonsLayout.addWidget(self.buttonMap[value])

        exitButton = QPushButton("Exit", self)
        exitButton.clicked.connect(self.exit)
        self.menuButtonsLayout.addWidget(exitButton)
        self.menuButtonsLayout.addStretch(5)
        self.menuButtonsLayout.setSpacing(20)
        self.menuButtonsWidget.setLayout(self.menuButtonsLayout)

        # MAIN ITEM
        self.mainWidget = QTabWidget()
        self.mainWidget.tabBar().setObjectName("mainTab")

        for tab in self.tabs:
            self.mainWidget.addTab(tab, "")

        self.mainWidget.setCurrentIndex(0)
        self.mainWidget.setStyleSheet("""QTabBar::tab{width: 0; height: 0; margin: 0; padding: 0; border: none;}""")

        # CONTAINER
        container = QWidget()
        self.containerLayout = QHBoxLayout()
        self.containerLayout.addWidget(self.menuButtonsWidget)
        self.containerLayout.addWidget(self.mainWidget)

        self.containerLayout.setStretch(0, 40)
        self.containerLayout.setStretch(1, 200)

        container.setLayout(self.containerLayout)
        self.setCentralWidget(container)

        # self.searchbar = QLineEdit()
        # centralWidget = QWidget(self)
        # centralWidget.setLayout(self.generalLayout)
        # self.setCentralWidget(centralWidget)
        # self._createMenu()
        # self._createMainPanel()

    def setTabIndex(self, idx):
        self.mainWidget.setCurrentIndex(idx)

    def displayShops(self):
        return ShopDisplayService(self, session=self.session)

    def displayProducts(self):
        return ProductDisplayService(self, session=self.session)

    def displaySettings(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Settings"))
        restartButton = QCheckBox("Restart as terminal app")
        restartButton.stateChanged.connect(lambda: self.setRestartAsTerminal(restartButton))
        mainLayout.addWidget(restartButton)
        mainLayout.addStretch(5)
        main = QWidget()
        main.setLayout(mainLayout)
        return main

    def setRestartAsTerminal(self, btn):
        self.restartAsTerminal = btn.isChecked()

    def displayHelp(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel("Help"))
        mainLayout.addStretch(5)
        main = QWidget()
        main.setLayout(mainLayout)
        return main

    def exit(self):
        self.close()


def main():
    session = initialize_database()
    app = QApplication([])
    window = Window(session)
    window.show()
    app.exec()

    return "TERMINAL" if window.restartAsTerminal else "EXIT"


if __name__ == "__main__":
    main()
