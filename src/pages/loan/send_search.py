import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from components import DB  # Firestore 연결을 위한 모듈
from datetime import datetime
import traceback


class SendSearchWindow(QMainWindow):
    def __init__(self):
        super(SendSearchWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui_loan_send_search.ui")  # UI 파일 경로 (고객상담자료검색)
        uic.loadUi(ui_path, self)
        self.setup_connections()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.SearchButton.clicked.connect(self.search_send_data)

    def search_send_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            customer_name = self.CustomerName.toPlainText().strip()
            sender_name = self.SenderName.toPlainText().strip()
            start_date = self.StartDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기
            end_date = self.LastDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기

            # 필수 필드 검증
            missing_fields = []
            if not customer_name:
                missing_fields.append("고객명")
            if not sender_name:
                missing_fields.append("발송대상자")
            if not start_date:
                missing_fields.append("발송 시작일")
            if not end_date:
                missing_fields.append("발송 종료일")

            # 비어있는 필드가 있으면 경고 메시지 표시 후 종료
            if missing_fields:
                QMessageBox.warning(self, "입력 오류", f"다음 필드를 입력하세요: {', '.join(missing_fields)}")
                return

            # Firestore 데이터베이스 조회 준비
            query = DB.collection('Send')  # Firestore의 Send 컬렉션에 접근

            # 고객명 검색
            if customer_name:
                query = query.where("customer_name", "==", customer_name)

            # 발송대상자 검색
            if sender_name:
                query = query.where("sender_name", "==", sender_name)

            # 발송일자 검색
            if start_date and end_date:
                start_date = datetime.combine(start_date, datetime.min.time())  # 날짜 변환
                end_date = datetime.combine(end_date, datetime.max.time())  # 날짜 변환
                query = query.where("send_date", ">=", start_date).where("send_date", "<=", end_date)

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
        self.SendTable.setRowCount(0)

        # 검색 결과 테이블에 표시
        try:
            for row_idx, doc in enumerate(results):
                send_data = doc.to_dict()
                self.SendTable.insertRow(row_idx)

                # Firestore 필드와 UI 열에 맞게 데이터를 매핑
                self.SendTable.setItem(row_idx, 0, QTableWidgetItem(str(send_data.get("send_date", ""))))
                self.SendTable.setItem(row_idx, 1, QTableWidgetItem(send_data.get("customer_name", "")))
                self.SendTable.setItem(row_idx, 2, QTableWidgetItem(str(send_data.get("contract_date", ""))))
                self.SendTable.setItem(row_idx, 3, QTableWidgetItem(send_data.get("loan_status", "")))
                self.SendTable.setItem(row_idx, 4, QTableWidgetItem(send_data.get("management_number", "")))
                self.SendTable.setItem(row_idx, 5, QTableWidgetItem(str(send_data.get("cost", ""))))
                self.SendTable.setItem(row_idx, 6, QTableWidgetItem(send_data.get("content", "")))
                self.SendTable.setItem(row_idx, 7, QTableWidgetItem(send_data.get("send_source", "")))
                self.SendTable.setItem(row_idx, 8, QTableWidgetItem(send_data.get("sender_name", "")))
                self.SendTable.setItem(row_idx, 9, QTableWidgetItem(send_data.get("process_result", "")))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"테이블에 데이터를 표시하는 중 오류가 발생했습니다: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = SendSearchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()