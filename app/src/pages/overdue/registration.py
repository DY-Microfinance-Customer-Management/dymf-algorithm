import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIntValidator, QIcon, QColor

from src.components import DB
from src.components.select_loan import SelectLoanWindow

class OverdueRegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Connect the search button to the method to show SelectLoanWindow
        self.searchButton.clicked.connect(self.open_select_loan_window)

    def open_select_loan_window(self):
        # Create an instance of SelectLoanWindow
        self.select_loan_window = SelectLoanWindow()

        # Connect the loan_selected signal to a handler method
        self.select_loan_window.loan_selected.connect(self.handle_loan_selected)

        # Show the SelectLoanWindow dialog
        self.select_loan_window.exec_()

    def handle_loan_selected(self, selected_data):
        loan_ref = DB.collection('Loan')
        loan_id = selected_data['loan_id']
        loan_doc = loan_ref.document(loan_id).get()
        loan_data = loan_doc.to_dict()
    
        self.customerLoanNumber.setText(loan_data['loan_number'])
        self.customerName.setText(selected_data['customer_name'])

        self.loanNumber.setText(loan_data['loan_number'])
        self.contractDate.setText(loan_data['contract_date'])
        self.loanStatus.setText(loan_data['loan_status'])
        self.loanType.setText(loan_data['loan_type'])
        officer_data = DB.collection('Officer').document(loan_data['loan_officer']).get().to_dict()
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
            repayment_data = [item for item in schedule_data if item.get('status') == 0]  # Scheduled payments
            received_data = [item for item in schedule_data if item.get('status') in [1, 2]]  # Paid or Overdue

            # Load the tables and pass the appropriate flag for totals
            self.load_table(self.repaymentScheduleTable, repayment_data, columns, is_scheduled=True)
            self.load_table(self.receivedTable, received_data, columns, is_scheduled=False)

        if 'guarantors' in loan_data:
            guarantor_uids = loan_data['guarantors']  # List of UID values
            model = QStandardItemModel(len(guarantor_uids), 3)
            model.setHorizontalHeaderLabels(["Name", "Date of Birth", "Contact"])

            # Loop through each guarantor UID and fetch the details from the Guarantor collection
            for row_idx, guarantor_uid in enumerate(guarantor_uids):
                try:
                    # Fetch guarantor details using the UID from the 'Guarantor' collection
                    guarantor_doc = DB.collection('Guarantor').document(guarantor_uid).get()
                    if guarantor_doc.exists:
                        guarantor_data = guarantor_doc.to_dict()

                        # Populate the table with the fetched guarantor information
                        model.setItem(row_idx, 0, QStandardItem(guarantor_data.get("name", "Unknown")))
                        model.setItem(row_idx, 1, QStandardItem(guarantor_data.get("date_of_birth", "Unknown")))
                        model.setItem(row_idx, 2, QStandardItem('-'.join([guarantor_data.get('tel1ByOne', ''), guarantor_data.get('tel1ByTwo', ''), guarantor_data.get('tel1ByThree', '')])))
                    else:
                        # Handle the case where the document does not exist
                        model.setItem(row_idx, 0, QStandardItem("Unknown"))
                        model.setItem(row_idx, 1, QStandardItem("Unknown"))
                        model.setItem(row_idx, 2, QStandardItem("Unknown"))

                except Exception as e:
                    # Handle any exceptions while fetching the guarantor data
                    model.setItem(row_idx, 0, QStandardItem(f"Error loading guarantor: {e}"))
                    model.setItem(row_idx, 1, QStandardItem("Error"))
                    model.setItem(row_idx, 2, QStandardItem("Error"))

            # Set the model to the table
            self.guarantorTable.setModel(model)
            self.guarantorTable.resizeColumnsToContents()

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

    def load_table(self, table_view, data, columns, is_scheduled=True):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        status_mapping = {0: 'Scheduled', 1: 'Paid', 2: 'Overdue'}
        total_sum = 0  # Initialize sum of the "Total" column

        for row_idx, item in enumerate(data):
            is_overdue = item.get("status") == 2
            
            for col_idx, column_name in enumerate(columns):
                item_value = item.get(column_name, "")

                # If the column is "Principal", "Interest", or "Total", format the number
                if column_name in ["Principal", "Interest", "Total"] and item_value != "":
                    item_value = "{:,}".format(int(float(item_value)))  # Add commas without decimals
                    if column_name == "Total":  # If we're in the "Total" column, accumulate the sum
                        total_sum += float(item.get(column_name, 0))

                item_value_obj = self.create_read_only_item(item_value)

                if is_overdue:
                    item_value_obj.setForeground(QColor(Qt.red))

                model.setItem(row_idx, col_idx, item_value_obj)

            # Handle status column
            status = item.get("status", 0)
            status_text = status_mapping.get(status, 'Unknown')
            status_item = self.create_read_only_item(status_text)

            if is_overdue:
                status_item.setForeground(QColor(Qt.red))

            model.setItem(row_idx, 4, status_item)

        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def create_read_only_item(self, text):
        item = QStandardItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverdueRegistrationApp()
    window.show()
    sys.exit(app.exec_())