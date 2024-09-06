import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic

class HomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "home.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        ## -- Registration -- ##
        # Registration / Customer
        self.actionRegistrationCustomer = self.findChild(QAction, 'actionRegistrationCustomer')
        self.actionRegistrationCustomer.triggered.connect(self.open_registration_customer)
        
        # # Registration / Guarantor
        self.actionRegistrationGuarantor = self.findChild(QAction, 'actionRegistrationGuarantor')
        self.actionRegistrationGuarantor.triggered.connect(self.open_registration_guarantor)
        
        # # Registration / Loan
        # self.actionRegistrationLoan = self.findChild(QAction, 'actionRegistrationLoan')
        # self.actionRegistrationLoan.triggered.connect(self.open_registration_loan)

        # Registration / Calculator
        self.actionCalculator = self.findChild(QAction, 'actionCalculator')
        self.actionCalculator.triggered.connect(self.open_calculator)

        ## -- Search -- ##
        # Search / Customer
        self.actionSearchCustomer = self.findChild(QAction, 'actionSearchCustomer')
        self.actionSearchCustomer.triggered.connect(self.open_search_customer)

    ## -- Registration -- ##
    # Registration / Customer
    def open_registration_customer(self):
        from src.pages.registration.customer import RegistrationCustomerApp
        self.registration_customer_window = RegistrationCustomerApp()
        self.registration_customer_window.show()

    # # Registration / Guarantor
    def open_registration_guarantor(self):
        from src.pages.registration.guarantor import RegistrationGuarantorApp
        self.registration_guarantor_window = RegistrationGuarantorApp()
        self.registration_guarantor_window.show()

    # # Registration / Loan
    # def open_registration_loan(self):
    #     from src.pages.registration.loan import RegistrationLoanApp
    #     self.registration_loan_window = RegistrationLoanApp()
    #     self.registration_loan_window.show()

    # Registration / Calculator
    def open_calculator(self):
        from src.pages.registration.calculator import CalculatorApp
        self.calculator_window = CalculatorApp()
        self.calculator_window.show()

    ## -- Search -- ##
    # Search / Customer
    def open_search_customer(self):
        from src.pages.search.customer import SearchCustomerApp
        self.search_customer_window = SearchCustomerApp()
        self.search_customer_window.show()
    
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit Application', "Are you sure you want to exit?", QMessageBox.Cancel | QMessageBox.Ok, QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeApp()
    window.show()
    sys.exit(app.exec_())
