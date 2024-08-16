import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableView
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

        # Disable paidButton and deleteButton initially
        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        # Set selection behavior for tables
        self.repaymentScheduleTable.setSelectionBehavior(QTableView.SelectRows)
        self.receivedTable.setSelectionBehavior(QTableView.SelectRows)

        # Connect the table click events to the respective functions
        self.repaymentScheduleTable.clicked.connect(self.handle_table_click)
        self.receivedTable.clicked.connect(self.handle_received_table_click)

        # Connect the paidButton and deleteButton click events
        self.paidButton.clicked.connect(self.on_paid_button_clicked)
        self.deleteButton.clicked.connect(self.on_delete_button_clicked)

        self.selected_row = None  # Track selected row
        self.selected_received_row = None  # Track selected row for receivedTable

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
        if not self.customer_uid:
            QMessageBox.warning(self, "Warning", "Customer UID is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("customer_uid", "==", self.customer_uid).get()

        if len(query) > 0:
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
        current_year_month = datetime.now().strftime("%Y%m")

        loans_ref = DB.collection("Loan")
        loans = loans_ref.order_by("loanNumber", direction="DESCENDING").limit(1).stream()

        max_sequence_number = 0
        for loan in loans:
            loan_number = loan.to_dict().get("loanNumber", "")
            if loan_number.startswith(current_year_month):
                sequence_number = int(loan_number[6:])
                max_sequence_number = max(max_sequence_number, sequence_number)

        new_sequence_number = max_sequence_number + 1
        new_loan_number = f"{current_year_month}{new_sequence_number:07d}"

        self.loanNumber.setText(new_loan_number)

    def clear_all_fields(self):
        self.customerName.clear()
        self.customerContact.clear()
        self.customerDateOfBirth.clear()
        self.loanAmount.clear()
        self.interestRate.clear()
        self.loanType.clear()
        self.paymentDueDate.clear()
        self.checkBoxMale.setChecked(False)
        self.checkBoxFemale.setChecked(False)
        self.loanNumber.clear()
        self.contractDate.setDate(QDate.currentDate())
        self.existing_loan_id = None  # Reset the existing loan tracking
        self.set_read_only(True)
        self.customer_uid = None  # Clear the stored customer UID
        self.paidButton.setEnabled(False)  # Disable paidButton when fields are cleared
        self.deleteButton.setEnabled(False)  # Disable deleteButton when fields are cleared

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
        loan_info = {
            "customer_uid": self.customer_uid,
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

            for schedule_item in loan_schedule:
                schedule_item['status'] = 0  # 초기 상태를 'Scheduled'로 설정

            loan_info["loanSchedule"] = loan_schedule

        try:
            if self.existing_loan_id:
                DB.collection("Loan").document(self.existing_loan_id).set(loan_info)
            else:
                # 새 대출 등록시 생성된 loan_id를 설정
                doc_ref = DB.collection("Loan").add(loan_info)
                self.existing_loan_id = doc_ref[1].id  # 새로 생성된 문서의 ID를 저장

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
        df_with_status = df.copy()

        # Check if 'Status' column exists, if not, create and set all to 0 (Scheduled)
        if 'Status' not in df_with_status.columns:
            df_with_status['Status'] = 0  # Default all statuses to 'Scheduled'

        # Convert Status column values to 'Scheduled' or 'Paid'
        df_with_status['Status'] = df_with_status['Status'].apply(lambda x: 'Scheduled' if x == 0 else 'Paid')

        # Remove 'Remaining Balance' column if it exists in the repayment table
        if 'Remaining Balance' in df_with_status.columns:
            df_with_status = df_with_status.drop(columns=['Remaining Balance'])

        # Remove 'Total' row if it exists
        if 'Total' in df_with_status['Payment Date'].values:
            df_with_status = df_with_status[df_with_status['Payment Date'] != 'Total']

        # Reorder the columns to have Status right next to the Payment Date column in the repayment table
        cols = df_with_status.columns.tolist()
        status_idx = cols.index('Payment Date') + 1
        cols.insert(status_idx, cols.pop(cols.index('Status')))
        df_with_status = df_with_status[cols]

        # Prepare the vertical header for both tables (without modifying Period)
        vertical_header = [str(i) for i in df['Period'].values]

        # Drop the Period column from the DataFrame before display
        df_loan_table = df.drop(columns=['Period'])
        df_with_status = df_with_status.drop(columns=['Period'])

        # Define a function to format numbers with commas
        def format_number(value):
            try:
                return "{:,}".format(int(value))
            except ValueError:
                return value

        # Apply formatting to all numerical columns
        for column in df_loan_table.columns:
            df_loan_table[column] = df_loan_table[column].apply(format_number)

        for column in df_with_status.columns:
            df_with_status[column] = df_with_status[column].apply(format_number)

        # Model for loanScheduleTable (without Status)
        model_loan_table = QStandardItemModel(df_loan_table.shape[0], df_loan_table.shape[1])
        model_loan_table.setHorizontalHeaderLabels(df_loan_table.columns.tolist())
        model_loan_table.setVerticalHeaderLabels(vertical_header)

        for row in range(df_loan_table.shape[0]):
            for col in range(df_loan_table.shape[1]):
                item = QStandardItem(df_loan_table.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model_loan_table.setItem(row, col, item)

        # Model for repaymentScheduleTable (with Status, no Remaining Balance and no Total row)
        model_repayment_table = QStandardItemModel(df_with_status.shape[0], df_with_status.shape[1])
        model_repayment_table.setHorizontalHeaderLabels(df_with_status.columns.tolist())
        model_repayment_table.setVerticalHeaderLabels(vertical_header)

        for row in range(df_with_status.shape[0]):
            for col in range(df_with_status.shape[1]):
                item = QStandardItem(df_with_status.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model_repayment_table.setItem(row, col, item)

        # Set the model for loanScheduleTable (without Status)
        self.loanScheduleTable.setModel(model_loan_table)
        self.loanScheduleTable.resizeColumnsToContents()

        # Set the model for repaymentScheduleTable (with Status, no Remaining Balance and no Total row)
        self.repaymentScheduleTable.setModel(model_repayment_table)
        self.repaymentScheduleTable.resizeColumnsToContents()

    def handle_table_click(self, index):
        if index.isValid():
            self.selected_row = index.row()
            model = index.model()
            status_value = model.data(model.index(self.selected_row, 1))

            if status_value == "Scheduled":
                self.paidButton.setEnabled(True)
            else:
                self.paidButton.setEnabled(False)

    def handle_received_table_click(self, index):
        if index.isValid():
            self.selected_received_row = index.row()
            self.deleteButton.setEnabled(True)
            self.receivedTable.selectRow(self.selected_received_row)

    def load_data_into_tables(self):
        if not self.existing_loan_id:
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        if loan_data and "loanSchedule" in loan_data:
            repayment_data = []
            received_data = []

            # Extract loan schedule and filter out Total row and remove "Remaining Balance" column
            for i, schedule in enumerate(loan_data["loanSchedule"]):
                # Exclude the last Total row by checking the index
                if i == len(loan_data["loanSchedule"]) - 1:
                    continue
                
                # Remove "Remaining Balance" from schedule if it exists
                schedule.pop("Remaining Balance", None)
                
                if schedule["status"] == 0:  # Scheduled
                    repayment_data.append(schedule)
                elif schedule["status"] == 1:  # Paid
                    received_data.append(schedule)

            # Clear the models before loading new data
            self.clear_table(self.repaymentScheduleTable)
            self.clear_table(self.receivedTable)

            # Load repayment data into repaymentScheduleTable (without the last row)
            if repayment_data:
                self.load_table(self.repaymentScheduleTable, repayment_data, status_included=True)

            # Load received data into receivedTable
            if received_data:
                self.load_table(self.receivedTable, received_data, status_included=True)

    def load_table(self, table, data, status_included=False):
        if not data:
            return

        # Define the correct column order excluding "Remaining Balance"
        column_order = ["Payment Date", "Status", "Principal", "Interest", "Total"]

        model = QStandardItemModel(len(data), len(column_order))
        model.setHorizontalHeaderLabels(column_order)

        for row_idx, row_data in enumerate(data):
            period_value = row_data.get("Period", 0)

            # Ensure period_value is an integer
            try:
                period_value = int(period_value)
            except ValueError:
                period_value = 0  # Handle case where Period might not be convertible

            row_idx = period_value - 1  # Adjust for zero-based index

            for col_idx, column in enumerate(column_order):
                value = row_data.get(column, "")

                # Handle Status column: if status_included is True and column is Status
                if column == "Status":
                    if status_included:
                        status_value = row_data.get("status", 0)
                        if status_value == 0:
                            value = "Scheduled"
                        elif status_value == 1:
                            value = "Paid"

                item = QStandardItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item non-editable
                model.setItem(row_idx, col_idx, item)

        table.setModel(model)
        table.resizeColumnsToContents()

    def clear_table(self, table):
        model = QStandardItemModel(0, 0)  # Empty model to clear the table
        table.setModel(model)

    def on_paid_button_clicked(self):
        if self.selected_row is not None and self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "loanSchedule" in loan_data:
                loan_schedule = loan_data["loanSchedule"]

                period_value = self.selected_row + 1

                for schedule in loan_schedule:
                    try:
                        schedule_period = int(schedule.get("Period", 0))
                    except ValueError:
                        schedule_period = 0

                    if schedule_period == period_value:
                        schedule["status"] = 1

                loan_ref.update({"loanSchedule": loan_schedule})
                self.load_data_into_tables()

    def on_delete_button_clicked(self):
        if self.selected_received_row is not None and self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "loanSchedule" in loan_data:
                loan_schedule = loan_data["loanSchedule"]

                # Get the Period value of the selected row from receivedTable
                period_value = self.selected_received_row + 1

                for schedule in loan_schedule:
                    try:
                        schedule_period = int(schedule.get("Period", 1))
                    except ValueError:
                        schedule_period = 1

                    if schedule_period == period_value:
                        schedule["status"] = 0  # Update status to 'Scheduled'

                # Update the loan document in Firestore
                loan_ref.update({"loanSchedule": loan_schedule})

                # Reload the tables to reflect changes
                self.load_data_into_tables()

                # Reset the selected row and disable the delete button after action
                self.selected_received_row = None
                self.deleteButton.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = LoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
