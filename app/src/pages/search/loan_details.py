import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QTabWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor
from src.components import DB  # Firestore 연결을 위한 모듈

class LoanDetailsApp(QMainWindow):
    def __init__(self, loan_data, collaterals_data, counselings_data, guarantors_data, loan_schedule_data):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan_details.ui")  # Load the appropriate UI file
        uic.loadUi(ui_path, self)
        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        # Set up tabs
        self.tabWidget.currentChanged.connect(self.on_tab_change)

        # Store the data
        self.loan_data = loan_data
        self.collaterals_data = collaterals_data
        self.counselings_data = counselings_data
        self.guarantors_data = guarantors_data
        self.loan_schedule_data = loan_schedule_data

        # Initialize the first tab with loan details
        self.load_loan_details()
        self.populate_schedule_tables()  # loan details 탭에서 테이블에 데이터 채우기

        # 테이블들을 읽기 전용으로 설정
        self.set_tables_read_only()

    def set_tables_read_only(self):
        """테이블을 읽기 전용으로 설정"""
        tables = [self.repaymentScheduleTable, self.receivedTable, self.guarantorTable, self.collateralTable, self.counselingTable]
        for table in tables:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def load_loan_details(self):
        """Load loan details when the first tab is shown."""
        self.loanNumber.setText(self.loan_data.get('loan_number', ''))
        self.contractDate.setText(self.loan_data.get('contract_date', ''))
        self.loanStatus.setText(self.loan_data.get('loan_status', ''))
        self.loanType.setText(self.loan_data.get('loan_type', ''))
        officer_data = DB.collection('Officer').document(self.loan_data.get('loan_officer', '')).get().to_dict()
        self.loanOfficer.setText(officer_data['name'])
        self.cpNumber.setText(self.loan_data.get('cp_number', ''))
        self.loanAmount.setText(str(self.loan_data.get('principal', '')))
        self.repaymentCycle.setText(self.loan_data.get('repayment_cycle', ''))
        self.interestRate.setText(str(self.loan_data.get('interest_rate', '')))
        self.numberOfRepayment.setText(str(self.loan_data.get('number_of_repayment', '')))
        self.repaymentMethod.setText(self.loan_data.get('repayment_method', ''))

    def on_tab_change(self, index):
        """Handle tab change event."""
        if index == 0:
            self.load_loan_details()  # Loan Details tab
        elif index == 1:
            self.populate_guarantors_table()  # Guarantors tab
        elif index == 2:
            self.populate_table(self.collateralTable, self.collaterals_data)  # Collaterals tab
        elif index == 3:
            self.populate_table(self.counselingTable, self.counselings_data)  # Counselings tab

    def populate_table(self, table_widget, data):
        # 데이터가 없는 경우 테이블을 비우고 종료
        if not data:
            model = QStandardItemModel(0, 0)  # 빈 모델로 테이블 초기화
            table_widget.setModel(model)
            return

        # 데이터가 리스트가 아닌 경우
        if not isinstance(data, list):
            model = QStandardItemModel(0, 0)  # 빈 모델로 테이블 초기화
            table_widget.setModel(model)
            return

        # 데이터의 첫 번째 항목이 딕셔너리가 아닌 경우
        if not isinstance(data[0], dict):
            model = QStandardItemModel(0, 0)  # 빈 모델로 테이블 초기화
            table_widget.setModel(model)
            return

        # Create model and fill table
        model = QStandardItemModel(len(data), len(data[0]))  # assuming all dicts have the same keys
        model.setHorizontalHeaderLabels(data[0].keys())  # 딕셔너리의 키를 테이블 헤더로 사용

        for row_idx, row_data in enumerate(data):
            is_overdue = False  # 해당 행이 Overdue인지 추적

            for col_idx, (key, value) in enumerate(row_data.items()):
                if key == 'status':
                    # status 값을 텍스트로 변환
                    value = self.convert_status(value)

                    # status가 "Overdue"인 경우 해당 행 전체의 텍스트를 빨간색으로 설정
                    if value == "Overdue":
                        is_overdue = True
                else:
                    # 숫자 형식인 항목에 대해 쉼표를 추가 (status가 아닌 경우)
                    if isinstance(value, (int, float)):
                        value = format(value, ",")

                item = QStandardItem(str(value))
                model.setItem(row_idx, col_idx, item)

            # 행이 Overdue일 경우, 행 전체의 텍스트를 빨간색으로 설정
            if is_overdue:
                for col_idx in range(len(row_data)):
                    model.item(row_idx, col_idx).setForeground(QColor('red'))

        table_widget.setModel(model)
        table_widget.resizeColumnsToContents()
    def convert_status(self, status_value):
        """status 값을 텍스트로 변환"""
        if status_value == 0:
            return "Scheduled"
        elif status_value == 1:
            return "Paid"
        elif status_value == 2:
            return "Overdue"
        return "Unknown"

    def populate_guarantors_table(self):
        """Guarantor 데이터를 DB에서 검색하여 테이블에 추가"""
        # Guarantor 데이터가 없으면 빈 테이블로 설정하고 종료
        if not self.guarantors_data:
            self.populate_table(self.guarantorTable, [])
            return

        guarantor_details = []
        try:
            # Guarantor 데이터를 DB에서 가져오기
            for guarantor_id in self.guarantors_data:
                guarantor_ref = DB.collection('Guarantor').document(guarantor_id).get()
                if guarantor_ref.exists:
                    guarantor_data = guarantor_ref.to_dict()
                    # 필요한 데이터만 추출
                    guarantor_info = {
                        'name': guarantor_data.get('name', ''),
                        'nrc_no': guarantor_data.get('nrc_no', ''),
                        'date_of_birth': guarantor_data.get('date_of_birth', ''),
                        # 전화번호는 세 개의 필드를 합쳐서 하나로 출력
                        'telephone': f"{guarantor_data.get('tel1ByOne', '')}-{guarantor_data.get('tel1ByTwo', '')}-{guarantor_data.get('tel1ByThree', '')}"
                    }
                    guarantor_details.append(guarantor_info)

            # Guarantor details가 없으면 빈 테이블로 설정
            self.populate_table(self.guarantorTable, guarantor_details)

        except Exception as e:
            self.populate_table(self.guarantorTable, [])

    def populate_schedule_tables(self):
        """loan_schedule_data를 loan_status에 따라 테이블에 분리해서 채워줍니다."""

        # 필요한 열만 포함하도록 데이터를 필터링합니다.
        def filter_schedule_data(data):
            filtered_data = []
            for schedule in data:
                filtered_schedule = {
                    'Payment Date': schedule.get('Payment Date', ''),
                    'Principal': schedule.get('Principal', ''),
                    'Interest': schedule.get('Interest', ''),
                    'Total': schedule.get('Total', ''),
                    'status': schedule.get('status', '')
                }
                filtered_data.append(filtered_schedule)
            return filtered_data

        # Repayment Schedule (status가 0 또는 2인 경우)
        repayment_schedule_data = [schedule for schedule in self.loan_schedule_data if schedule.get('status') in [0, 2]]
        repayment_schedule_data = filter_schedule_data(repayment_schedule_data)

        # Received Schedule (status가 1인 경우)
        received_schedule_data = [schedule for schedule in self.loan_schedule_data if schedule.get('status') == 1]
        received_schedule_data = filter_schedule_data(received_schedule_data)

        # Repayment Schedule Table (status == 0 또는 2)
        self.populate_table(self.repaymentScheduleTable, repayment_schedule_data)

        # Received Schedule Table (status == 1)
        self.populate_table(self.receivedTable, received_schedule_data)

def main():
    # Firestore에서 실제 데이터를 가져와서 로드하는 부분
    loan_data = {}  # 실제 loan data를 Firestore에서 가져와서 여기에 할당
    collaterals_data = []  # Firestore에서 가져온 담보 데이터
    counselings_data = []  # Firestore에서 가져온 상담 데이터
    guarantors_data = []  # Firestore에서 가져온 보증인 ID 리스트
    loan_schedule_data = []  # Firestore에서 가져온 대출 스케줄 데이터

    app = QApplication(sys.argv)
    window = LoanDetailsApp(loan_data, collaterals_data, counselings_data, guarantors_data, loan_schedule_data)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()