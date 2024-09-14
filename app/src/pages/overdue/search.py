import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import os
import traceback
from src.components import DB  # Firestore 연결을 위한 모듈

class OverdueSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "search.ui")  # UI 파일 경로 (고객상담자료검색)
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        # Details 버튼 비활성화
        # self.detailsButton.setEnabled(False)

        self.setup_connections()
        self.setup_loan_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.searchButton.clicked.connect(self.search_loan_data)
        # 테이블의 행 클릭 연결
        # self.overdueLoanTable.clicked.connect(self.on_table_click)
        # Details 버튼 클릭 연결
        # self.detailsButton.clicked.connect(self.on_details_button_clicked)

    def setup_loan_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 5열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["Overdue Loan Number", "NRC No.", "Customer Name", "Loan Type"])
        self.overdueLoanTable.setModel(self.model)
        self.overdueLoanTable.horizontalHeader().setStretchLastSection(True)

        # 테이블을 읽기 전용으로 설정
        self.overdueLoanTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def search_loan_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            customer_name = self.customerName.text().strip()

            if customer_name:
                # Firestore에서 모든 고객 정보를 가져오기
                all_customers = DB.collection('Customer').get()

                # 대소문자 구분 없이 필터링
                filtered_customers = []
                lower_customer_name = customer_name.lower()
                for customer in all_customers:
                    customer_data = customer.to_dict()
                    name = customer_data.get("name", "")
                    if lower_customer_name in name.lower():  # 대소문자 구분 없이 비교
                        filtered_customers.append(customer.id)

                if not filtered_customers:
                    QMessageBox.warning(self, "No Data", "No customer found with the entered name.")
                    return

                # 테이블의 기존 데이터 삭제
                self.model.removeRows(0, self.model.rowCount())

                # 대출 정보를 가져와서 테이블에 채우기
                for customer_id in filtered_customers:
                    loan_ref = DB.collection('Overdue').where("uid", "==", customer_id).get()
                    self.populate_table(loan_ref, customer_id)
            else:
                QMessageBox.warning(self, "Input Error", "Please enter the customer's name.")

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while searching for customer data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

    def get_customer_data(self, customer_id):
        """
        Customer DB에서 customer_id를 사용하여 customer_name과 nrc_no를 가져오는 함수
        """
        try:
            customer_ref = DB.collection('Customer').document(customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                return customer_data.get("name", ""), customer_data.get("nrc_no", "")
            else:
                return "", ""
        except Exception as e:
            print(f"Error fetching customer data: {e}")
            return "", ""

    def populate_table(self, loan_results, customer_id):
        # 고객 정보를 Customer DB에서 가져오기
        customer_name, nrc_no = self.get_customer_data(customer_id)

        # Loan 데이터가 있을 경우 테이블에 표시
        try:
            for doc in loan_results:
                loan_data = doc.to_dict()
                loan_number = loan_data.get("loan_number", "")
                loan_type = loan_data.get("loan_type", "")

                # 데이터를 테이블에 추가
                row_data = [
                    QStandardItem(loan_number),
                    QStandardItem(customer_name),
                    QStandardItem(nrc_no),
                    QStandardItem(loan_type)
                ]
                self.model.appendRow(row_data)

            # 테이블이 다시 그려지도록 강제 업데이트
            self.overdueLoanTable.setModel(self.model)
            self.overdueLoanTable.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while processing loan data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

def main():
    app = QApplication(sys.argv)
    window = OverdueSearchApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()