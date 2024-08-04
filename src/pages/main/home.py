import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QDialog
from PyQt5 import uic

class HomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "home.ui")
        uic.loadUi(ui_path, self)

        self.action = self.findChild(QAction, 'action')
        self.action.triggered.connect(self.open_registration)

    def open_registration(self):
        from pages.customer.registration import RegistrationApp
        self.registeration_window = RegistrationApp()
        self.registeration_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeApp()
    sys.exit(app.exec_())
