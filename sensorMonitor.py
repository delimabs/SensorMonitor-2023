import sys
from PySide6.QtWidgets import QApplication
from interface import Main_Interface


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main_Interface()
    window.show()
    app.exec()