import sys, os
from datetime import datetime

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableView, QApplication
from PyQt5.QtCore import pyqtSlot, Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from pages.loan.select_customer import SelectCustomerWindow
from components import DB
from components.loan_calculator import LoanCalculator
from datetime import datetime, timedelta

class OverdueWindow(QMainWindow):
    def __init__(self):
        super(OverdueWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "overdue.ui")
        uic.loadUi(ui_path, self)

        # Disable everything except the Search button initially
        self.disable_all_fields()
        self.customerSearchButton.clicked.connect(self.on_search_customer)
        self.overdueNewButton.clicked.connect(self.on_new_button_clicked)
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)

        # Additional fields for state management
        self.current_principal = 0
        self.current_interest = 0
        self.current_overdue_interest = 0

    def disable_all_fields(self):
        # Disable everything except the search button initially
        self.overdueNewButton.setEnabled(False)
        self.Principal.setEnabled(False)
        self.Interest.setEnabled(False)
        self.Overdue_Interest.setEnabled(False)
        self.loanRepaymentCycle.setEnabled(False)
        self.calculateButton.setEnabled(False)
        self.Minus_Principal.setEnabled(False)
        self.Minus_Interest.setEnabled(False)
        self.Minus_Overdue_Interest.setEnabled(False)

    def enable_new_fields(self):
        self.Principal.setEnabled(True)
        self.Interest.setEnabled(True)
        self.Overdue_Interest.setEnabled(True)
        self.loanRepaymentCycle.setEnabled(True)
        self.calculateButton.setEnabled(True)

    def enable_minus_fields(self):
        self.Minus_Principal.setEnabled(True)
        self.Minus_Interest.setEnabled(True)
        self.Minus_Overdue_Interest.setEnabled(True)
        self.calculateButton.setEnabled(True)

    def on_search_customer(self):
        # Simulate customer search - would be connected to a real database or API in a real scenario
        customer_name = "John Doe"
        self.customerName.setText(customer_name)
        self.customerDateOfBirth.setText("1990-01-01")
        self.checkBoxMale.setChecked(True)

        # Enable "New" button once a customer is selected
        self.overdueNewButton.setEnabled(True)

    def on_new_button_clicked(self):
        # Check if the customer has overdue interest
        overdue_interest = float(self.Overdue_Interest.text()) if self.Overdue_Interest.text() else 0
        if overdue_interest > 0:
            self.enable_minus_fields()  # If overdue interest, enable the minus fields
        else:
            self.enable_new_fields()  # Otherwise, allow entry of new principal, interest, and repayment cycle

    def on_calculate_button_clicked(self):
        if self.Principal.isEnabled():  # Normal loan calculation
            self.calculate_new_schedule()
        elif self.Minus_Principal.isEnabled():  # Overdue loan calculation
            self.calculate_overdue_schedule()

    def calculate_new_schedule(self):
        try:
            principal = int(self.Principal.text())
            interest = float(self.Interest.text())
            overdue_interest = float(self.Overdue_Interest.text())
            repayment_cycle_days = int(self.loanRepaymentCycle.currentText().split()[0])

            next_payment_date = datetime.now() + timedelta(days=repayment_cycle_days)
            self.current_principal = principal
            self.current_interest = interest
            self.current_overdue_interest = overdue_interest

            # Display in the table view
            self.display_schedule(principal, interest, overdue_interest, next_payment_date)

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter valid values.")

    def calculate_overdue_schedule(self):
        try:
            minus_principal = int(self.Minus_Principal.text())
            minus_interest = float(self.Minus_Interest.text())
            minus_overdue_interest = float(self.Minus_Overdue_Interest.text())

            self.current_principal = max(0, self.current_principal - minus_principal)
            self.current_interest = max(0, self.current_interest - minus_interest)
            self.current_overdue_interest = max(0, self.current_overdue_interest - minus_overdue_interest)

            if self.current_principal == 0 and self.current_interest == 0 and self.current_overdue_interest == 0:
                QMessageBox.information(self, "Fully Paid", "The loan has been fully paid off.")
                self.disable_all_fields()
                return

            repayment_cycle_days = int(self.loanRepaymentCycle.currentText().split()[0])
            next_payment_date = datetime.now() + timedelta(days=repayment_cycle_days)

            # Display in the table view
            self.display_schedule(self.current_principal, self.current_interest, self.current_overdue_interest,
                                  next_payment_date)

        except ValueError:
            QMessageBox.warning(self, "Error", "enter valid values.")

    def display_schedule(self, principal, interest, overdue_interest, payment_date):
        model = QStandardItemModel(1, 4)
        model.setHorizontalHeaderLabels(["Next Payment Date", "Principal", "Interest", "Overdue Interest"])

        model.setItem(0, 0, QStandardItem(payment_date.strftime("%Y-%m-%d")))
        model.setItem(0, 1, QStandardItem(f"{principal:,}"))
        model.setItem(0, 2, QStandardItem(f"{interest:,.2f}"))
        model.setItem(0, 3, QStandardItem(f"{overdue_interest:,.2f}"))

        self.OverdueScheduleTable.setModel(model)
        self.OverdueScheduleTable.resizeColumnsToContents()

def main():
    app = QApplication(sys.argv)
    window = OverdueWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
