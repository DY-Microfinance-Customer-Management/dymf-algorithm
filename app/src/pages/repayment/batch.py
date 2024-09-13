import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QIcon
from PyQt5.QtCore import Qt, QDate
from PyQt5 import uic, QtCore

from src.components import DB  # Firestore DB를 사용한다고 가정
from src.pages.repayment.details import RepaymentDetailsWindow

class RepaymentBatchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "batch.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.show()
        self.setup_connections()
        self.setup_table()
        self.set_default_dates()
        self.paidButton.setEnabled(False)
        self.cancelPaymentButton.setEnabled(False)
        self.details_window = None

    def setup_connections(self):
        self.searchButton.clicked.connect(self.on_search_clicked)
        self.paidButton.clicked.connect(self.on_paid_clicked)
        self.cancelPaymentButton.clicked.connect(self.on_cancel_payment_clicked)
        self.detailsButton.clicked.connect(self.on_details_button_clicked)
        self.toExcelButton.clicked.connect(self.export_to_excel)
        self.repaymentScheduleTable.clicked.connect(self.on_table_clicked)

    def setup_table(self):
        model = QStandardItemModel(0, 6)
        model.setHorizontalHeaderLabels(["uid", "Date", "Customer", "Principal", "Interest", "Total", "Status"])
        self.repaymentScheduleTable.setModel(model)
        self.repaymentScheduleTable.setSelectionBehavior(self.repaymentScheduleTable.SelectRows)

    def set_default_dates(self):
        today = QDate.currentDate()
        self.startDate.setDate(today)
        self.endDate.setDate(today)
        
    def on_search_clicked(self):
        start_date = self.startDate.date().toString("yyyy-MM-dd")
        end_date = self.endDate.date().toString("yyyy-MM-dd")
        schedules_to_add = []  # 스케줄 데이터를 담을 리스트

        try:
            loans_ref = DB.collection('Loan')
            loans = loans_ref.stream()

            self.repaymentScheduleTable.model().removeRows(0, self.repaymentScheduleTable.model().rowCount())

            for loan_doc in loans:
                loan_data = loan_doc.to_dict()
                loan_schedule = loan_data.get("loan_schedule", [])
                customer_uid = loan_data.get('uid')  # Get customer UID from the loan

                # Get the customer name from the Customer collection using the UID
                customer_doc = DB.collection('Customer').document(customer_uid).get()
                customer_name = customer_doc.to_dict().get('name', '') if customer_doc.exists else 'Unknown'

                for schedule in loan_schedule:
                    payment_date = schedule.get("Payment Date", "")
                    if start_date <= payment_date <= end_date:
                        schedules_to_add.append((schedule, customer_uid, customer_name))  # Add schedule with customer name and uid

            # Payment Date 기준으로 스케줄 정렬
            schedules_to_add.sort(key=lambda x: x[0].get("Payment Date", ""))

            # 정렬된 스케줄 데이터를 테이블에 추가
            for schedule, customer_uid, customer_name in schedules_to_add:
                self.add_schedule_to_table(schedule, customer_uid, customer_name)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load repayment schedules: {e}")

    def add_schedule_to_table(self, schedule, customer_uid, customer_name):
        model = self.repaymentScheduleTable.model()

        principal = "{:,}".format(schedule.get("Principal", 0))
        interest = "{:,}".format(schedule.get("Interest", 0))
        total = "{:,}".format(schedule.get("Total", 0))

        status_code = schedule.get("status", "")
        if status_code == 0:
            status_text = "Scheduled"
        elif status_code == 1:
            status_text = "Paid"
        elif status_code == 2:
            status_text = "Overdue"
        else:
            status_text = ""

        # Add items to the row (including hidden uid)
        items = [
            QStandardItem(customer_uid),  # Hidden column to store UID
            QStandardItem(schedule.get("Payment Date", "")),
            QStandardItem(customer_name),  # Visible column with customer name
            QStandardItem(principal),
            QStandardItem(interest),
            QStandardItem(total),
            QStandardItem(status_text),
        ]

        if status_text == "Overdue":
            for item in items:
                item.setForeground(QBrush(Qt.red))

        for item in items:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

        model.appendRow(items)

        # Hide the UID column (which is the first column)
        self.repaymentScheduleTable.setColumnHidden(0, True)

    def on_table_clicked(self, index):
        if index.isValid():
            selected_row = index.row()
            model = self.repaymentScheduleTable.model()

            status = model.index(selected_row, 6).data()

            if status == "Scheduled":
                self.paidButton.setEnabled(True)
                self.cancelPaymentButton.setEnabled(False)
            elif status == "Paid":
                self.paidButton.setEnabled(False)
                self.cancelPaymentButton.setEnabled(True)
            else:
                self.paidButton.setEnabled(False)
                self.cancelPaymentButton.setEnabled(False)

    def on_paid_clicked(self):
        selected_indexes = self.repaymentScheduleTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record to mark as paid.")
            return

        selected_row = selected_indexes[0].row()
        model = self.repaymentScheduleTable.model()

        customer_uid = model.index(selected_row, 0).data()
        payment_date = model.index(selected_row, 1).data()

        try:
            loans_ref = DB.collection('Loan').where('uid', '==', customer_uid).get()

            if loans_ref:
                loan_doc = loans_ref[0]
                loan_data = loan_doc.to_dict()
                loan_schedule = loan_data.get("loan_schedule", [])

                for schedule in loan_schedule:
                    if schedule.get("Payment Date") == payment_date:
                        schedule['status'] = 1

                DB.collection('Loan').document(loan_doc.id).update({"loan_schedule": loan_schedule})

                QMessageBox.information(self, "Success", f"Payment for {payment_date} marked as paid.")
                self.on_search_clicked()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def on_cancel_payment_clicked(self):
        selected_indexes = self.repaymentScheduleTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record to cancel.")
            return

        selected_row = selected_indexes[0].row()
        model = self.repaymentScheduleTable.model()

        customer_uid = model.index(selected_row, 0).data()
        payment_date = model.index(selected_row, 1).data()

        try:
            loans_ref = DB.collection('Loan').where('uid', '==', customer_uid).get()

            if loans_ref:
                loan_doc = loans_ref[0]
                loan_data = loan_doc.to_dict()
                loan_schedule = loan_data.get("loan_schedule", [])

                for schedule in loan_schedule:
                    if schedule.get("Payment Date") == payment_date:
                        schedule['status'] = 0  # 상태를 0으로 변경

                DB.collection('Loan').document(loan_doc.id).update({"loan_schedule": loan_schedule})

                QMessageBox.information(self, "Success", f"Payment for {payment_date} has been canceled.")
                self.on_search_clicked()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def on_details_button_clicked(self):
        selected_indexes = self.repaymentScheduleTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record.")
            return

        selected_row = selected_indexes[0].row()
        model = self.repaymentScheduleTable.model()

        # Get the customer UID from the hidden column (first column)
        customer_uid = model.index(selected_row, 0).data()

        try:
            # Fetch the loan details using the UID
            loans_ref = DB.collection('Loan').where('uid', '==', customer_uid).get()

            if loans_ref:
                loan_doc = loans_ref[0]
                loan_data = loan_doc.to_dict()

                # Fetch customer details using the UID from the Customer collection
                customer_doc = DB.collection('Customer').document(customer_uid).get()
                customer_data = customer_doc.to_dict() if customer_doc.exists else {}

                self.details_window = RepaymentDetailsWindow(loan_data, customer_data)
                self.details_window.show()

            else:
                QMessageBox.warning(self, "No Data", "No loan details found for the selected customer.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load loan details: {e}")

    def export_to_excel(self):
        QMessageBox.information(self, "Export to Excel", "Repayment data will be exported to Excel.")

def main():
    app = QApplication(sys.argv)
    window = RepaymentBatchApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
