import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
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

        ## --------------------------------- Registration --------------------------------- ##
        # Registration / Customer
        self.actionRegistrationCustomer = self.findChild(QAction, 'actionRegistrationCustomer')
        self.actionRegistrationCustomer.triggered.connect(self.open_registration_customer)
        
        # # Registration / Guarantor
        self.actionRegistrationGuarantor = self.findChild(QAction, 'actionRegistrationGuarantor')
        self.actionRegistrationGuarantor.triggered.connect(self.open_registration_guarantor)
        
        # Registration / Loan
        self.actionRegistrationLoan = self.findChild(QAction, 'actionRegistrationLoan')
        self.actionRegistrationLoan.triggered.connect(self.open_registration_loan)

        # Registration / Calculator
        self.actionCalculator = self.findChild(QAction, 'actionCalculator')
        self.actionCalculator.triggered.connect(self.open_calculator)

        ## --------------------------------- Search --------------------------------- ##
        # Search / Customer
        self.actionSearchCustomer = self.findChild(QAction, 'actionSearchCustomer')
        self.actionSearchCustomer.triggered.connect(self.open_search_customer)

        # Search / Customer
        self.actionSearchLoan = self.findChild(QAction, 'actionSearchLoan')
        self.actionSearchLoan.triggered.connect(self.open_search_loan)

        # Search / Guarantor
        self.actionSearchGuarantor = self.findChild(QAction, 'actionSearchGuarantor')
        self.actionSearchGuarantor.triggered.connect(self.open_search_guarantor)

        # Search / Collateral
        self.actionSearchCollateral = self.findChild(QAction, 'actionSearchCollateral')
        self.actionSearchCollateral.triggered.connect(self.open_search_collateral)

        # Search / Counseling
        self.actionSearchCounseling = self.findChild(QAction, 'actionSearchCounseling')
        self.actionSearchCounseling.triggered.connect(self.open_search_counseling)
        ## --------------------------------- Repayment --------------------------------- ##
        # Repayment / Single
        self.actionRepaymentSingle = self.findChild(QAction, 'actionRepaymentSingle')
        self.actionRepaymentSingle.triggered.connect(self.open_repayment_single)

        # Repayment / Batch
        self.actionRepaymentBatch = self.findChild(QAction, 'actionRepaymentBatch')
        self.actionRepaymentBatch.triggered.connect(self.open_repayment_batch)

        ## --------------------------------- Overdue --------------------------------- ##
        # Overdue / Management
        self.actionOverdueRegistration = self.findChild(QAction, 'actionOverdueRegistration')
        self.actionOverdueRegistration.triggered.connect(self.open_overdue_registration)
        
        # Overdue / Management
        self.actionOverdueManagement = self.findChild(QAction, 'actionOverdueManagement')
        self.actionOverdueManagement.triggered.connect(self.open_overdue_management)

        # # Overdue / Search
        # self.actionOverdueSearch = self.findChild(QAction, 'actionOverdueSearch')
        # self.actionOverdueSearch.triggered.connect(self.open_overdue_search)

        ## --------------------------------- Settings --------------------------------- ##
        # Settings / Officer
        self.actionSettingsOfficer = self.findChild(QAction, 'actionSettingsOfficer')
        self.actionSettingsOfficer.triggered.connect(self.open_settings_officer)

        # Settings / User
        self.actionSettingsUser = self.findChild(QAction, 'actionSettingsUser')
        self.actionSettingsUser.triggered.connect(self.open_settings_user)






    ## --------------------------------- Registration --------------------------------- ##
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

    # Registration / Loan
    def open_registration_loan(self):
        from src.pages.registration.loan import RegistrationLoanApp
        self.registration_loan_window = RegistrationLoanApp()
        self.registration_loan_window.show()

    # Registration / Calculator
    def open_calculator(self):
        from src.pages.registration.calculator import CalculatorApp
        self.calculator_window = CalculatorApp()
        self.calculator_window.show()

    ## --------------------------------- Search --------------------------------- ##
    # Search / Customer
    def open_search_customer(self):
        from src.pages.search.customer import SearchCustomerApp
        self.search_customer_window = SearchCustomerApp()
        self.search_customer_window.show()

    def open_search_guarantor(self):
        from src.pages.search.guarantor import SearchGuarantorApp
        self.search_guarantor_window = SearchGuarantorApp()
        self.search_guarantor_window.show()

    def open_search_collateral(self):
        from src.pages.search.collateral import SearchCollateralWindow
        self.search_collateral_window = SearchCollateralWindow()
        self.search_collateral_window.show()

    def open_search_counseling(self):
        from src.pages.search.counseling import SearchCounselingWindow
        self.search_counseling_window = SearchCounselingWindow()
        self.search_counseling_window.show()
    def open_search_loan(self):
        from src.pages.search.loan import SearchLoanApp
        self.search_loan_window = SearchLoanApp()
        self.search_loan_window.show()

    ## --------------------------------- Repayment --------------------------------- ##
    # # Repayment / Single
    def open_repayment_single(self):
        from src.pages.repayment.single import RepaymentSingleApp
        self.repayment_single_window = RepaymentSingleApp()
        self.repayment_single_window.show()

    # Repayment / Batch
    def open_repayment_batch(self):
        from src.pages.repayment.batch import RepaymentBatchApp
        self.repayment_batch_window = RepaymentBatchApp()
        self.repayment_batch_window.show()

    ## --------------------------------- Overdue --------------------------------- ##
    # Overdue / Registration
    def open_overdue_registration(self):
        from src.pages.overdue.registration import OverdueRegistrationApp
        self.settings_overdue_registration = OverdueRegistrationApp()
        self.settings_overdue_registration.show()

    # Overdue / Management
    def open_overdue_management(self):
        from src.pages.overdue.management import OverdueManagementApp
        self.settings_overdue_management = OverdueManagementApp()
        self.settings_overdue_management.show()

    # # Overdue / Search
    # def open_overdue_search(self):
    #     from src.pages.overdue.search import OverdueSearchApp
    #     self.settings_overdue_search = OverdueSearchApp()
    #     self.settings_overdue_search.show()

    ## --------------------------------- Settings --------------------------------- ##
    # Settings / Officer
    def open_settings_officer(self):
        from src.pages.settings.officer import SettingsOfficerApp
        self.settings_officer_window = SettingsOfficerApp()
        self.settings_officer_window.show()

    # Settings / User
    def open_settings_user(self):
        from src.pages.settings.user import SettingsUserApp
        self.settings_user_window = SettingsUserApp()
        self.settings_user_window.show()
    
    ## --------------------------------- Close Event --------------------------------- ##
    # def closeEvent(self, event):
    #     reply = QMessageBox.question(self, 'Exit Application', "Are you sure you want to exit?", QMessageBox.Cancel | QMessageBox.Ok, QMessageBox.Ok)
    #     if reply == QMessageBox.Ok:
    #         event.accept()
    #     else:
    #         event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeApp()
    window.show()
    sys.exit(app.exec_())
