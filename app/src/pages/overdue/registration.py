import sys
import os
from datetime import datetime
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
        self.loan_data = None

        self.searchButton.clicked.connect(self.open_select_loan_window)
        self.markAsOverdueButton.clicked.connect(self.on_mark_as_overdue_button_clicked)

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
        self.loan_data = loan_data
    
        self.customerLoanNumber.setText(loan_data['loan_number'])
        self.customerName.setText(selected_data['customer_name'])
        self.loan_data['customer_name'] = selected_data['customer_name']

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
            repayment_data = [item for item in schedule_data if item.get('status') in [0, 2]]  # Scheduled and Overdue payments
            received_data = [item for item in schedule_data if item.get('status') == 1]  # Only Paid payments

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
                    guarantor_doc = DB.collection('Guarantor').document(guarantor_uid).get()
                    if guarantor_doc.exists:
                        guarantor_data = guarantor_doc.to_dict()

                        model.setItem(row_idx, 0, QStandardItem(guarantor_data.get("name", "Unknown")))
                        model.setItem(row_idx, 1, QStandardItem(guarantor_data.get("date_of_birth", "Unknown")))
                        model.setItem(row_idx, 2, QStandardItem('-'.join([guarantor_data.get('tel1ByOne', ''), guarantor_data.get('tel1ByTwo', ''), guarantor_data.get('tel1ByThree', '')])))
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
        total_sum = 0  
        principal_sum = 0  
        interest_sum = 0  
        overdue_interest_sum = 0  

        for row_idx, item in enumerate(data):
            status = item.get("status", 0)
            is_overdue = status == 2

            for col_idx, column_name in enumerate(columns):
                item_value = item.get(column_name, "")

                if column_name in ["Principal", "Interest", "Total"] and item_value != "":
                    item_value = "{:,}".format(int(float(item_value)))  
                    if column_name == "Total":  
                        total_sum += int(item.get(column_name, 0))
                    elif column_name == "Principal":  
                        principal_sum += int(item.get(column_name, 0))
                    elif column_name == "Interest":  
                        interest_sum += int(item.get(column_name, 0))

                item_value_obj = self.create_read_only_item(item_value)

                if is_overdue:
                    item_value_obj.setForeground(QColor(Qt.red))

                model.setItem(row_idx, col_idx, item_value_obj)

            status_text = status_mapping.get(status, 'Unknown')
            status_item = self.create_read_only_item(status_text)

            if is_overdue:
                status_item.setForeground(QColor(Qt.red))

                payment_date_str = item.get("Payment Date", "")
                if payment_date_str:
                    payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d")
                    current_date = datetime.now()

                    overdue_days = (current_date - payment_date).days 
                    if overdue_days > 0:
                        principal_amount = int(item.get("Principal", 0))
                        interest_amount = int(item.get("Interest", 0))
                        total_amount = principal_amount + interest_amount
                        overdue_interest_rate = float(self.loan_data.get("interest_rate", 0))
                        overdue_interest = self.overdue_interest(total_amount, overdue_days, overdue_interest_rate)
                        overdue_interest_sum += overdue_interest  

            model.setItem(row_idx, 4, status_item)

        table_view.setModel(model)
        table_view.resizeColumnsToContents()

        total_sum_formatted = "{:,.0f}".format(total_sum)
        principal_sum_formatted = "{:,.0f}".format(principal_sum)
        interest_sum_formatted = "{:,.0f}".format(interest_sum)

        if is_scheduled:
            self.remainingPrincipal.setText(principal_sum_formatted)
            self.remainingInterest.setText(interest_sum_formatted)
            self.remainingTotal.setText(total_sum_formatted)

            self.loan_data['remaining_principal'] = principal_sum
            self.loan_data['remaining_interest'] = interest_sum
            self.loan_data['remaining_overdue_interest'] = overdue_interest_sum
        else:
            pass

    def create_read_only_item(self, text):
        item = QStandardItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
    
    def overdue_interest(self, amount: int, overdue_days: int, overdue_interest_rate: float) -> int:
        overdue_interest = amount * (overdue_interest_rate / 100 / 365 * overdue_days)
        return round(overdue_interest)
    
    def on_mark_as_overdue_button_clicked(self):
        if self.loan_data is not None:
            self.post_registration_window = OverduePostRegistrationApp(self.loan_data, self)  # self를 넘겨줌
            self.post_registration_window.show()
        else:
            QMessageBox.warning(self, "Error", "No loan data selected!")


class OverduePostRegistrationApp(QMainWindow):
    def __init__(self, loan_data, parent_window=None):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "post_registration.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.generate_loan_number()
        self.loan_data = loan_data
        self.parent_window = parent_window  # OverdueRegistrationApp 객체를 전달받음
        self.init_ui(loan_data)

        self.startDate.setDate(QDate.currentDate())

        self.saveButton.clicked.connect(self.save_to_firestore)

        self.selected_customer_uid = loan_data['uid']

    def init_ui(self, loan_data):
        self.customerName.setText(loan_data['customer_name'])
        self.loanOfficer.setText(loan_data['officer_name'])
        self.startDate.setDate(QDate.currentDate())
        self.repaymentCycle.setText(loan_data['repayment_cycle'])
        
        self.principal.setText(str(loan_data['remaining_principal']))
        self.interest.setText(str(loan_data['remaining_interest']))
        self.overdueInterest.setText(str(loan_data['remaining_overdue_interest']))

    def setup_validators(self):
        int_validator = QIntValidator(0, 2147483647, self)
        
        self.loanNumber.setValidator(int_validator)
        self.repaymentCycle.setValidator(int_validator)
        self.principal.setValidator(int_validator)
        self.interestRate.setValidator(int_validator)
        self.interest.setValidator(int_validator)
        self.overdueInterest.setValidator(int_validator)

    def generate_loan_number(self):
        current_year_month = datetime.now().strftime("%Y%m")

        loans_ref = DB.collection("Overdue")
        loans_query = loans_ref.where("loan_number", ">=", current_year_month + "00000").where(
            "loan_number", "<=", current_year_month + "99999"
        ).order_by("loan_number", direction="DESCENDING").limit(1)
        
        loans = loans_query.stream()

        max_sequence_number = 0
        for loan in loans:
            loan_number = loan.to_dict().get("loan_number", "")
            if loan_number.startswith(current_year_month):
                sequence_number = int(loan_number[6:])
                max_sequence_number = max(max_sequence_number, sequence_number)

        new_sequence_number = max_sequence_number + 1
        new_loan_number = f"{current_year_month}{new_sequence_number:05d}"

        self.loanNumber.setText(new_loan_number)

    def save_to_firestore(self):
        if not self.selected_customer_uid:
            QMessageBox.critical(self, "Error", "Customer UID is missing.")
            return

        save_data = {
            'uid': self.selected_customer_uid,
            'loan_number': self.loanNumber.text(),
            'loan_officer': self.loan_data['loan_officer'],
            'start_date': self.startDate.date().toString("yyyy-MM-dd"),
            'repayment_cycle': self.repaymentCycle.text(),
            'interest_rate': self.interestRate.text(),
            'loan_schedule': [
                {
                    'principal': self.principal.text(),
                    'interest': self.interest.text(),
                    'overdue_interest': self.overdueInterest.text(),
                    'repayment_date': self.startDate.date().addDays(int(self.repaymentCycle.text())).toString("yyyy-MM-dd")
                }
            ],
        }

        management_data = save_data.copy()
        management_data['customer_name'] = self.loan_data['customer_name']

        try:
            doc_ref = DB.collection('Overdue').add(save_data)  
            loan_id = doc_ref[1].id  

            DB.collection('Overdue').document(loan_id).update({'loan_id': loan_id})
            DB.collection('Loan').document(self.loan_data['loan_id']).update({'loan_status': 'Overdue'})

            save_data['loan_id'] = loan_id
            management_data['loan_id'] = loan_id

            QMessageBox.information(self, "Success", "Successfully saved data.")
            
            self.open_overdue_loan_management(management_data)  

            # 두 창 모두 닫기
            if self.parent_window is not None:
                self.parent_window.close()  # OverdueRegistrationApp 닫기
            self.close()  # OverduePostRegistrationApp 닫기

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data to Firestore: {e}")

    def open_overdue_loan_management(self, loan_data):
        from src.pages.overdue.management import OverdueManagementApp
        self.management_window = OverdueManagementApp(loan_data)
        self.management_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverdueRegistrationApp()
    window.show()
    sys.exit(app.exec_())