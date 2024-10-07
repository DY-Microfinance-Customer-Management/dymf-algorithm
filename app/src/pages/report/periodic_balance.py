import sys, os

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import QDate
from google.cloud.firestore_v1.base_query import FieldFilter
import pandas as pd
from openpyxl import Workbook

from src.components import DB  # Firestore DB 임포트

class ReportPeriodicBalanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "periodic_balance.ui")
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())

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
        # self.endMonth.setValue(current_date.month())  # Set the current month
        self.endMonth.setValue(current_date.addMonths(-1).month())  # Set the current month

        # 로드된 데이터를 저장하는 변수
        self.loan_schedules = None
        self.overdue_schedules = None
        self.overdue_received_schedules = None

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

            # Document ID 생성
            document_id = f"{start_year}{start_month:02d}"

            # DB에서 해당 document_id의 데이터가 있는지 확인
            report_ref = DB.collection('Report').document(document_id)
            report_data = report_ref.get().to_dict()

            if report_data:
                # 이미 데이터가 존재하는 경우, 이 데이터를 사용해 엑셀 파일을 만듦
                self.create_excel_report_from_db(report_data, start_date)
            else:
                # 데이터가 없는 경우, 기존 로직을 통해 데이터를 생성하고 저장
                previous_month_str = f"{start_year}-{start_month - 1:02d}-01"
                previous_month = QDate.fromString(previous_month_str, "yyyy-MM-dd")

                try:
                    # 데이터를 가져와 처리 (데이터가 없을 경우만 DB에서 로드)
                    if self.loan_schedules is None or self.overdue_schedules is None:
                        self.loan_schedules, self.overdue_schedules, self.overdue_received_schedules = self.retrieve_loan_and_overdue_schedules()

                    total_principal = self.calculate_total_principal(start_date, previous_month)
                    
                    # 필터링 함수 호출 및 반환값 받기
                    filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules = self.filter_and_print_schedules(start_date, start_date.addMonths(1).addDays(-1))

                    # Report 저장 함수 호출
                    self.save_report_to_firestore(start_date, total_principal, filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules)

                    # 생성된 데이터를 이용해 엑셀 파일 생성
                    self.create_excel_report(start_date, total_principal, filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules)

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to calculate data: {e}")
        else:
            QMessageBox.warning(self, "Invalid Dates", "Start date and End date must be the same for this operation.")

    def retrieve_loan_and_overdue_schedules(self):
        try:
            # Loan collection 데이터 가져오기
            loans_ref = DB.collection('Loan').where(
                filter=FieldFilter('loan_status', '==', 'In Process')
            ).stream()
            loan_schedules = []
            overdue_schedules = []
            overdue_received_schedules = []

            for loan_doc in loans_ref:
                loan_data = loan_doc.to_dict()

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
                received_schedule = overdue_data.get('received_schedule', [])

                # overdue_schedules 추가
                for schedule in overdue_schedule:
                    payment_date = schedule.get('repayment_date', '')
                    overdue_schedules.append({
                        "Loan ID": overdue_doc.id,
                        "Payment Date": payment_date,
                        "Schedule": schedule
                    })

                for received in received_schedule:
                    payment_date = received.get('repayment_date', '')
                    overdue_received_schedules.append({
                        "Loan ID": overdue_doc.id,
                        "Payment Date": payment_date,
                        "Schedule": received
                    })

            return loan_schedules, overdue_schedules, overdue_received_schedules

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")
            return [], []

    def filter_and_print_schedules(self, start_date, end_date):
        # print(f'start_date: {start_date}, end_date: {end_date}')

        filtered_loan_schedules_1 = []
        filtered_loan_schedules_2 = []
        filtered_loan_schedules_3 = []
        filtered_overdue_received_schedules = []

        # 1. contract_date가 start_date 이전이면서 Schedule의 Payment Date가 start_date와 end_date 사이의 날짜이면서 status가 1인 모든 데이터
        for entry in self.loan_schedules:
            contract_date_str = entry['Contract Date']
            if contract_date_str:
                contract_date = QDate.fromString(contract_date_str, "yyyy-MM-dd")
                if contract_date < start_date:
                    payment_date_str = entry['Payment Date']
                    payment_date = QDate.fromString(payment_date_str, "yyyy-MM-dd")
                    if start_date <= payment_date <= end_date and entry['Schedule'].get('status') == 1:
                        filtered_loan_schedules_1.append(entry)

        # 2. contract_date가 start_date와 end_date 사이인 모든 데이터
        for entry in self.loan_schedules:
            contract_date_str = entry['Contract Date']
            if contract_date_str:
                contract_date = QDate.fromString(contract_date_str, "yyyy-MM-dd")
                if start_date <= contract_date <= end_date:
                    filtered_loan_schedules_2.append(entry)

        # 3. contract_date가 start_date와 end_date 사이인 Schedule의 Payment Date가 start_date와 end_date 사이인 Schedule의 status가 1인 모든 데이터
        for entry in self.loan_schedules:
            contract_date_str = entry['Contract Date']
            if contract_date_str:
                contract_date = QDate.fromString(contract_date_str, "yyyy-MM-dd")
                if start_date <= contract_date <= end_date:
                    payment_date_str = entry['Payment Date']
                    payment_date = QDate.fromString(payment_date_str, "yyyy-MM-dd")
                    if start_date <= payment_date <= end_date and entry['Schedule'].get('status') == 1:
                        filtered_loan_schedules_3.append(entry)

        # 4. self.overdue_received_schedules에서 Payment Date가 start_date와 end_date 사이인 모든 데이터
        for entry in self.overdue_received_schedules:
            payment_date_str = entry['Payment Date']
            payment_date = QDate.fromString(payment_date_str, "yyyy-MM-dd")
            if start_date <= payment_date <= end_date:
                filtered_overdue_received_schedules.append(entry)

        return filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules

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

    def save_report_to_firestore(self, start_date, total_principal, filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules):
        try:
            # Document ID 생성 (YYYYMM 형식)
            document_id = f"{start_date.year()}{start_date.month():02d}"

            # 데이터 구성
            start_asset = total_principal

            # Plus 데이터 (filtered_loan_schedules_2)
            plus = []
            for entry in filtered_loan_schedules_2:
                contract_date = entry['Contract Date']
                principal = entry['Schedule'].get('Principal', 0)
                if principal != 0:
                    plus.append({'date': contract_date, 'principal': principal})

            # Minus 데이터 (filtered_loan_schedules_1, filtered_loan_schedules_3, filtered_overdue_received_schedules)
            minus = []
            for entry_list in [filtered_loan_schedules_1, filtered_loan_schedules_3, filtered_overdue_received_schedules]:
                for entry in entry_list:
                    payment_date = entry['Payment Date']
                    principal = entry['Schedule'].get('Principal', 0)
                    interest = entry['Schedule'].get('Interest', 0)
                    overdue_interest = entry['Schedule'].get('Overdue Interest', 0)
                    if principal != 0:
                        minus.append({'date': payment_date, 'principal': principal})
                    if interest != 0:
                        minus.append({'date': payment_date, 'interest': interest})
                    if overdue_interest != 0:
                        minus.append({'date': payment_date, 'overdue_interest': overdue_interest})

            # Firestore에 저장할 데이터
            report_data = {
                "start_asset": start_asset,
                "plus": plus,
                "minus": minus
            }

            # Firestore에 데이터 저장
            DB.collection('Report').document(document_id).set(report_data)

            # QMessageBox.information(self, "Success", "Report saved successfully to Firestore.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save report to Firestore: {e}")

    def create_excel_report(self, start_date, total_principal, filtered_loan_schedules_1, filtered_loan_schedules_2, filtered_loan_schedules_3, filtered_overdue_received_schedules):
        try:
            # 파일 저장 대화 상자를 통해 사용자가 파일 경로를 선택하게 함
            options = QFileDialog.Options()
            default_path = "C:\\"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", default_path, "Excel Files (*.xlsx);;All Files (*)", options=options)

            
            if not file_path:
                QMessageBox.warning(self, "Cancelled", "Excel report creation was cancelled.")
                return
            
            # 확장자 확인 및 추가
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"

            # Create a new Excel file (workbook)
            writer = pd.ExcelWriter(file_path, engine='openpyxl')

            # 1. Periodic Loan Balance Sheet 시트 작성
            periodic_data = []

            # 시작 날짜 및 자산 금액
            if total_principal != 0:
                periodic_data.append({'Date': start_date.toString('yyyy-MM-dd'), 'Description': 'Total Loan Assets', 'Amount': total_principal})

            # 대출 자산 + 요인 (값이 0이 아닌 경우만 추가)
            plus_sum = {}
            for entry in filtered_loan_schedules_2:
                contract_date = entry['Contract Date']
                principal = entry['Schedule'].get('Principal', 0)
                if contract_date in plus_sum:
                    plus_sum[contract_date] += principal
                else:
                    plus_sum[contract_date] = principal

            for date, amount in plus_sum.items():
                if amount != 0:
                    periodic_data.append({'Date': date, 'Description': 'Loan Asset Increase', 'Amount': amount})

            # 대출 자산 - 요인 (값이 0이 아닌 경우만 추가)
            minus_sum = {}
            for entry_list in [filtered_loan_schedules_1, filtered_loan_schedules_3, filtered_overdue_received_schedules]:
                for entry in entry_list:
                    payment_date = entry['Payment Date']
                    principal = entry['Schedule'].get('Principal', 0)
                    if payment_date in minus_sum:
                        minus_sum[payment_date] += principal
                    else:
                        minus_sum[payment_date] = principal

            for date, amount in minus_sum.items():
                if amount != 0:
                    periodic_data.append({'Date': date, 'Description': 'Loan Asset Decrease', 'Amount': -amount})

            # 총 대출 자산 금액 계산 후 추가 (값이 0이 아닌 경우만 추가)
            end_total_principal = total_principal + sum(plus_sum.values()) - sum(minus_sum.values())
            if end_total_principal != 0:
                periodic_data.append({'Date': start_date.addMonths(1).toString('yyyy-MM-dd'), 'Description': 'Total Loan Assets', 'Amount': end_total_principal})

            # DataFrame으로 변환하여 시트에 작성
            periodic_df = pd.DataFrame(periodic_data)
            periodic_df.to_excel(writer, index=False, sheet_name='Periodic Loan Balance Sheet')

            # 2. Profit & Loss 시트 작성
            profit_loss_data = []

            # 필터된 데이터에서 이자 정보를 날짜별로 나열 (값이 0이 아닌 경우만 추가)
            for entry_list in [filtered_loan_schedules_1, filtered_loan_schedules_3]:
                for entry in entry_list:
                    payment_date = entry['Payment Date']
                    interest = entry['Schedule'].get('Interest', 0)
                    if interest != 0:
                        profit_loss_data.append({'Date': payment_date, 'Description': 'Interest', 'Amount': interest})

            for entry in filtered_overdue_received_schedules:
                payment_date = entry['Payment Date']
                interest = entry['Schedule'].get('Interest', 0)
                overdue_interest = entry['Schedule'].get('Overdue Interest', 0)
                if interest != 0:
                    profit_loss_data.append({'Date': payment_date, 'Description': 'Interest', 'Amount': interest})
                if overdue_interest != 0:
                    profit_loss_data.append({'Date': payment_date, 'Description': 'Overdue Interest', 'Amount': overdue_interest})

            # DataFrame으로 변환하여 시트에 작성
            profit_loss_df = pd.DataFrame(profit_loss_data)
            profit_loss_df.to_excel(writer, index=False, sheet_name='Profit & Loss')

            # Save the workbook
            writer.close()
            QMessageBox.information(self, "Success", "Excel report created successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create Excel report: {e}")

    def create_excel_report_from_db(self, report_data, start_date):
        try:
            # 파일 저장 대화 상자를 통해 사용자가 파일 경로를 선택하게 함
            options = QFileDialog.Options()
            default_path = "C:\\"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", default_path, "Excel Files (*.xlsx);;All Files (*)", options=options)

            if not file_path:
                QMessageBox.warning(self, "Cancelled", "Excel report creation was cancelled.")
                return

            # 확장자 확인 및 추가
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"

            # Create a new Excel file (workbook)
            writer = pd.ExcelWriter(file_path, engine='openpyxl')

            # 1. Periodic Loan Balance Sheet 시트 작성
            periodic_data = []

            # 시작 날짜 및 자산 금액
            periodic_data.append({'Date': start_date.toString('yyyy-MM-dd'), 'Description': 'Total Loan Assets', 'Amount': report_data.get('start_asset', 0)})

            # 날짜별 대출 자산 증가 요인 합산
            plus_entries = report_data.get('plus', [])
            plus_sum = {}
            for entry in plus_entries:
                date = entry.get('date', '')
                principal = entry.get('principal', 0)
                if date in plus_sum:
                    plus_sum[date] += principal
                else:
                    plus_sum[date] = principal

            for date, amount in plus_sum.items():
                if amount != 0:
                    periodic_data.append({'Date': date, 'Description': 'Loan Asset Increase', 'Amount': amount})

            # 날짜별 대출 자산 감소 요인 합산
            minus_entries = report_data.get('minus', [])
            minus_sum = {}
            for entry in minus_entries:
                date = entry.get('date', '')
                principal = entry.get('principal', 0)
                if principal != 0:
                    if date in minus_sum:
                        minus_sum[date] += principal
                    else:
                        minus_sum[date] = principal

            for date, amount in minus_sum.items():
                if amount != 0:
                    periodic_data.append({'Date': date, 'Description': 'Loan Asset Decrease', 'Amount': -amount})

            # 총 대출 자산 금액 계산 후 추가
            end_total_principal = report_data.get('start_asset', 0) + sum(plus_sum.values()) - sum(minus_sum.values())
            periodic_data.append({'Date': start_date.addMonths(1).toString('yyyy-MM-dd'), 'Description': 'Total Loan Assets', 'Amount': end_total_principal})

            # DataFrame으로 변환하여 시트에 작성
            periodic_df = pd.DataFrame(periodic_data)
            periodic_df.to_excel(writer, index=False, sheet_name='Periodic Loan Balance Sheet')

            # 2. Profit & Loss 시트 작성
            profit_loss_data = []

            # 날짜별 이자 정보 합산
            interest_sum = {}
            for entry in minus_entries:
                date = entry.get('date', '')
                interest = entry.get('interest', 0)
                overdue_interest = entry.get('overdue_interest', 0)

                if date not in interest_sum:
                    interest_sum[date] = {'Interest': 0, 'Overdue Interest': 0}

                if interest != 0:
                    interest_sum[date]['Interest'] += interest

                if overdue_interest != 0:
                    interest_sum[date]['Overdue Interest'] += overdue_interest

            for date, amounts in interest_sum.items():
                if amounts['Interest'] != 0:
                    profit_loss_data.append({'Date': date, 'Description': 'Interest', 'Amount': amounts['Interest']})
                if amounts['Overdue Interest'] != 0:
                    profit_loss_data.append({'Date': date, 'Description': 'Overdue Interest', 'Amount': amounts['Overdue Interest']})

            # DataFrame으로 변환하여 시트에 작성
            profit_loss_df = pd.DataFrame(profit_loss_data)
            profit_loss_df.to_excel(writer, index=False, sheet_name='Profit & Loss')

            # Save the workbook
            writer.close()
            QMessageBox.information(self, "Success", "Excel report created successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create Excel report: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPeriodicBalanceApp()
    window.show()
    sys.exit(app.exec_())