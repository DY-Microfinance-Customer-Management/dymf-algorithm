import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import traceback

from src.components import DB  # Firestore 연결을 위한 모듈


class SearchCollateralWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "collateral.ui")  # UI 파일 경로
        if not os.path.exists(ui_path):
            QMessageBox.critical(self, "Error", f"UI file not found: {ui_path}")
            sys.exit(1)
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        # 연결 설정
        self.setup_connections()
        self.setup_collateral_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.searchButton.clicked.connect(self.search_collateral_data)

    def setup_collateral_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 3)  # 4열 테이블로 설정
        self.model.setHorizontalHeaderLabels(
            ["Type", "Name", "Details"]
        )
        self.collateralTable.setModel(self.model)
        self.collateralTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
    def search_collateral_data(self):
        try:
            # loanNumber 입력받기
            loan_number = self.loanNumber.text().strip()

            if not loan_number:
                QMessageBox.warning(self, "Input Error", "Please enter a Loan Number.")
                return

            # Firestore 데이터베이스에서 loan_number로 검색
            query = DB.collection('Loan').where("loan_number", "==", loan_number)

            # Firestore에서 데이터 가져오기
            loan_docs = query.stream()

            # 테이블에 데이터를 채우기
            self.populate_table(loan_docs)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Data retrieval failed: {e}")
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
                collaterals = loan_data.get("collaterals", [])

                if not collaterals:
                    continue

                # 담보 정보 테이블에 추가
                for collateral in collaterals:
                    collateral_name = collateral.get("name", "")
                    collateral_type = collateral.get("type", "")
                    collateral_details = collateral.get("details", "")

                    row_data = [
                        QStandardItem(collateral_type),
                        QStandardItem(collateral_name),
                        QStandardItem(collateral_details)
                    ]
                    self.model.appendRow(row_data)
                    data_found = True  # 데이터가 있음을 표시

            # 테이블이 다시 그려지도록 강제 업데이트
            self.collateralTable.setModel(self.model)
            self.collateralTable.resizeColumnsToContents()

            # 만약 데이터를 찾지 못했다면 경고 메시지 표시
            if not data_found:
                QMessageBox.warning(self, "No Data Found", "No collateral data found for the given Loan Number.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Data processing failed: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = SearchCollateralWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()