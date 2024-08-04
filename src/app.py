import sys
from PyQt5.QtWidgets import QApplication
from pages.main.login import LoginApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    sys.exit(app.exec_())
