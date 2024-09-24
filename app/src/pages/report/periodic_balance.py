import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import QDate
from src.components import DB  # Firestore DB 임포트

class ReportPeriodicBalanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "periodic_balance.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set fixed size to prevent resizing
        self.setFixedSize(self.size())

        # Set spinbox range (for example, year: 2024 to 3000, month: 1 to 12)
        self.startYear.setRange(2024, 3000)  # Set year range
        self.startMonth.setRange(1, 12)  # Set month range
        self.endYear.setRange(2024, 3000)  # Set year range
        self.endMonth.setRange(1, 12)  # Set month range

        # Set the year and month with the current date
        current_date = QDate.currentDate()
        self.startYear.setValue(current_date.year())  # Set the current year
        self.startMonth.setValue(current_date.addMonths(-1).month())  # Set the previous month
        self.endYear.setValue(current_date.year())  # Set the current year
        self.endMonth.setValue(current_date.month())  # Set the current month

        # 로드된 데이터를 저장하는 변수
        self.loan_schedules = None
        self.overdue_schedules = None

        # Connect the downloadButton click event to the process_report function
        self.downloadButton.clicked.connect(self.process_report)

    def process_report(self):
        start_year = self.startYear.value()
        start_month = self.startMonth.value()
        end_year = self.endYear.value()
        end_month = self.endMonth.value()

        # 시작 날짜와 종료 날짜가 같은지 확인
        if start_year == end_year and start_month == end_month:
            start_date_str = f"{start_year}-{start_month:02d}-01"
            start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")

            previous_month_str = f"{start_year}-{start_month-1:02d}-01"
            previous_month = QDate.fromString(previous_month_str, "yyyy-MM-dd")

            try:
                # 데이터를 가져와 처리 (데이터가 없을 경우만 DB에서 로드)
                if self.loan_schedules is None or self.overdue_schedules is None:
                    self.loan_schedules, self.overdue_schedules = self.retrieve_loan_and_overdue_schedules()

                total_principal = self.calculate_total_principal(start_date, previous_month)
                QMessageBox.information(self, "Total Principal", f"Total principal is: {total_principal}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to calculate data: {e}")
        else:
            QMessageBox.warning(self, "Invalid Dates", "Start date and End date must be the same for this operation.")

    def retrieve_loan_and_overdue_schedules(self):
        try:
            # Loan collection 데이터 가져오기
            loans_ref = DB.collection('Loan').stream()  
            loan_schedules = []
            overdue_schedules = []

            for loan_doc in loans_ref:
                loan_data = loan_doc.to_dict()

                # loan_status가 'Overdue'인 것은 제외
                if loan_data.get('loan_status') == 'Overdue':
                    continue

                loan_schedule = loan_data.get('loan_schedule', [])
                contract_date = loan_data.get('contract_date', "")

                # loan_schedules 추가
                for schedule in loan_schedule:
                    payment_date = schedule.get('Payment Date', '')
                    loan_schedules.append({
                        "Loan ID": loan_doc.id,
                        "Contract Date": contract_date,
                        "Payment Date": payment_date,
                        "Schedule": schedule
                    })

            # Overdue collection 데이터 가져오기
            overdue_ref = DB.collection('Overdue').stream()  

            for overdue_doc in overdue_ref:
                overdue_data = overdue_doc.to_dict()
                overdue_schedule = overdue_data.get('loan_schedule', [])

                # overdue_schedules 추가
                for schedule in overdue_schedule:
                    payment_date = schedule.get('Payment Date', '')
                    overdue_schedules.append({
                        "Loan ID": overdue_doc.id,
                        "Payment Date": payment_date,
                        "Schedule": schedule
                    })

            return loan_schedules, overdue_schedules

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
            return [], []

    def calculate_total_principal(self, start_date, previous_month):
        total_principal = 0

        # loan_schedules 처리
        for entry in self.loan_schedules:
            payment_date_str = entry['Payment Date']
            payment_date = QDate.fromString(payment_date_str, "yyyy-MM-dd")

            contract_date_str = entry['Contract Date']
            if contract_date_str:
                contract_date = QDate.fromString(contract_date_str, "yyyy-MM-dd")
                if contract_date > start_date:
                    continue

            # 주어진 날짜 이전의 Payment Date와 status가 2인 데이터 필터링
            if payment_date < start_date and entry['Schedule'].get('status') == 2:
                principal = entry['Schedule'].get('Principal', 0)
                total_principal += principal

        # overdue_schedules 처리
        latest_principal = 0
        for entry in self.overdue_schedules:
            payment_date_str = entry['Payment Date']
            payment_date = QDate.fromString(payment_date_str, "yyyy-MM-dd")

            # 주어진 날짜 이전과 이후의 Payment Date를 필터링
            if payment_date < start_date and entry['Schedule'].get('status') == 2:
                principal = entry['Schedule'].get('Principal', 0)
                total_principal += principal

            # start_date 직전 월에 해당하는 Payment Date 중 가장 최근 날짜 선택
            if previous_month <= payment_date < start_date:
                latest_principal = max(latest_principal, entry['Schedule'].get('Principal', 0))

        total_principal += latest_principal
        return total_principal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPeriodicBalanceApp()
    window.show()
    sys.exit(app.exec_())