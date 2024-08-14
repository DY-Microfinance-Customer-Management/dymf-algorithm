import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5 import uic

class HomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "home.ui")
        uic.loadUi(ui_path, self)

        # 1. 고객관리 / 고객등록
        self.action = self.findChild(QAction, 'action')
        self.action.triggered.connect(self.open_customer_registration)

        # 2. 대출관리 / 대출등록
        self.action3 = self.findChild(QAction, 'action_3')
        self.action3.triggered.connect(self.open_loan)

        # 2. 대출관리 / 이자계산기
        self.action3 = self.findChild(QAction, 'action_12')
        self.action3.triggered.connect(self.open_calculator)

    def open_customer_registration(self):
        from pages.customer.registration import RegistrationApp
        self.customer_registration_window = RegistrationApp()
        self.customer_registration_window.show()

    def open_loan(self):
        from pages.loan.loan import LoanWindow
        self.loan_window = LoanWindow()
        self.loan_window.show()
    
    def open_calculator(self):
        from pages.loan.calculator import CalculatorApp
        self.calculator_window = CalculatorApp()
        self.calculator_window.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Application', 
                                     "Are you sure you want to exit?", 
                                     QMessageBox.Cancel | QMessageBox.Ok, 
                                     QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeApp()
    window.show()
    sys.exit(app.exec_())
