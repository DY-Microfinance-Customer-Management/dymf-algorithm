import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent

class HomeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "home.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Connect menu actions to functions
        self.setup_connections()

    def setup_connections(self):
        # Registration / Customer
        self.actionRegistrationCustomer = self.findChild(QAction, 'actionRegistrationCustomer')
        self.actionRegistrationCustomer.triggered.connect(self.open_registration_customer)

        # Registration / Guarantor
        self.actionRegistrationGuarantor = self.findChild(QAction, 'actionRegistrationGuarantor')
        self.actionRegistrationGuarantor.triggered.connect(self.open_registration_guarantor)

        # Registration / Loan
        self.actionRegistrationLoan = self.findChild(QAction, 'actionRegistrationLoan')
        self.actionRegistrationLoan.triggered.connect(self.open_registration_loan)

        # Registration / Calculator
        self.actionCalculator = self.findChild(QAction, 'actionCalculator')
        self.actionCalculator.triggered.connect(self.open_calculator)

        # Search / Customer
        self.actionSearchCustomer = self.findChild(QAction, 'actionSearchCustomer')
        self.actionSearchCustomer.triggered.connect(self.open_search_customer)

        # Search / Loan
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

        # Repayment / Single
        self.actionRepaymentSingle = self.findChild(QAction, 'actionRepaymentSingle')
        self.actionRepaymentSingle.triggered.connect(self.open_repayment_single)

        # Repayment / Batch
        self.actionRepaymentBatch = self.findChild(QAction, 'actionRepaymentBatch')
        self.actionRepaymentBatch.triggered.connect(self.open_repayment_batch)

        # Overdue / Registration
        self.actionOverdueRegistration = self.findChild(QAction, 'actionOverdueRegistration')
        self.actionOverdueRegistration.triggered.connect(self.open_overdue_registration)

        # Overdue / Management
        self.actionOverdueManagement = self.findChild(QAction, 'actionOverdueManagement')
        self.actionOverdueManagement.triggered.connect(self.open_overdue_management)

        # Overdue / Search
        self.actionOverdueSearch = self.findChild(QAction, 'actionOverdueSearch')
        self.actionOverdueSearch.triggered.connect(self.open_overdue_search)

        # Report / Periodic Balance
        self.actionPeriodicLoanBalanceReport = self.findChild(QAction, 'actionPeriodicLoanBalanceReport')
        self.actionPeriodicLoanBalanceReport.triggered.connect(self.open_report_periodic_balance)

        # Personnel / Staff Register
        self.actionPersonnelStaffRegister = self.findChild(QAction, 'actionPersonnelStaffRegister')
        self.actionPersonnelStaffRegister.triggered.connect(self.open_personnel_staff_register)

        # # Personnel / Payroll
        # self.actionPersonnelStaffRegister = self.findChild(QAction, 'actionPersonnelStaffRegister')
        # self.actionPersonnelStaffRegister.triggered.connect(self.open_personnel_payroll)

        # # Personnel / Download Report
        # self.actionPersonnelStaffRegister = self.findChild(QAction, 'actionPersonnelStaffRegister')
        # self.actionPersonnelStaffRegister.triggered.connect(self.open_personnel_download_report)

        # Settings / Officer
        self.actionSettingsOfficer = self.findChild(QAction, 'actionSettingsOfficer')
        self.actionSettingsOfficer.triggered.connect(self.open_settings_officer)

        # Settings / User
        self.actionSettingsUser = self.findChild(QAction, 'actionSettingsUser')
        self.actionSettingsUser.triggered.connect(self.open_settings_user)

        # Settings / Fixed Asset
        self.actionSettingsAssets = self.findChild(QAction, 'actionSettingsAssets')
        self.actionSettingsAssets.triggered.connect(self.open_settings_assets)

    def show_child_window(self, window):
        # Set the parent to the main window to ensure it stays above the main window but below other apps
        window.setParent(self, Qt.Window)
        window.setAttribute(Qt.WA_DeleteOnClose)
        window.setWindowModality(Qt.NonModal)  # Ensure it behaves like a normal window (not modal)
        window.show()

    # Registration / Customer
    def open_registration_customer(self):
        from src.pages.registration.customer import RegistrationCustomerApp
        self.registration_customer_window = RegistrationCustomerApp()
        self.show_child_window(self.registration_customer_window)

    # Registration / Guarantor
    def open_registration_guarantor(self):
        from src.pages.registration.guarantor import RegistrationGuarantorApp
        self.registration_guarantor_window = RegistrationGuarantorApp()
        self.show_child_window(self.registration_guarantor_window)

    # Registration / Loan
    def open_registration_loan(self):
        from src.pages.registration.loan import RegistrationLoanApp
        self.registration_loan_window = RegistrationLoanApp()
        self.show_child_window(self.registration_loan_window)

    # Registration / Calculator
    def open_calculator(self):
        from src.pages.registration.calculator import CalculatorApp
        self.calculator_window = CalculatorApp()
        self.show_child_window(self.calculator_window)

    # Search / Customer
    def open_search_customer(self):
        from src.pages.search.customer import SearchCustomerApp
        self.search_customer_window = SearchCustomerApp()
        self.show_child_window(self.search_customer_window)

    # Search / Guarantor
    def open_search_guarantor(self):
        from src.pages.search.guarantor import SearchGuarantorApp
        self.search_guarantor_window = SearchGuarantorApp()
        self.show_child_window(self.search_guarantor_window)

    # Search / Collateral
    def open_search_collateral(self):
        from src.pages.search.collateral import SearchCollateralWindow
        self.search_collateral_window = SearchCollateralWindow()
        self.show_child_window(self.search_collateral_window)

    # Search / Counseling
    def open_search_counseling(self):
        from src.pages.search.counseling import SearchCounselingWindow
        self.search_counseling_window = SearchCounselingWindow()
        self.show_child_window(self.search_counseling_window)

    # Search / Loan
    def open_search_loan(self):
        from src.pages.search.loan import SearchLoanApp
        self.search_loan_window = SearchLoanApp()
        self.show_child_window(self.search_loan_window)

    # Repayment / Single
    def open_repayment_single(self):
        from src.pages.repayment.single import RepaymentSingleApp
        self.repayment_single_window = RepaymentSingleApp()
        self.show_child_window(self.repayment_single_window)

    # Repayment / Batch
    def open_repayment_batch(self):
        from src.pages.repayment.batch import RepaymentBatchApp
        self.repayment_batch_window = RepaymentBatchApp()
        self.show_child_window(self.repayment_batch_window)

    # Overdue / Registration
    def open_overdue_registration(self):
        from src.pages.overdue.registration import OverdueRegistrationApp
        self.overdue_registration_window = OverdueRegistrationApp()
        self.show_child_window(self.overdue_registration_window)

    # Overdue / Management
    def open_overdue_management(self):
        from src.pages.overdue.management import OverdueManagementApp
        self.overdue_management_window = OverdueManagementApp()
        self.show_child_window(self.overdue_management_window)

    # Overdue / Search
    def open_overdue_search(self):
        from src.pages.overdue.search import OverdueSearchApp
        self.overdue_search_window = OverdueSearchApp()
        self.show_child_window(self.overdue_search_window)

    # Report / Periodic Balance
    def open_report_periodic_balance(self):
        from src.pages.report.periodic_balance import ReportPeriodicBalanceApp
        self.report_periodic_balance_window = ReportPeriodicBalanceApp()
        self.show_child_window(self.report_periodic_balance_window)

    # Personnel / Staff Register
    def open_personnel_staff_register(self):
        from src.pages.personnel.registration import PersonnelRegisterApp
        self.personnel_registration_window = PersonnelRegisterApp()
        self.show_child_window(self.personnel_registration_window)

    # Settings / Officer
    def open_settings_officer(self):
        from src.pages.settings.officer import SettingsOfficerApp
        self.settings_officer_window = SettingsOfficerApp()
        self.show_child_window(self.settings_officer_window)

    # Settings / User
    def open_settings_user(self):
        from src.pages.settings.user import SettingsUserApp
        self.settings_user_window = SettingsUserApp()
        self.show_child_window(self.settings_user_window)

    # Settings / Fixed Asset
    def open_settings_assets(self):
        from src.pages.settings.fixed_asset import SettingsFixedAssetApp
        self.settings_assets_window = SettingsFixedAssetApp()
        self.show_child_window(self.settings_assets_window)

    # Handle minimizing all child windows when the main window is minimized
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowMinimized:
                # Minimize all child windows when the main window is minimized
                for child in self.findChildren(QMainWindow):
                    if child.isVisible():
                        child.showMinimized()
        super().changeEvent(event)

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
