import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QAbstractItemView
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
import os
import traceback

from src.components import DB
from src.pages.search.loan_details import LoanDetailsApp
from google.cloud.firestore_v1.base_query import FieldFilter

class SearchLoanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan.ui")  # UI 파일 경로 (고객상담자료검색)
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 창 크기 고정
        self.setFixedSize(self.size())

        # Details 버튼 비활성화
        self.detailsButton.setEnabled(False)

        self.setup_connections()
        self.setup_loan_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.SearchButton.clicked.connect(self.search_loan_data)
        # 테이블의 행 클릭 연결
        self.loanTable.clicked.connect(self.on_table_click)
        # Details 버튼 클릭 연결
        self.detailsButton.clicked.connect(self.on_details_button_clicked)

    def setup_loan_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 5열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["NRC No.", "Customer Name", "Loan Number", "Loan Type"])
        self.loanTable.setModel(self.model)
        self.loanTable.horizontalHeader().setStretchLastSection(True)

        # 테이블을 읽기 전용으로 설정
        self.loanTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def search_loan_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            customer_name = self.CustomerName.text().strip()
            
            lower_keyword = customer_name.lower()
            upper_keyword = customer_name.title()

            if customer_name:
                filtered_customers = []
                
                # lower_keyword_customers = DB.collection('Customer').where(filter=FieldFilter('name', '>=', lower_keyword)).where(filter=FieldFilter('name', '<=', lower_keyword + '\uf8ff')).stream()
                # upper_keyword_customers = DB.collection('Customer').where(filter=FieldFilter('name', '>=', upper_keyword)).where(filter=FieldFilter('name', '<=', upper_keyword + '\uf8ff')).stream()
                lower_keyword_customers = DB.collection('Customer').where(filter=FieldFilter('name', '==', lower_keyword)).stream()
                upper_keyword_customers = DB.collection('Customer').where(filter=FieldFilter('name', '==', upper_keyword)).stream()

                for lower_doc in lower_keyword_customers:
                    filtered_customers.append(lower_doc.id)
                    print(lower_doc.to_dict())

                for  upper_doc in upper_keyword_customers:
                    filtered_customers.append(upper_doc.id)
                    print(upper_doc.to_dict())

                if not filtered_customers:
                    QMessageBox.warning(self, "No Data", "No customer found with the entered name.")
                    return

                # 테이블의 기존 데이터 삭제
                self.model.removeRows(0, self.model.rowCount())

                # 대출 정보를 가져와서 테이블에 채우기
                for customer_id in filtered_customers:
                    loan_ref = DB.collection('Loan').where("uid", "==", customer_id).get()
                    
                    # 데이터가 없는 경우 경고 메시지 표시
                    if not loan_ref:
                        QMessageBox.warning(self, "No Data", f"No loan data found for {upper_keyword}")
                    else:
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
                    QStandardItem(nrc_no),
                    QStandardItem(customer_name),
                    QStandardItem(loan_number),
                    QStandardItem(loan_type)
                ]
                self.model.appendRow(row_data)

            # 테이블이 다시 그려지도록 강제 업데이트
            self.loanTable.setModel(self.model)
            self.loanTable.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", "An error occurred while processing loan data.")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

    def on_table_click(self, index):
        # 테이블에서 클릭한 행 전체 선택
        self.loanTable.selectRow(index.row())
        # Details 버튼 활성화
        self.detailsButton.setEnabled(True)

    def on_details_button_clicked(self):
        selected_indexes = self.loanTable.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a loan record.")
            return

        selected_row = selected_indexes[0].row()
        model = self.loanTable.model()

        # Get the loan number from the selected row
        loan_number = model.index(selected_row, 2).data()  # 3번째 열에서 대출 번호를 가져옵니다.

        try:
            # Fetch the loan details using the loan number
            loan_ref = DB.collection('Loan').where('loan_number', '==', loan_number).get()

            if not loan_ref:
                QMessageBox.warning(self, "No Data", "No loan found with the selected loan number.")
                return

            loan_doc = loan_ref[0]  # 첫 번째 결과 사용
            loan_data = loan_doc.to_dict()

            # 하위 필드로부터 배열이나 딕셔너리 정보를 가져오는 방식
            collaterals = loan_data.get('collaterals', [])
            counselings = loan_data.get('counselings', [])
            guarantors = loan_data.get('guarantors', [])
            loan_schedule = loan_data.get('loan_schedule', [])

            # LoanDetailsApp을 열고 각 테이블에 데이터를 채움
            self.loan_details_app = LoanDetailsApp(
                loan_data,
                collaterals,
                counselings,
                guarantors,
                loan_schedule  # loan_schedule 데이터를 전체 전달하고, 내부에서 분리
            )
            self.loan_details_app.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load loan details: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())


def main():
    app = QApplication(sys.argv)
    window = SearchLoanApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()