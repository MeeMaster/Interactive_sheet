from PyQt5.QtWidgets import (QMainWindow, QApplication)
from shooting import ShootingWidget
import sys
from parameters import translate_ui


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setWindowTitle(self.title)

        # Add main widget
        self.window_widget = ShootingWidget(self)
        self.setCentralWidget(self.window_widget)
        self.setWindowTitle(translate_ui("ui_shooting_app"))
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
