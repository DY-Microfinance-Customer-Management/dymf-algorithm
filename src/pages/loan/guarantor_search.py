import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from components import DB  # Firestore 연결을 위한 모듈
from datetime import datetime
import traceback


class GuarantorSearchWindow(QMainWindow):
    def __init__(self):
        super(GuarantorSearchWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui_loan_guarantor_search.ui")
        uic.loadUi(ui_path, self)
        self.setup_connections()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.SearchButton.clicked.connect(self.search_guarantor_data)

    def search_guarantor_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            guarantor_name = self.GuarantorName.text().strip()
            customer_name = self.CustomerName.text().strip()
            start_date = self.StartDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기
            end_date = self.LastDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기

            # 필수 필드 확인
            missing_fields = []
            if not guarantor_name:
                missing_fields.append("보증인명")
            if not customer_name:
                missing_fields.append("고객명")
            if not start_date:
                missing_fields.append("계약 시작일")
            if not end_date:
                missing_fields.append("계약 종료일")

            # 만약 비어 있는 필드가 있으면 경고 메시지 표시
            if missing_fields:
                QMessageBox.warning(self, "입력 오류", f"다음 필드를 입력하세요: {', '.join(missing_fields)}")
                return

            # Firestore 데이터베이스 조회 준비
            query = DB.collection('Loan')

            # 보증인명 검색
            if guarantor_name:
                query = query.where("guarantor_name", "==", guarantor_name)

            # 고객명 검색
            if customer_name:
                query = query.where("customer_name", "==", customer_name)

            # 계약일자 검색
            if start_date and end_date:
                start_date = datetime.combine(start_date, datetime.min.time())  # 날짜 변환
                end_date = datetime.combine(end_date, datetime.max.time())  # 날짜 변환
                query = query.where("contract_date", ">=", start_date).where("contract_date", "<=", end_date)

            # Firestore에서 데이터 가져오기
            print("Executing Firestore query...")
            results = query.stream()

            # 테이블에 데이터를 채우기
            self.populate_table(results)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"데이터 검색에 실패했습니다: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력

    def populate_table(self, results):
        # 기존 테이블 데이터 삭제
        self.GuarantorTable.setRowCount(0)

        # 검색 결과 테이블에 표시
        try:
            for row_idx, doc in enumerate(results):
                loan_data = doc.to_dict()
                self.GuarantorTable.insertRow(row_idx)

                # 데이터가 Firestore의 필드와 UI의 열에 맞게 매핑됨
                self.GuarantorTable.setItem(row_idx, 0, QTableWidgetItem(str(loan_data.get("contract_date", ""))))
                self.GuarantorTable.setItem(row_idx, 1, QTableWidgetItem(loan_data.get("customer_name", "")))
                self.GuarantorTable.setItem(row_idx, 2, QTableWidgetItem(loan_data.get("guarantor_class", "")))
                self.GuarantorTable.setItem(row_idx, 3, QTableWidgetItem(loan_data.get("guarantor_name", "")))
                self.GuarantorTable.setItem(row_idx, 4, QTableWidgetItem(loan_data.get("guarantor_dob", "")))  # 생년월일
                self.GuarantorTable.setItem(row_idx, 5, QTableWidgetItem(loan_data.get("guarantor_gender", "")))  # 성별
                self.GuarantorTable.setItem(row_idx, 6, QTableWidgetItem(loan_data.get("relationship", "")))  # 관계
                self.GuarantorTable.setItem(row_idx, 7, QTableWidgetItem(loan_data.get("guarantor_phone", "")))  # 핸드폰번호
                self.GuarantorTable.setItem(row_idx, 8, QTableWidgetItem(loan_data.get("guarantor_nickname", "")))  # 별칭
                self.GuarantorTable.setItem(row_idx, 9, QTableWidgetItem(loan_data.get("registered_by", "")))  # 등록자
        except Exception as e:
            QMessageBox.critical(self, "Error", f"테이블에 데이터를 표시하는 중 오류가 발생했습니다: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = GuarantorSearchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()