import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5 import uic
from PyQt5.QtGui import QIntValidator, QIcon
from datetime import datetime

from src.components import DB  # DB 객체를 components 모듈에서 가져옴

class OverdueRegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 특정 입력란과 버튼 비활성화
        self.startDate.setDate(QDate.currentDate())
        self.checkBoxMale.setEnabled(False)
        self.checkBoxFemale.setEnabled(False)
        self.disable_inputs()

        self.customerSearchButton.clicked.connect(self.open_customer_search)
        self.saveButton.clicked.connect(self.save_to_firestore)

        self.selected_customer_uid = None  # 고객 UID를 저장할 변수

        # QLineEdit 위젯에 숫자만 입력되도록 설정
        self.setup_validators()

    def setup_validators(self):
        # 숫자만 입력 가능하도록 QIntValidator 설정
        int_validator = QIntValidator(0, 2147483647, self)
        
        # 모든 QLineEdit에 validator 설정
        self.loanNumber.setValidator(int_validator)
        self.repaymentCycle.setValidator(int_validator)
        self.principal.setValidator(int_validator)
        self.interestRate.setValidator(int_validator)
        self.interest.setValidator(int_validator)
        self.overdueInterest.setValidator(int_validator)

    def disable_inputs(self):
        widgets_to_disable = [
            self.loanNumber,
            self.loanOfficer,
            self.startDate,
            self.repaymentCycle,
            self.principal,
            self.interestRate,
            self.interest,
            self.overdueInterest,
            self.saveButton
        ]

        for widget in widgets_to_disable:
            widget.setEnabled(False)

    def enable_inputs(self):
        widgets_to_enable = [
            self.loanOfficer,
            self.startDate,
            self.repaymentCycle,
            self.principal,
            self.interestRate,
            self.interest,
            self.overdueInterest,
            self.saveButton
        ]

        for widget in widgets_to_enable:
            widget.setEnabled(True)

    def open_customer_search(self):
        from app.src.components.select_customer import SelectCustomerWindow
        self.customer_search_window = SelectCustomerWindow()
        self.customer_search_window.customer_selected.connect(self.handle_customer_selected)
        self.customer_search_window.show()

    def handle_customer_selected(self, customer_data):
        self.customerName.setText(customer_data['name'])
        self.customerDateOfBirth.setText(customer_data['date_of_birth'])
        self.customerContact.setText(customer_data['phone1'] + '-' + customer_data['phone2'] + '-' + customer_data['phone3'])

        # 성별에 따라 체크박스 설정
        if customer_data.get('gender') == 'Man':
            self.checkBoxMale.setChecked(True)
            self.checkBoxFemale.setChecked(False)
        elif customer_data.get('gender') == 'Woman':
            self.checkBoxMale.setChecked(False)
            self.checkBoxFemale.setChecked(True)
        else:
            self.checkBoxMale.setChecked(False)
            self.checkBoxFemale.setChecked(False)

        self.selected_customer_uid = customer_data.get('uid')  # 고객 UID 저장

        self.enable_inputs()
        self.generate_loan_number()  # 고객 선택 후 loanNumber 생성
        self.customerSearchButton.setEnabled(False)

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

        loan_data = {
            'customer_name': self.customerName.text(),
            'customer_dob': self.customerDateOfBirth.text(),
            'customer_contact': self.customerContact.text(),
            'customer_uid': self.selected_customer_uid,  # 고객 UID 추가
            'loan_number': self.loanNumber.text(),
            'loan_officer': self.loanOfficer.currentText(),
            'start_date': self.startDate.date().toString("yyyy-MM-dd"),
            'repayment_cycle': self.repaymentCycle.text(),
            'interest_rate': self.interestRate.text(),
            'loanSchedule': [
                {
                    'principal': self.principal.text(),
                    'interest': self.interest.text(),
                    'overdue_interest': self.overdueInterest.text(),
                    'repayment_date': self.startDate.date().addDays(int(self.repaymentCycle.text())).toString("yyyy-MM-dd")
                }
            ],
            'gender': 'Man' if self.checkBoxMale.isChecked() else 'Woman' if self.checkBoxFemale.isChecked() else 'Unknown'
        }

        try:
            doc_ref = DB.collection('Overdue').add(loan_data)  # Firestore에 데이터를 추가
            loan_id = doc_ref[1].id  # 생성된 document의 ID 가져오기

            # loan_id를 Firestore에 추가로 저장
            DB.collection('Overdue').document(loan_id).update({'loan_id': loan_id})

            # loan_id를 loan_data에 추가
            loan_data['loan_id'] = loan_id

            QMessageBox.information(self, "Success", "Successfully saved data.")
            self.reset_form()  # 저장 후 초기 상태로 리셋
            self.customerSearchButton.setEnabled(True)

            self.open_overdue_loan_management(loan_data)  # 저장된 데이터와 함께 관리 화면 열기

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data to Firestore: {e}")

    def reset_form(self):
        # 입력된 값을 초기화하고 비활성화 상태로 되돌리기
        self.customerName.clear()
        self.customerDateOfBirth.clear()
        self.customerContact.clear()
        self.checkBoxMale.setChecked(False)
        self.checkBoxFemale.setChecked(False)
        self.loanNumber.clear()
        self.loanOfficer.setCurrentIndex(0)
        self.startDate.setDate(QDate.currentDate())
        self.repaymentCycle.clear()
        self.principal.clear()
        self.interest.clear()
        self.overdueInterest.clear()

        self.disable_inputs()

    def open_overdue_loan_management(self, loan_data):
        from app.src.pages.overdue.management import OverdueLoanManagementWindow
        self.management_window = OverdueLoanManagementWindow(loan_data)
        self.management_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverdueRegistrationWindow()
    window.show()
    sys.exit(app.exec_())