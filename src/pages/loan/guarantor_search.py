import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import traceback

from src.components import DB  # Firestore 연결을 위한 모듈

class GuarantorSearchWindow(QMainWindow):
    def __init__(self):
        super(GuarantorSearchWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "guarantor_search.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        # 기본적으로 현재 날짜로 설정
        self.StartDate.setDate(QDate.currentDate())
        self.LastDate.setDate(QDate.currentDate())

        self.setup_connections()
        self.setup_guarantor_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.SearchButton.clicked.connect(self.search_guarantor_data)

    def setup_guarantor_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 4열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["Guarantor Name", "Guarantor Type", "Guarantor Relation", "Customer Name"])
        self.GuarantorTable.setModel(self.model)

    def search_guarantor_data(self):
        try:
            customer_name = self.CustomerName.toPlainText().strip()  # 변경된 부분
            start_date = self.StartDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기
            end_date = self.LastDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기

            # Firestore 데이터베이스 조회 준비
            query = DB.collection('Loan')

            # 고객명으로 필터링 (입력된 경우)
            if customer_name:
                query = query.where("customerName", "==", customer_name)

            # Firestore에서 데이터 가져오기
            results = query.stream()

            # 테이블에 데이터를 채우기
            self.populate_table(results, start_date, end_date)

        except Exception as e:
            QMessageBox.critical(self, "Data does not exist")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

    def populate_table(self, results, start_date, end_date):
        # 기존 테이블 데이터 삭제
        self.model.removeRows(0, self.model.rowCount())

        # 검색 결과가 없음을 확인하기 위한 플래그
        data_found = False

        # 검색 결과 테이블에 표시
        try:
            for doc in results:
                loan_data = doc.to_dict()
                contract_date_str = loan_data.get("contractDate", "")

                # Firestore에서 받은 contractDate가 비어있는지 확인
                if not contract_date_str:
                    continue

                # contractDate를 datetime 객체로 변환
                contract_date = datetime.strptime(contract_date_str, "%Y-%m-%d").date()

                # 계약일자를 기준으로 필터링
                if start_date <= contract_date <= end_date:
                    guarantors = loan_data.get("guarantors", [])

                    for guarantor in guarantors:
                        guarantor_name = guarantor.get("name", "")
                        guarantor_type = guarantor.get("type", "")
                        relation = guarantor.get("relation", "")
                        customer_name = loan_data.get("customerName", "")
                        # 보증인 데이터 테이블에 추가
                        row_data = [
                            QStandardItem(guarantor_name),
                            QStandardItem(relation),
                            QStandardItem(guarantor_type),
                            QStandardItem(customer_name)
                        ]
                        self.model.appendRow(row_data)
                        data_found = True  # 데이터가 있음을 표시

            # 테이블이 다시 그려지도록 강제 업데이트
            self.GuarantorTable.setModel(self.model)
            self.GuarantorTable.resizeColumnsToContents()

            # 만약 데이터를 찾지 못했다면 경고 메시지 표시
            if not data_found:
                QMessageBox.warning(self, "Data does not exist")

        except Exception as e:
            QMessageBox.critical(self, "Data does not exist")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = GuarantorSearchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()