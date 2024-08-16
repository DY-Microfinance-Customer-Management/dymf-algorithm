import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import pyqtSlot, Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
from datetime import datetime
from pages.loan.select_customer import SelectCustomerWindow
from components import DB
from components.loan_calculator import LoanCalculator

class LoanWindow(QMainWindow):
    def __init__(self):
        super(LoanWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan.ui")
        uic.loadUi(ui_path, self)

        self.interestRate.setText("28")

        self.set_read_only(True)

        self.loanNumber.setReadOnly(True)
        self.loanStatus.setEnabled(False)

        self.customer_uid = None  # To store the selected customer's UID

        self.customerSearchButton.clicked.connect(self.check_and_open_select_customer_window)
        
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.existing_loan_id = None  # To track if we're updating an existing document
        self.show()

    def set_read_only(self, read_only):
        line_edits = [
            self.loanAmount, self.interestRate, self.expiry
        ]
        date_edits = [
            self.contractDate
        ]
        combo_boxes = [
            self.loanType, self.loanOfficer, self.loanRepaymentCycle
        ]
        check_boxes = [
            self.checkBoxMale, self.checkBoxFemale
        ]

        for line_edit in line_edits:
            line_edit.setReadOnly(read_only)
        
        for date_edit in date_edits:
            date_edit.setReadOnly(read_only)
        
        for combo_box in combo_boxes:
            combo_box.setEnabled(not read_only)
        
        for check_box in check_boxes:
            check_box.setEnabled(False)

    def check_and_open_select_customer_window(self):
        if self.customerName.text():
            reply = QMessageBox.question(
                self,
                'Confirm',
                'There is already data being entered. Do you want to clear it?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                self.clear_all_fields()
                self.open_select_customer_window()
        else:
            self.open_select_customer_window()

    def open_select_customer_window(self):
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    @pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        print(f"Customer selected: {customer_data}")

        self.customerName.setText(customer_data.get('name', ''))
        self.customerContact.setText(customer_data.get('phone', ''))
        self.customer_uid = customer_data.get('uid', '')  # Save customer's UID
        
        birth_timestamp = customer_data.get('birth', 0)
        if isinstance(birth_timestamp, (int, float)):
            birth_date = datetime.fromtimestamp(birth_timestamp).strftime('%Y-%m-%d')
            self.customerDateOfBirth.setText(birth_date)
        else:
            self.customerDateOfBirth.setText('')

        gender = customer_data.get('gender', '')
        self.checkBoxMale.setChecked(gender == 0)
        self.checkBoxFemale.setChecked(gender == 1)

        current_date = QDate.currentDate()
        self.contractDate.setDate(current_date)
        self.contractDate.setReadOnly(False)

        self.check_existing_customer_loan()

    def check_existing_customer_loan(self):
        # Check if the customer UID already has a loan in the database
        if not self.customer_uid:
            QMessageBox.warning(self, "Warning", "Customer UID is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("customer_uid", "==", self.customer_uid).get()

        if len(query) > 0:
            # Show message if a loan already exists for this customer
            reply = QMessageBox.question(
                self,
                'Confirm',
                'A loan already exists for this customer. Do you want to continue?',
                QMessageBox.Ok | QMessageBox.Cancel
            )

            if reply != QMessageBox.Ok:
                self.clear_all_fields()
                return

        self.generate_loan_number()
        self.set_read_only(False)

    def generate_loan_number(self):
        loans_ref = DB.collection("Loan")
        loans = loans_ref.order_by("loanNumber", direction="DESCENDING").limit(1).stream()

        max_loan_number = 0
        for loan in loans:
            max_loan_number = loan.to_dict().get("loanNumber", 0)

        new_loan_number = int(max_loan_number) + 1
        if new_loan_number > 99999999:
            QMessageBox.critical(self, "Error", "Loan number limit exceeded.")
            return

        self.loanNumber.setText(f"{new_loan_number:08d}")

    def clear_all_fields(self):
        self.customerName.clear()
        self.customerContact.clear()
        self.customerDateOfBirth.clear()
        self.loanAmount.clear()
        self.interestRate.clear()
        self.loanTerm.clear()
        self.paymentDueDate.clear()
        self.checkBoxMale.setChecked(False)
        self.checkBoxFemale.setChecked(False)
        self.loanNumber.clear()
        self.contractDate.setDate(QDate.currentDate())
        self.existing_loan_id = None  # Reset the existing loan tracking
        self.set_read_only(True)
        self.customer_uid = None  # Clear the stored customer UID

    def closeEvent(self, event):
        if self.customerName.text():
            reply = QMessageBox.question(
                self,
                'Confirm',
                'You have unsaved data. Are you sure you want to exit?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def on_calculate_button_clicked(self):
        self.check_existing_loan()

    def check_existing_loan(self):
        # Check if loanNumber already exists in Firestore
        loan_number = self.loanNumber.text()
        if not loan_number:
            QMessageBox.warning(self, "Warning", "Loan number is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("loanNumber", "==", loan_number).get()

        if len(query) > 0:
            self.existing_loan_id = query[0].id  # Store the document ID to update later
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Do you want to re-register the repayment schedule?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
        else:
            self.existing_loan_id = None
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Do you want to register the repayment schedule?',
                QMessageBox.Ok | QMessageBox.Cancel
            )

        if reply == QMessageBox.Ok:
            self.calculate_loan_schedule()
            self.save_loan_to_firestore()

    def save_loan_to_firestore(self):
        # Create a dictionary to hold all loan info
        loan_info = {
            "customer_uid": self.customer_uid,  # Save the customer UID with the loan
            "customerName": self.customerName.text(),
            "customerContact": self.customerContact.text(),
            "customerDateOfBirth": self.customerDateOfBirth.text(),
            "loanAmount": self.loanAmount.text(),
            "interestRate": self.interestRate.text(),
            "expiry": self.expiry.text(),
            "loanType": self.loanType.currentText(),
            "loanOfficer": self.loanOfficer.currentText(),
            "loanRepaymentCycle": self.loanRepaymentCycle.currentText(),
            "loanNumber": self.loanNumber.text(),
            "contractDate": self.contractDate.date().toString("yyyy-MM-dd"),
            "loanStatus": self.loanStatus.currentText()
        }

        if hasattr(self, 'schedule_df'):
            loan_schedule = self.schedule_df.to_dict(orient="records")
            loan_info["loanSchedule"] = loan_schedule

        try:
            if self.existing_loan_id:
                # Update existing document
                DB.collection("Loan").document(self.existing_loan_id).set(loan_info)
            else:
                # Add new document
                DB.collection("Loan").add(loan_info)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the loan: {e}")

    def calculate_loan_schedule(self):
        if not self.customerName.text():
            QMessageBox.warning(self, "Warning", "Please select a customer before calculating.")
            return

        if not all([
            self.loanType.currentText(),
            self.loanAmount.text(),
            self.interestRate.text(),
            self.expiry.text(),
            self.loanRepaymentCycle.currentText()
        ]):
            QMessageBox.warning(self, "Warning", "Please fill in Loan Type, Loan Amount, Interest Rate, Expiry, and Repayment Cycle.")
            return

        try:
            principal = int(self.loanAmount.text())
            annual_interest_rate = float(self.interestRate.text()) / 100
            expiration_months = int(self.expiry.text())

            cycle_text = self.loanRepaymentCycle.currentText()
            cycle_mapping = {
                "Monthly": "month",
                "4 Week": "4week",
                "2 Week": "2week",
                "Weekly": "week"
            }
            cycle = cycle_mapping.get(cycle_text)

            if not cycle:
                QMessageBox.critical(self, "Error", "Invalid repayment cycle selected.")
                return

            calculator = LoanCalculator(
                start_date=self.contractDate.date().toPyDate(),
                principal=principal,
                expiration_months=expiration_months,
                annual_interest_rate=annual_interest_rate
            )

            loan_type = self.loanType.currentText().lower()
            if loan_type == "equal":
                self.schedule_df = calculator.equal_payment(cycle=cycle)
            elif loan_type == "equal principal":
                self.schedule_df = calculator.equal_principal_payment(cycle=cycle)
            elif loan_type == "bullet":
                self.schedule_df = calculator.bullet_payment(cycle=cycle)
            else:
                QMessageBox.critical(self, "Error", "Invalid loan type selected.")
                return

            self.display_schedule(self.schedule_df)

            self.update_other_tabs()

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def update_other_tabs(self):
        # Update fields across other tabs based on the current loan data
        self.guarantorLoanNumber.setText(self.loanNumber.text())
        self.collateralLoanNumber.setText(self.loanNumber.text())
        self.counselingLoanNumber.setText(self.loanNumber.text())

        self.guarantorLoanStatus.setText(self.loanStatus.currentText())
        self.collateralLoanStatus.setText(self.loanStatus.currentText())
        self.counselingLoanStatus.setText(self.loanStatus.currentText())

        self.guarantorLoanOfficer.setText(self.loanOfficer.currentText())
        self.collateralLoanOfficer.setText(self.loanOfficer.currentText())
        self.counselingLoanOfficer.setText(self.loanOfficer.currentText())

        contract_date_str = self.contractDate.date().toString("yyyy-MM-dd")
        self.guarantorContractDate.setText(contract_date_str)
        self.collateralContractDate.setText(contract_date_str)
        self.counselingContractDate.setText(contract_date_str)

        self.guarantorLoanType.setText(self.loanType.currentText())
        self.collateralLoanType.setText(self.loanType.currentText())
        self.counselingLoanType.setText(self.loanType.currentText())

        self.guarantorLoanAmount.setText(self.loanAmount.text())
        self.collateralLoanAmount.setText(self.loanAmount.text())
        self.counselingLoanAmount.setText(self.loanAmount.text())

        self.guarantorInterestRate.setText(self.interestRate.text())
        self.collateralInterestRate.setText(self.interestRate.text())
        self.counselingInterestRate.setText(self.interestRate.text())

        self.guarantorExpiry.setText(self.expiry.text())
        self.collateralExpiry.setText(self.expiry.text())
        self.counselingExpiry.setText(self.expiry.text())

        self.guarantorRepaymentCycle.setText(self.loanRepaymentCycle.currentText())
        self.collateralRepaymentCycle.setText(self.loanRepaymentCycle.currentText())
        self.counselingRepaymentCycle.setText(self.loanRepaymentCycle.currentText())

    def display_schedule(self, df: pd.DataFrame):
        vertical_header = [str(i) for i in df['Period'].values]
        df = df.drop(columns=['Period'])
        
        def format_number(value):
            try:
                return "{:,}".format(int(value))
            except ValueError:
                return value

        for column in df.columns:
            df[column] = df[column].apply(format_number)
        
        model = QStandardItemModel(df.shape[0], df.shape[1])
        model.setHorizontalHeaderLabels(df.columns.tolist())
        model.setVerticalHeaderLabels(vertical_header)
        
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(df.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item non-editable
                model.setItem(row, col, item)
        
        self.loanScheduleTable.setModel(model)
        self.loanScheduleTable.resizeColumnsToContents()

        # Set the same model for repaymentScheduleTable
        self.repaymentScheduleTable.setModel(model)
        self.repaymentScheduleTable.resizeColumnsToContents()

def main():
    app = QApplication(sys.argv)
    window = LoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
