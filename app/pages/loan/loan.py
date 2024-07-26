import sys
from PyQt5 import QtWidgets, uic

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi("kor_loan.ui", self)
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
