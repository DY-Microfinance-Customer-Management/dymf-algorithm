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

        # Set default value for interestRate
        self.interestRate.setText("28")

        # Set all input fields to read-only initially
        self.set_read_only(True)

        # Set loanNumber and loanStatus to always be read-only
        self.loanNumber.setReadOnly(True)
        self.loanStatus.setEnabled(False)

        # Connect the search button to the function
        self.customerSearchButton.clicked.connect(self.check_and_open_select_customer_window)
        
        # Connect the calculate button to the function
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)

        # Override the closeEvent
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()

    def set_read_only(self, read_only):
        # List all the QLineEdit, QDateEdit, and QComboBox fields to set read-only
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
            check_box.setEnabled(False)  # Always read-only

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
        # Populate loan.ui fields with customer_data
        self.customerName.setText(customer_data.get('name', ''))
        self.customerContact.setText(customer_data.get('phone', ''))
        
        # Convert timestamp to yyyy-mm-dd format
        birth_timestamp = customer_data.get('birth', 0)
        if isinstance(birth_timestamp, (int, float)):
            birth_date = datetime.fromtimestamp(birth_timestamp).strftime('%Y-%m-%d')
            self.customerDateOfBirth.setText(birth_date)
        else:
            self.customerDateOfBirth.setText('')

        # Set gender checkboxes
        gender = customer_data.get('gender', '')
        self.checkBoxMale.setChecked(gender == 0)
        self.checkBoxFemale.setChecked(gender == 1)

        # Set contractDate to the current date and make it editable
        current_date = QDate.currentDate()
        self.contractDate.setDate(current_date)
        self.contractDate.setReadOnly(False)

        # Generate and set loan number
        self.generate_loan_number()
        
        # Make the other fields editable
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
        self.contractDate.setDate(QDate.currentDate())  # Reset contractDate
        # Clear other fields as needed
        self.set_read_only(True)

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
        # Show the confirmation message box before calculating
        reply = QMessageBox.question(
            self,
            'Confirm',
            '상환스케줄을 등록하시겠습니까?',
            QMessageBox.Ok | QMessageBox.Cancel
        )

        # If the user cancels, do not proceed with the calculation
        if reply != QMessageBox.Ok:
            return

        # If the user confirms, proceed with the calculation and saving
        self.calculate_loan_schedule()
        self.save_loan_to_firestore()

    def save_loan_to_firestore(self):
        # Create a dictionary to hold all loan info
        loan_info = {
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

        # Assuming 'self.schedule_df' contains the loan schedule DataFrame
        if hasattr(self, 'schedule_df'):
            # Convert the schedule DataFrame to a list of dictionaries
            loan_schedule = self.schedule_df.to_dict(orient="records")
            loan_info["loanSchedule"] = loan_schedule

        try:
            # Save the loan info to Firestore
            DB.collection("Loan").add(loan_info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the loan: {e}")

    def calculate_loan_schedule(self):
        # Check if customer is selected
        if not self.customerName.text():
            QMessageBox.warning(self, "Warning", "Please select a customer before calculating.")
            return

        # Check if required fields are filled
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

            # Map the loanRepaymentCycle text to appropriate cycle value
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

            # Create a LoanCalculator object
            calculator = LoanCalculator(
                start_date=self.contractDate.date().toPyDate(),
                principal=principal,
                expiration_months=expiration_months,
                annual_interest_rate=annual_interest_rate
            )

            # Determine which loan type to calculate
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

            # Display the schedule in the QTableView or QTableWidget
            self.display_schedule(self.schedule_df)

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def display_schedule(self, df: pd.DataFrame):
        vertical_header = [str(i) for i in df['Period'].values]
        df = df.drop(columns=['Period'])
        
        # Define a function to format numbers with commas
        def format_number(value):
            try:
                return "{:,}".format(int(value))  # Format with commas and 2 decimal places
            except ValueError:
                return value  # Return the value as-is if it's not a number
        
        # Apply formatting to all numerical columns
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

def main():
    app = QApplication(sys.argv)
    window = LoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
