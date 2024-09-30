import sys
import os
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QAbstractItemView, QMessageBox, QTableView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon

from src.components import DB  # Firestore 연결을 위한 모듈
from src.components.select_loan import SelectLoanWindow


class RepaymentSingleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "single.ui")
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Initialize buttons and labels
        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.overdueButton.setEnabled(False)

        # Connect buttons
        self.searchButton.clicked.connect(self.on_search_button_clicked)

        self.setup_table_selection()  # Setup table selection for repayment/received tables
        self.paidButton.clicked.connect(self.on_paid_button_clicked)
        self.deleteButton.clicked.connect(self.on_delete_button_clicked)
        self.overdueButton.clicked.connect(self.on_overdue_button_clicked)  # Connect overdueButton

        # Set tables to read-only mode
        self.set_tables_read_only()

    def set_tables_read_only(self):
        """Set all tables to read-only mode."""
        tables = [self.repaymentScheduleTable, self.receivedTable, self.guarantorTable, self.collateralTable,
                  self.counselingTable]
        for table in tables:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setup_table_selection(self):
        """Handle row selections for repayment and received tables."""
        self.repaymentScheduleTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.repaymentScheduleTable.setSelectionMode(QTableView.SingleSelection)
        self.repaymentScheduleTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.receivedTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.receivedTable.setSelectionMode(QTableView.SingleSelection)
        self.receivedTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Handle table row click events
        self.repaymentScheduleTable.clicked.connect(self.handle_repayment_schedule_table_click)
        self.receivedTable.clicked.connect(self.handle_received_table_click)

    def handle_repayment_schedule_table_click(self, index):
        """Handle button enabling/disabling based on the selected row's status in the repayment schedule table."""
        # Clear the selection in the received table
        self.receivedTable.clearSelection()

        # Disable all buttons initially
        self.paidButton.setEnabled(False)
        self.overdueButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        # Get the selected row data
        model = self.repaymentScheduleTable.model()
        selected_row = index.row()
        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        # Enable/disable buttons based on status
        status = self.selected_schedule_data["Status"]
        if status == "Paid":
            self.deleteButton.setEnabled(True)  # Only delete button enabled for Paid status
        elif status == "Scheduled":
            self.paidButton.setEnabled(True)
            self.overdueButton.setEnabled(True)  # Overdue and Paid buttons enabled for Scheduled
        elif status == "Overdue":
            self.paidButton.setEnabled(True)  # Only Paid button enabled for Overdue

    def handle_received_table_click(self, index):
        """Handle button enabling/disabling based on the selected row's status in the received table."""
        # Clear the selection in the repayment schedule table
        self.repaymentScheduleTable.clearSelection()

        # Disable all buttons initially
        self.paidButton.setEnabled(False)
        self.overdueButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        # Get the selected row data
        model = self.receivedTable.model()
        selected_row = index.row()
        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        # Enable delete button only for Paid rows in the received table
        if self.selected_schedule_data["Status"] == "Paid":
            self.deleteButton.setEnabled(True)

    def on_paid_button_clicked(self):
        """Mark the selected repayment schedule as paid and move it to the received table."""
        selected_schedule = self.selected_schedule_data
        if not selected_schedule:
            QMessageBox.warning(self, "Error", "No repayment schedule selected.")
            return

        payment_date = selected_schedule.get("Payment Date")

        try:
            loan_schedule = self.loan_data.get("loan_schedule", [])
            for schedule in loan_schedule:
                if schedule.get("Payment Date") == payment_date:
                    schedule["status"] = 1  # Mark as 'Paid'

            loan_id = self.loan_data.get("loan_id")
            DB.collection("Loan").document(loan_id).update({"loan_schedule": loan_schedule})

            QMessageBox.information(self, "Success", f"Payment for {payment_date} marked as paid.")

            # Remove the paid row from the repayment schedule table and update its status
            self.update_table_row_status(self.repaymentScheduleTable, payment_date, "Paid", QColor(Qt.black))

            # Move to the received table
            self.move_row_to_received_table(payment_date)

            # Recalculate totals
            self.calculate_totals()

            self.paidButton.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def move_row_to_received_table(self, payment_date):
        """Move the row from the repaymentScheduleTable to the receivedTable when marked as paid."""
        model = self.repaymentScheduleTable.model()
        row_count = model.rowCount()

        for row in range(row_count):
            if model.item(row, 0).text() == payment_date:
                # Collect data from the row
                row_data = [
                    model.item(row, col).text() for col in range(model.columnCount())
                ]
                # Remove from repayment schedule table
                model.removeRow(row)

                # Add to received table
                self.add_row_to_received_table(row_data)
                break

    def add_row_to_received_table(self, row_data):
        """Add the row data to the received table."""
        model = self.receivedTable.model()
        row_idx = model.rowCount()
        model.insertRow(row_idx)

        for col_idx, value in enumerate(row_data):
            item = self.create_read_only_item(value)
            model.setItem(row_idx, col_idx, item)

    def on_delete_button_clicked(self):
        """Revert the selected row to 'Scheduled' and move it back to the repayment schedule table."""
        if not self.selected_schedule_data:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record.")
            return

        payment_date = self.selected_schedule_data["Payment Date"]

        try:
            loan_schedule = self.loan_data.get("loan_schedule", [])
            for schedule in loan_schedule:
                if schedule.get("Payment Date") == payment_date:
                    schedule['status'] = 0  # Revert to 'Scheduled'

            loan_id = self.loan_data['loan_id']
            DB.collection("Loan").document(loan_id).update({"loan_schedule": loan_schedule})

            QMessageBox.information(self, "Success", f"Payment for {payment_date} reverted to Scheduled.")

            # Remove the row from the received table and move it back to the repayment schedule table
            self.move_row_to_repayment_schedule_table(payment_date)

            # Recalculate totals
            self.calculate_totals()

            self.deleteButton.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def move_row_to_repayment_schedule_table(self, payment_date):
        """Move the row from the receivedTable back to the repaymentScheduleTable and set status to 'Scheduled'."""
        model = self.receivedTable.model()
        row_count = model.rowCount()

        for row in range(row_count):
            if model.item(row, 0).text() == payment_date:
                # Collect data from the row
                row_data = [
                    model.item(row, col).text() for col in range(model.columnCount())
                ]
                # Remove from received table
                model.removeRow(row)

                # Set status to 'Scheduled' and add back to repayment schedule table
                row_data[4] = "Scheduled"  # Update status to 'Scheduled'
                self.add_row_to_repayment_schedule_table(row_data)
                break

    def add_row_to_repayment_schedule_table(self, row_data):
        """Add the row data back to the repayment schedule table."""
        model = self.repaymentScheduleTable.model()
        row_idx = model.rowCount()
        model.insertRow(row_idx)

        for col_idx, value in enumerate(row_data):
            item = self.create_read_only_item(value)
            model.setItem(row_idx, col_idx, item)

    def on_overdue_button_clicked(self):
        """Mark the selected repayment schedule as overdue without moving it to another table."""
        selected_schedule = self.selected_schedule_data
        if not selected_schedule:
            QMessageBox.warning(self, "Error", "No repayment schedule selected.")
            return

        payment_date = selected_schedule.get("Payment Date")

        try:
            loan_schedule = self.loan_data.get("loan_schedule", [])
            for schedule in loan_schedule:
                if schedule.get("Payment Date") == payment_date:
                    schedule["status"] = 2  # Mark as 'Overdue'

            loan_id = self.loan_data.get("loan_id")
            DB.collection("Loan").document(loan_id).update({"loan_schedule": loan_schedule})

            QMessageBox.information(self, "Success", f"Payment for {payment_date} marked as overdue.")

            # Update the status in the table directly
            self.update_table_row_status(self.repaymentScheduleTable, payment_date, "Overdue", QColor(Qt.red))

            self.overdueButton.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def update_table_row_status(self, table_view, payment_date, new_status, color):
        """Update the row status and apply color to the row for overdue status."""
        model = table_view.model()
        row_count = model.rowCount()

        for row in range(row_count):
            # Find the matching payment date row
            if model.item(row, 0).text() == payment_date:
                # Update the status
                status_item = self.create_read_only_item(new_status)
                status_item.setForeground(color)
                model.setItem(row, 4, status_item)  # Assuming status is in the 5th column (index 4)

                # Update the color of the entire row to reflect the new status
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    if item:
                        item.setForeground(color)
                break
    def on_search_button_clicked(self):
        """Open the customer selection dialog and handle the loan selection."""
        self.select_loan_window = SelectLoanWindow()
        self.select_loan_window.loan_selected.connect(self.handle_loan_selected)
        self.select_loan_window.exec_()

    def handle_loan_selected(self, selected_data):
        """Load loan and customer details once a loan is selected."""
        loan_ref = DB.collection('Loan')
        loan_id = selected_data['loan_id']
        loan_doc = loan_ref.document(loan_id).get()
        loan_data = loan_doc.to_dict()
        self.loan_data = loan_data
        # Get customer name from the loan data and search for customer in the Customer DB
        customer_name = selected_data['customer_name']

        # Fetch customer data based on the customer_name from 'Customer' collection
        customer_ref = DB.collection('Customer')
        customer_query = customer_ref.where('name', '==', customer_name).get()

        if customer_query:
            customer_data = customer_query[0].to_dict()  # Fetch the first matching customer document

            # Set customer information in the UI
            self.customerName.setText(customer_data.get('name', 'Unknown'))
            self.contact.setText('-'.join([
                customer_data.get('tel1ByOne', ''),
                customer_data.get('tel1ByTwo', ''),
                customer_data.get('tel1ByThree', '')
            ]))
            self.loan_data['customer_name'] = customer_data.get('name', 'Unknown')
        else:
            QMessageBox.warning(self, "Error", "Customer not found.")

        self.loanNumber.setText(loan_data['loan_number'])
        self.contractDate.setText(loan_data['contract_date'])
        self.loanStatus.setText(loan_data['loan_status'])
        self.loanType.setText(loan_data['loan_type'])
        officer_data = DB.collection('Officer').document(loan_data['loan_officer']).get().to_dict()
        self.loan_data['officer_name'] = officer_data['name']
        self.loanOfficer.setText(officer_data['name'])
        self.cpNumber.setText(loan_data['cp_number'])

        self.loanAmount.setText(loan_data['principal'])
        self.repaymentCycle.setText(loan_data['repayment_cycle'])
        self.interestRate.setText(loan_data['interest_rate'])
        self.numberOfRepayment.setText(loan_data['number_of_repayment'])
        self.repaymentMethod.setText(loan_data['repayment_method'])

        if 'loan_schedule' in loan_data:
            schedule_data = loan_data['loan_schedule']
            columns = ["Payment Date", "Principal", "Interest", "Total", "Status"]

            # Separate scheduled and received payments
            repayment_data = [item for item in schedule_data if item.get('status') in [0, 2]]  # Scheduled and Overdue
            received_data = [item for item in schedule_data if item.get('status') == 1]  # Only Paid

            # Load the tables
            self.load_table(self.repaymentScheduleTable, repayment_data, columns, is_scheduled=True)
            self.load_table(self.receivedTable, received_data, columns, is_scheduled=False)

        self.load_collateral_data(loan_data)
        self.load_counseling_data(loan_data)
        self.load_guarantor_data(loan_data)

    def load_table(self, table_view, data, columns, is_scheduled=True):
        """Load repayment schedule and received data into the respective tables."""
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        status_mapping = {0: 'Scheduled', 1: 'Paid', 2: 'Overdue'}
        total_sum = 0

        for row_idx, item in enumerate(data):
            status = item.get("status", 0)
            is_overdue = status == 2

            for col_idx, column_name in enumerate(columns):
                item_value = item.get(column_name, "")

                if column_name in ["Principal", "Interest", "Total"] and item_value != "":
                    item_value = "{:,}".format(int(float(item_value)))
                    if column_name == "Total":
                        total_sum += int(item.get(column_name, 0))

                item_value_obj = self.create_read_only_item(item_value)

                if is_overdue:
                    item_value_obj.setForeground(QColor(Qt.red))

                model.setItem(row_idx, col_idx, item_value_obj)

            status_text = status_mapping.get(status, 'Unknown')
            status_item = self.create_read_only_item(status_text)

            if is_overdue:
                status_item.setForeground(QColor(Qt.red))

            model.setItem(row_idx, 4, status_item)

        table_view.setModel(model)
        table_view.resizeColumnsToContents()

        # Display total sum
        total_sum_formatted = "{:,.0f}".format(total_sum)
        if is_scheduled:
            self.totalScheduled.setText(f"{total_sum_formatted}")
        else:
            self.totalReceived.setText(f"{total_sum_formatted}")

    def load_loan_schedule(self, loan_data):
        """Load the loan schedule data, preserving Overdue rows."""
        if 'loan_schedule' in loan_data:
            schedule_data = loan_data['loan_schedule']
            columns = ["Payment Date", "Principal", "Interest", "Total", "Status"]

            # Separate scheduled and received payments
            repayment_data = [item for item in schedule_data if item.get('status') in [0, 2]]  # Scheduled and Overdue
            received_data = [item for item in schedule_data if item.get('status') == 1]  # Paid

            # Load the tables
            self.load_table(self.repaymentScheduleTable, repayment_data, columns, is_scheduled=True)
            self.load_table(self.receivedTable, received_data, columns, is_scheduled=False)

    def calculate_totals(self):
        """Recalculate and update the total amounts for both scheduled and received tables."""
        total_scheduled = 0
        total_received = 0

        # Calculate the total for the repayment schedule table
        model = self.repaymentScheduleTable.model()
        for row in range(model.rowCount()):
            total_value = model.item(row, 3).text().replace(',', '')  # Get the 'Total' column value
            total_scheduled += float(total_value)

        # Calculate the total for the received table
        model = self.receivedTable.model()
        for row in range(model.rowCount()):
            total_value = model.item(row, 3).text().replace(',', '')  # Get the 'Total' column value
            total_received += float(total_value)

        # Update the labels
        self.totalScheduled.setText(f"{total_scheduled:,.0f}")
        self.totalReceived.setText(f"{total_received:,.0f}")

    def load_guarantor_data(self, loan_data):
        if 'guarantors' in loan_data:
            guarantor_uids = loan_data['guarantors']
            model = QStandardItemModel(len(guarantor_uids), 3)
            model.setHorizontalHeaderLabels(["Name", "Date of Birth", "Contact"])

            for row_idx, guarantor_uid in enumerate(guarantor_uids):
                try:
                    guarantor_doc = DB.collection('Guarantor').document(guarantor_uid).get()
                    if guarantor_doc.exists:
                        guarantor_data = guarantor_doc.to_dict()
                        model.setItem(row_idx, 0, QStandardItem(guarantor_data.get("name", "Unknown")))
                        model.setItem(row_idx, 1, QStandardItem(guarantor_data.get("date_of_birth", "Unknown")))
                        model.setItem(row_idx, 2, QStandardItem('-'.join(
                            [guarantor_data.get('tel1ByOne', ''), guarantor_data.get('tel1ByTwo', ''),
                             guarantor_data.get('tel1ByThree', '')])))
                    else:
                        model.setItem(row_idx, 0, QStandardItem("Unknown"))
                        model.setItem(row_idx, 1, QStandardItem("Unknown"))
                        model.setItem(row_idx, 2, QStandardItem("Unknown"))
                except Exception as e:
                    model.setItem(row_idx, 0, QStandardItem(f"Error loading guarantor: {e}"))
                    model.setItem(row_idx, 1, QStandardItem("Error"))
                    model.setItem(row_idx, 2, QStandardItem("Error"))

            self.guarantorTable.setModel(model)
            self.guarantorTable.resizeColumnsToContents()

    def load_collateral_data(self, loan_data):
        if 'collaterals' in loan_data:
            columns = ["Type", "Name", "Details"]
            model = QStandardItemModel(len(loan_data['collaterals']), len(columns))
            model.setHorizontalHeaderLabels(columns)

            for row_idx, collateral in enumerate(loan_data['collaterals']):
                model.setItem(row_idx, 0, self.create_read_only_item(collateral.get("type", "")))
                model.setItem(row_idx, 1, self.create_read_only_item(collateral.get("name", "")))
                model.setItem(row_idx, 2, self.create_read_only_item(collateral.get("details", "")))

            self.collateralTable.setModel(model)
            self.collateralTable.resizeColumnsToContents()

    def load_counseling_data(self, loan_data):
        if 'counselings' in loan_data:
            columns = ["Date", "Subject", "Details", "Corrective Measure"]
            model = QStandardItemModel(len(loan_data['counselings']), len(columns))
            model.setHorizontalHeaderLabels(columns)

            for row_idx, counseling in enumerate(loan_data['counselings']):
                model.setItem(row_idx, 0, self.create_read_only_item(counseling.get("date", "")))
                model.setItem(row_idx, 1, self.create_read_only_item(counseling.get("subject", "")))
                model.setItem(row_idx, 2, self.create_read_only_item(counseling.get("details", "")))
                model.setItem(row_idx, 3, self.create_read_only_item(counseling.get("corrective_measure", "")))

            self.counselingTable.setModel(model)
            self.counselingTable.resizeColumnsToContents()


    def create_read_only_item(self, text):
        """Create a read-only QStandardItem."""
        item = QStandardItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def show_message(self, title, message):
        """Show a message box with the given title and message."""
        QMessageBox.warning(self, title, message)


def main():
    app = QApplication(sys.argv)
    window = RepaymentSingleApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
