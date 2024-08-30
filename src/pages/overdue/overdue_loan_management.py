import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import QDate

from src.components import DB

class OverdueLoanManagementWindow(QMainWindow):
    def __init__(self, loan_data=None):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "overdue_loan_management.ui")
        uic.loadUi(ui_path, self)

        self.loanSearchButton.clicked.connect(self.open_select_loan)
        self.calculateButton.clicked.connect(self.update_received_schedule)

        self.current_loan_data = loan_data  # 현재 선택된 loan_data를 저장

        if loan_data:
            self.load_loan_data(loan_data)
        else:
            self.load_empty_state()

    def open_select_loan(self):
        from src.pages.overdue.select_loan import SelectLoanWindow
        self.select_loan_window = SelectLoanWindow()
        self.select_loan_window.loan_selected.connect(self.load_loan_data)
        self.select_loan_window.show()

    def load_loan_data(self, loan_data):
        self.current_loan_data = loan_data  # 현재 선택된 loan_data를 저장
        self.loanNumber.setText(loan_data['loan_number'])
        self.customerName.setText(loan_data['customer_name'])
        self.load_loan_schedule(loan_data['loanSchedule'], loan_data.get('receivedSchedule', []))

    def load_loan_schedule(self, loan_schedule, received_schedule):
        # Model 초기화
        total_rows = len(loan_schedule) + len(received_schedule)
        model = QStandardItemModel(total_rows, 7)
        model.setHorizontalHeaderLabels([
            'Repayment Date', 'Principal', 'Interest', 'Overdue Interest',
            'Received Principal', 'Received Interest', 'Received Overdue Interest'
        ])

        for i in range(len(loan_schedule)):
            # loanSchedule 항목 추가
            self.add_schedule_to_model(model, i * 2, loan_schedule[i])

            # receivedSchedule이 존재하면 그 다음에 추가
            if i < len(received_schedule):
                self.add_schedule_to_model(model, i * 2 + 1, received_schedule[i], received=True)

        self.loanTable.setModel(model)
        self.loanSearchButton.setEnabled(False)

    def add_schedule_to_model(self, model, row, schedule, received=False):
        if not received:
            repayment_date_item = QStandardItem(schedule.get('repayment_date', ''))
            principal_item = QStandardItem(schedule.get('principal', ''))
            interest_item = QStandardItem(schedule.get('interest', ''))
            overdue_interest_item = QStandardItem(schedule.get('overdue_interest', ''))

            received_principal_item = QStandardItem('')
            received_interest_item = QStandardItem('')
            received_overdue_interest_item = QStandardItem('')
        else:
            repayment_date_item = QStandardItem('')  # Repayment Date를 비워둠
            principal_item = QStandardItem('')  # Principal을 비워둠
            interest_item = QStandardItem('')  # Interest를 비워둠
            overdue_interest_item = QStandardItem('')  # Overdue Interest를 비워둠

            received_principal_item = QStandardItem(schedule.get('principal', ''))
            received_interest_item = QStandardItem(schedule.get('interest', ''))
            received_overdue_interest_item = QStandardItem(schedule.get('overdue_interest', ''))

            # 글씨 색상을 빨간색으로 설정
            red_color = QColor(255, 0, 0)
            repayment_date_item.setForeground(red_color)
            principal_item.setForeground(red_color)
            interest_item.setForeground(red_color)
            overdue_interest_item.setForeground(red_color)
            received_principal_item.setForeground(red_color)
            received_interest_item.setForeground(red_color)
            received_overdue_interest_item.setForeground(red_color)

        model.setItem(row, 0, repayment_date_item)
        model.setItem(row, 1, principal_item)
        model.setItem(row, 2, interest_item)
        model.setItem(row, 3, overdue_interest_item)
        model.setItem(row, 4, received_principal_item)
        model.setItem(row, 5, received_interest_item)
        model.setItem(row, 6, received_overdue_interest_item)

    def update_received_schedule(self):
        if not self.current_loan_data:
            QMessageBox.warning(self, "Error", "No loan selected.")
            return

        # 수령된 값을 가져옴
        received_principal = self.receivedPrincipal.text()
        received_interest = self.receivedInterest.text()
        received_overdue_interest = self.receivedOverdueInterest.text()

        if not (received_principal and received_interest and received_overdue_interest):
            QMessageBox.warning(self, "Error", "Please fill in all received fields.")
            return

        # 현재 loanSchedule의 마지막 항목을 가져옴
        last_schedule = self.current_loan_data['loanSchedule'][-1]

        # 입력된 값이 남아있는 금액을 초과하지 않도록 제한
        if int(received_principal) > int(last_schedule['principal']):
            QMessageBox.warning(self, "Error", "Received principal cannot be greater than remaining principal.")
            return

        if int(received_interest) > int(last_schedule['interest']):
            QMessageBox.warning(self, "Error", "Received interest cannot be greater than remaining interest.")
            return

        if int(received_overdue_interest) > int(last_schedule['overdue_interest']):
            QMessageBox.warning(self, "Error", "Received overdue interest cannot be greater than remaining overdue interest.")
            return

        # loanSchedule과 동일한 구조로 receivedSchedule 생성
        received_schedule = {
            'principal': received_principal,
            'interest': received_interest,
            'overdue_interest': received_overdue_interest,
        }

        try:
            # Firestore에서 현재 loan의 document를 업데이트
            loan_id = self.current_loan_data.get('loan_id')  # load_data에서 'loan_id' 설정이 누락되었을 수 있음
            if not loan_id:  # loan_id가 없을 경우 처리
                raise Exception("No loan_id in the current loan data")

            # 기존 receivedSchedule에 추가
            existing_received_schedule = self.current_loan_data.get('receivedSchedule', [])
            updated_received_schedule = existing_received_schedule + [received_schedule]

            # 기존 loanSchedule에 다음 회차 추가
            next_loan_schedule = self.add_next_loan_schedule(received_schedule)
            updated_loan_schedule = self.current_loan_data['loanSchedule'] + [next_loan_schedule]

            # Firestore에 업데이트
            DB.collection('Overdue').document(loan_id).update({
                'receivedSchedule': updated_received_schedule,
                'loanSchedule': updated_loan_schedule
            })

            # 업데이트된 데이터를 포함하여 loanTable 갱신
            self.current_loan_data['receivedSchedule'] = updated_received_schedule
            self.current_loan_data['loanSchedule'] = updated_loan_schedule
            self.load_loan_schedule(updated_loan_schedule, updated_received_schedule)

            QMessageBox.information(self, "Success", "Received schedule updated successfully.")
            self.clear_received_fields()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update received schedule: {e}")

    def add_next_loan_schedule(self, received_schedule):
        # 현재 loanSchedule의 마지막 항목을 가져옴
        last_schedule = self.current_loan_data['loanSchedule'][-1]

        # 새롭게 추가될 다음 회차의 Repayment Date 계산
        last_repayment_date = QDate.fromString(last_schedule['repayment_date'], "yyyy-MM-dd")
        repayment_cycle = int(self.current_loan_data['repayment_cycle'])
        next_repayment_date = last_repayment_date.addDays(repayment_cycle).toString("yyyy-MM-dd")

        # 다음 loanSchedule의 principal, interest, overdue interest 계산
        next_principal = str(int(last_schedule['principal']) - int(received_schedule['principal']))
        next_interest = str(int(last_schedule['interest']) - int(received_schedule['interest']))
        next_overdue_interest = str(round((int(last_schedule['overdue_interest']) \
                                 - int(received_schedule['overdue_interest']) \
                                 + int(next_interest)) * 0.28))

        # 새 loanSchedule 생성
        next_loan_schedule = {
            'repayment_date': next_repayment_date,
            'principal': next_principal,
            'interest': next_interest,
            'overdue_interest': next_overdue_interest,
        }

        return next_loan_schedule

    def clear_received_fields(self):
        self.receivedPrincipal.clear()
        self.receivedInterest.clear()
        self.receivedOverdueInterest.clear()

    def load_empty_state(self):
        self.loanNumber.clear()
        self.customerName.clear()
        self.loanTable.setModel(QStandardItemModel(0, 7))
        self.loanTable.model().setHorizontalHeaderLabels([
            'Repayment Date', 'Principal', 'Interest', 'Overdue Interest',
            'Received Principal', 'Received Interest', 'Received Overdue Interest'
        ])
        self.clear_received_fields()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverdueLoanManagementWindow()
    window.show()
    sys.exit(app.exec_())