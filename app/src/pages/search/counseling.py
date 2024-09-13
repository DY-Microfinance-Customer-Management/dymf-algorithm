import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import traceback

from src.components import DB  # Firestore 연결을 위한 모듈


class SearchCounselingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "counseling.ui")  # UI 파일 경로 (고객상담자료검색)
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        self.setup_connections()
        self.setup_counseling_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.searchButton.clicked.connect(self.search_counseling_data)

    def setup_counseling_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 4열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])
        self.counselingTable.setModel(self.model)
        self.counselingTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def search_counseling_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            loan_number = self.loanNumber.text().strip()  # loanNumber 입력받기

            if not loan_number:
                QMessageBox.warning(self, "Input Error", "Please enter a Loan Number.")
                return

            # Firestore 데이터베이스 조회 준비
            query = DB.collection('Loan').where("loan_number", "==", loan_number)

            # Firestore에서 데이터 가져오기
            loan_docs = query.stream()

            # 테이블에 데이터를 채우기
            self.populate_table(loan_docs)

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while fetching data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

    def populate_table(self, loan_docs):
        # 기존 테이블 데이터 삭제
        self.model.removeRows(0, self.model.rowCount())

        # 검색 결과가 없음을 확인하기 위한 플래그
        data_found = False

        # 검색 결과 테이블에 표시
        try:
            for loan_doc in loan_docs:
                loan_data = loan_doc.to_dict()
                counselings = loan_data.get("counselings", [])

                # 상담 데이터를 테이블에 추가
                for counseling in counselings:
                    counseling_date = counseling.get("date", "")
                    counsel_subject = counseling.get("subject", "")
                    counsel_details = counseling.get("details", "")
                    corrective_measure = counseling.get("corrective_measure", "")

                    row_data = [
                        QStandardItem(counseling_date),
                        QStandardItem(counsel_subject),
                        QStandardItem(counsel_details),
                        QStandardItem(corrective_measure)
                    ]
                    self.model.appendRow(row_data)
                    data_found = True  # 데이터가 있음을 표시

            # 테이블이 다시 그려지도록 강제 업데이트
            self.counselingTable.setModel(self.model)
            self.counselingTable.resizeColumnsToContents()

            # 만약 데이터를 찾지 못했다면 경고 메시지 표시
            if not data_found:
                QMessageBox.warning(self, "No Data Found", "No counseling data found for the given Loan Number.")

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while processing data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = SearchCounselingWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()