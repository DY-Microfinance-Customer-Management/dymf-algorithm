import sys, os

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic, QtCore
from PyQt5.QtCore import QDate

from components import DB  # Firestore DB를 사용한다고 가정

class RepaymentSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "repayment_search.ui")
        uic.loadUi(ui_path, self)
        self.show()
        self.setup_connections()
        self.setup_table()
        self.set_default_dates()

    def setup_connections(self):
        # 버튼 클릭 시 각 메서드 연결
        self.searchButton.clicked.connect(self.on_search_clicked)
        self.paidButton.clicked.connect(self.on_paid_clicked)
        self.cancelPaymentButton.clicked.connect(self.on_cancel_payment_clicked)
        self.toExcelButton.clicked.connect(self.export_to_excel)

    def setup_table(self):
        # 테이블 초기화 (헤더 설정)
        model = QStandardItemModel(0, 5)
        model.setHorizontalHeaderLabels(["Date", "Amount", "Paid", "Outstanding", "Status"])
        self.repaymentScheduleTable.setModel(model)

    def set_default_dates(self):
        # startDate와 endDate를 오늘 날짜로 설정
        today = QDate.currentDate()
        self.startDate.setDate(today)
        self.endDate.setDate(today)

    def on_search_clicked(self):
        # 검색 버튼 클릭 시 DB에서 데이터를 검색하는 메서드
        start_date = self.startDate.date().toString("yyyy-MM-dd")
        end_date = self.endDate.date().toString("yyyy-MM-dd")
        print(1)
        
        # Firestore에서 Loan Collection의 모든 문서 가져오기
        try:
            print(2)
            loans_ref = DB.collection('Loan')
            loans = loans_ref.stream()

            # 테이블의 이전 데이터를 삭제
            self.repaymentScheduleTable.model().removeRows(0, self.repaymentScheduleTable.model().rowCount())
            print(3)

            # 모든 문서에 대해 loanSchedule 필드 검색
            for loan_doc in loans:
                print(4)
                loan_data = loan_doc.to_dict()
                loan_schedule = loan_data.get("loanSchedule", [])
                print(5)

                # loanSchedule에서 paymentDate가 start_date와 end_date 사이에 있는 항목만 필터링
                for schedule in loan_schedule:
                    print(6)
                    payment_date = schedule.get("Payment Date", "")
                    if start_date <= payment_date <= end_date:
                        # 필터링된 항목을 테이블에 추가
                        self.add_schedule_to_table(schedule)
                        print(7)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load repayment schedules: {e}")

    def add_schedule_to_table(self, schedule):
        # 테이블에 스케줄 데이터를 추가하는 함수
        model = self.repaymentScheduleTable.model()
        row = model.rowCount()

        # 스케줄 데이터를 가져와 각 컬럼에 삽입
        model.setItem(row, 0, QStandardItem(schedule.get("Payment Date", "")))
        model.setItem(row, 1, QStandardItem(str(schedule.get("amount", 0))))
        model.setItem(row, 2, QStandardItem(str(schedule.get("paid", 0))))
        model.setItem(row, 3, QStandardItem(str(schedule.get("outstanding", 0))))
        model.setItem(row, 4, QStandardItem(schedule.get("status", "")))

    def on_paid_clicked(self):
        # Paid 버튼 클릭 시 동작할 메서드
        selected_indexes = self.repaymentScheduleTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record to mark as paid.")
            return
        
        # 선택된 행의 데이터 가져오기
        selected_row = selected_indexes[0].row()
        model = self.repaymentScheduleTable.model()
        date = model.index(selected_row, 0).data()
        
        QMessageBox.information(self, "Payment Marked as Paid", f"Payment for {date} marked as paid.")

    def on_cancel_payment_clicked(self):
        # Cancel Payment 버튼 클릭 시 동작할 메서드
        selected_indexes = self.repaymentScheduleTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record to cancel.")
            return
        
        # 선택된 행의 데이터 가져오기
        selected_row = selected_indexes[0].row()
        model = self.repaymentScheduleTable.model()
        date = model.index(selected_row, 0).data()
        
        QMessageBox.information(self, "Payment Canceled", f"Payment for {date} has been canceled.")

    def export_to_excel(self):
        # 엑셀로 내보내기 버튼 클릭 시 동작할 메서드
        QMessageBox.information(self, "Export to Excel", "Repayment data will be exported to Excel.")

def main():
    app = QApplication(sys.argv)
    window = RepaymentSearchApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
