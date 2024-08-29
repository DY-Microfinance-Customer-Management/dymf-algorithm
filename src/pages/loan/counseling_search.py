import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QDate
from components import DB  # Firestore 연결을 위한 모듈
from datetime import datetime
import traceback


class CounselingSearchWindow(QMainWindow):
    def __init__(self):
        super(CounselingSearchWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "counseling_search.ui")  # UI 파일 경로 (고객상담자료검색)
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())

        self.StartDate.setDate(QDate.currentDate())
        self.LastDate.setDate(QDate.currentDate())

        self.setup_connections()
        self.setup_counseling_table()

    def setup_connections(self):
        # 검색 버튼 클릭 연결
        self.SearchButton.clicked.connect(self.search_counseling_data)

    def setup_counseling_table(self):
        # 테이블의 초기 설정 (TableView에 사용할 모델 설정)
        self.model = QStandardItemModel(0, 4)  # 4열 테이블로 설정
        self.model.setHorizontalHeaderLabels(["상담일자", "상담주제", "상담내용", "결과조치"])
        self.CounselingTable.setModel(self.model)

    def search_counseling_data(self):
        try:
            # 사용자 입력 데이터 가져오기
            customer_name = self.CustomerName.toPlainText().strip()
            start_date = self.StartDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기
            end_date = self.LastDate.date().toPyDate()  # QDateEdit에서 날짜 가져오기

            # 필수 필드 검증
            missing_fields = []
            if not customer_name:
                missing_fields.append("고객명")
            if not start_date:
                missing_fields.append("상담 시작일")
            if not end_date:
                missing_fields.append("상담 종료일")

            # 비어있는 필드가 있으면 경고 메시지 표시 후 종료
            if missing_fields:
                QMessageBox.warning(self, "입력 오류", f"다음 필드를 입력하세요: {', '.join(missing_fields)}")
                return

            # Firestore 데이터베이스 조회 준비
            query = DB.collection('Loan').where(field_path="customerName", op_string="==", value=customer_name)

            # Firestore에서 데이터 가져오기
            results = query.stream()

            # 테이블에 데이터를 채우기
            self.populate_table(results, start_date, end_date)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"데이터 검색에 실패했습니다: {e}")
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
                counselings = loan_data.get("counselings", [])

                for counseling in counselings:
                    counseling_date = counseling.get("date", "")

                    # 상담일자를 기준으로 필터링
                    if start_date <= datetime.strptime(counseling_date, "%Y-%m-%d").date() <= end_date:
                        counsel_subject = counseling.get("subject", "")
                        counsel_details = counseling.get("details", "")
                        corrective_measure = counseling.get("corrective_measure", "")

                        # 상담 데이터 테이블에 추가
                        row_data = [
                            QStandardItem(counseling_date),
                            QStandardItem(counsel_subject),
                            QStandardItem(counsel_details),
                            QStandardItem(corrective_measure)
                        ]
                        self.model.appendRow(row_data)
                        data_found = True  # 데이터가 있음을 표시

            # 테이블이 다시 그려지도록 강제 업데이트
            self.CounselingTable.setModel(self.model)
            self.CounselingTable.resizeColumnsToContents()

            # 만약 데이터를 찾지 못했다면 경고 메시지 표시
            if not data_found:
                QMessageBox.warning(self, "No Data Found", "일치하는 상담 데이터를 찾을 수 없습니다.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"테이블에 데이터를 표시하는 중 오류가 발생했습니다: {e}")
            print(f"Error: {e}")
            print(traceback.format_exc())  # 상세 오류 정보 콘솔 출력


def main():
    app = QApplication(sys.argv)
    window = CounselingSearchWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()