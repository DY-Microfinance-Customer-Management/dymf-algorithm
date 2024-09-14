import os, sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableView, QAbstractItemView, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon

from src.components import DB
from src.components.select_customer import SelectCustomerWindow

class RepaymentSingleApp(QMainWindow):
    def __init__(self, loan_data, customer_data):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "details.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.loan_data = loan_data
        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        self.init_loan_data(loan_data)
        self.init_customer_data(customer_data)
        self.setup_table_selection()
        self.setup_connections()
        self.show()

    def init_customer_data(self, customer_data):
        self.customerName.setText(customer_data['name'])
        self.contact.setText('-'.join([customer_data['tel1ByOne'], customer_data['tel1ByTwo'], customer_data['tel1ByThree']]))

    def init_loan_data(self, loan_data):
        self.load_loan_info(loan_data)
        self.load_loan_schedule(loan_data)
        self.load_guarantor_data(loan_data)
        self.load_collateral_data(loan_data)
        self.load_counseling_data(loan_data)

    def setup_connections(self):
        self.paidButton.clicked.connect(self.on_paid_button_clicked)
        self.deleteButton.clicked.connect(self.on_delete_button_clicked)

    def setup_table_selection(self):
        self.repaymentScheduleTable.setSelectionBehavior(QTableView.SelectRows)
        self.repaymentScheduleTable.setSelectionMode(QTableView.SingleSelection)
        self.repaymentScheduleTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.receivedTable.setSelectionBehavior(QTableView.SelectRows)
        self.receivedTable.setSelectionMode(QTableView.SingleSelection)
        self.receivedTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 테이블 클릭 이벤트 연결
        self.repaymentScheduleTable.clicked.connect(self.handle_repayment_schedule_table_click)
        self.receivedTable.clicked.connect(self.handle_received_table_click)

    def handle_repayment_schedule_table_click(self, index):
        self.receivedTable.clearSelection()
        model = self.repaymentScheduleTable.model()
        selected_row = index.row()

        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        self.paidButton.setEnabled(self.selected_schedule_data["Status"] == "Scheduled")

    def handle_received_table_click(self, index):
        self.repaymentScheduleTable.clearSelection()
        model = self.receivedTable.model()
        selected_row = index.row()

        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        self.deleteButton.setEnabled(self.selected_schedule_data["Status"] == "Paid")

    def on_paid_button_clicked(self):
        selected_schedule = self.selected_schedule_data
        if not selected_schedule:
            QMessageBox.warning(self, "Error", "No repayment schedule selected.")
            return

        payment_date = selected_schedule.get("Payment Date")

        try:
            loan_schedule = self.loan_data.get("loan_schedule", [])
            for schedule in loan_schedule:
                if schedule.get("Payment Date") == payment_date:
                    schedule["status"] = 1

            loan_id = self.loan_data.get("loan_id")
            DB.collection("Loan").document(loan_id).update({"loan_schedule": loan_schedule})

            QMessageBox.information(self, "Success", f"Payment for {payment_date} marked as paid.")
            self.load_loan_schedule(self.loan_data)
            self.paidButton.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def on_delete_button_clicked(self):
        if not self.selected_schedule_data:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record.")
            return

        payment_date = self.selected_schedule_data["Payment Date"]

        try:
            loan_schedule = self.loan_data.get("loan_schedule", [])
            for schedule in self.loan_data['loan_schedule']:
                if schedule.get("Payment Date") == payment_date:
                    schedule['status'] = 0

            loan_id = self.loan_data['loan_id']
            DB.collection("Loan").document(loan_id).update({"loan_schedule": loan_schedule})

            QMessageBox.information(self, "Success", "Payment for {payment_date} marked as Scheduled.")
            self.load_loan_schedule(self.loan_data)
            self.deleteButton.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def load_guarantor_data(self, loan_data):
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

    def load_loan_schedule(self, loan_data):
        if 'loan_schedule' in loan_data:
            schedule_data = loan_data['loan_schedule']
            columns = ["Payment Date", "Principal", "Interest", "Total", "Status"]

            # Separate scheduled and received payments
            repayment_data = [item for item in schedule_data if item.get('status') == 0]  # Scheduled payments
            received_data = [item for item in schedule_data if item.get('status') in [1, 2]]  # Paid or Overdue

            # Load the tables and pass the appropriate flag for totals
            self.load_table(self.repaymentScheduleTable, repayment_data, columns, is_scheduled=True)
            self.load_table(self.receivedTable, received_data, columns, is_scheduled=False)

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

        # Set the total sum to the appropriate label
        total_sum_formatted = "{:,.0f}".format(total_sum)  # Format with commas, no decimals
        if is_scheduled:
            self.totalScheduled.setText(total_sum_formatted)
        else:
            self.totalReceived.setText(total_sum_formatted)

    def load_loan_info(self, loan_data):
        self.loanNumber.setText(loan_data['loan_number'])
        self.contractDate.setText(loan_data['contract_date'])
        self.loanStatus.setText(loan_data['loan_status'])
        self.loanType.setText(loan_data['loan_type'])
        officer = DB.collection('Officer').document(loan_data['loan_officer']).get().to_dict()
        self.loanOfficer.setText(officer['name'])
        self.cpNumber.setText(loan_data['cp_number'])
        self.loanAmount.setText(loan_data['principal'])
        self.repaymentCycle.setText(loan_data['repayment_cycle'])
        self.interestRate.setText(loan_data['interest_rate'])
        self.numberOfRepayment.setText(loan_data['number_of_repayment'])
        self.repaymentMethod.setText(loan_data['repayment_method'])

    def create_read_only_item(self, text):
        item = QStandardItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item


def main():
    app = QApplication(sys.argv)

    # DB에서 실제 loan_data와 customer_data를 가져와야 합니다.
    # loan_data와 customer_data는 해당 앱의 초기화 시 필요한 데이터입니다.
    # 이 부분은 실제 환경에서 데이터베이스에서 가져와야 합니다.
    loan_data = {}  # 실제 loan 데이터를 가져와야 함
    customer_data = {}  # 실제 고객 데이터를 가져와야 함

    if not loan_data or not customer_data:
        print("Loan data or customer data not provided.")
        sys.exit(1)

    # 앱 초기화 및 실행
    window = RepaymentSingleApp(loan_data, customer_data)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()