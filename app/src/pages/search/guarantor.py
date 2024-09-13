import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import traceback

from src.components import DB  # Firestore 연결을 위한 모듈


class SearchGuarantorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "guarantor.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        self.setup_connections()
        self.setup_guarantor_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.searchButton.clicked.connect(self.search_guarantor_data)

    def setup_guarantor_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 4열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["Guarantor Name", "NRC No.", "Date of Birth", "Telephone"])
        self.guarantorTable.setModel(self.model)
        self.guarantorTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
    def search_guarantor_data(self):
        try:
            loan_number = self.loanNumber.text().strip()  # Loan Number 입력받기

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
                guarantor_ids = loan_data.get("guarantors", [])

                # 보증인 정보가 없으면 다음 대출 데이터로 넘어감
                if not guarantor_ids:
                    continue

                # Guarantor DB에서 보증인 정보를 검색하여 테이블에 표시
                for guarantor_id in guarantor_ids:
                    guarantor_ref = DB.collection('Guarantor').document(guarantor_id).get()

                    if guarantor_ref.exists:
                        guarantor_data = guarantor_ref.to_dict()
                        guarantor_info = {
                            'name': guarantor_data.get('name', ''),
                            'nrc_no': guarantor_data.get('nrc_no', ''),
                            'date_of_birth': guarantor_data.get('date_of_birth', ''),
                            'telephone': f"{guarantor_data.get('tel1ByOne', '')}-{guarantor_data.get('tel1ByTwo', '')}-{guarantor_data.get('tel1ByThree', '')}"
                        }

                        # 테이블에 데이터를 추가
                        row_data = [
                            QStandardItem(guarantor_info['name']),
                            QStandardItem(guarantor_info['nrc_no']),
                            QStandardItem(guarantor_info['date_of_birth']),
                            QStandardItem(guarantor_info['telephone']),
                        ]
                        self.model.appendRow(row_data)
                        data_found = True  # 데이터가 있음을 표시

            # 테이블이 다시 그려지도록 강제 업데이트
            self.guarantorTable.setModel(self.model)
            self.guarantorTable.resizeColumnsToContents()

            # 만약 데이터를 찾지 못했다면 경고 메시지 표시
            if not data_found:
                QMessageBox.warning(self, "No Data", "No matching guarantor data found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while fetching guarantor data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = SearchGuarantorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()