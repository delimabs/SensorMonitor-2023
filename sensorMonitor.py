import sys
from PySide6.QtWidgets import QApplication
from interface import Main_Interface

"""     TO DO LIST
        #1 - DONE 17-01-2023 - Read and plot Thermocouple 1, BME280, MICS5524
        #2 Define and Create plot controls
        #3 Sequence implementation
        #4 - DONE 18-01-2023 - LOG DATA
        #5 VOVG
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main_Interface()
    window.show()
    app.exec()