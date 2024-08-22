import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView, QTableWidgetItem
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from components import DB  # Firestore DB 임포트

class LoanOfficerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan_officer.ui")
        uic.loadUi(ui_path, self)

        self.current_officer_id = None
        self.initialize_ui()
        self.show()

    def initialize_ui(self):
        # 버튼 초기 설정 및 테이블 설정
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.officerName.setEnabled(False)
        self.officerServiceArea.setEnabled(False)

        self.setup_table()

        # 버튼 클릭 연결
        self.newButton.clicked.connect(self.on_new_clicked)
        self.editButton.clicked.connect(self.on_edit_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.deleteButton.clicked.connect(self.on_delete_clicked)
        self.officerTable.clicked.connect(self.on_table_row_clicked)

        # 초기 데이터 로드
        self.load_officers()

    def setup_table(self):
        # 테이블 모델 설정
        self.model = QStandardItemModel(0, 2)
        self.model.setHorizontalHeaderLabels(["Name", "Service Area"])
        self.officerTable.setModel(self.model)
        self.officerTable.resizeColumnsToContents()
        self.officerTable.setSelectionBehavior(QTableView.SelectRows)

    def load_officers(self):
        try:
            officers = DB.collection('Officer').get()

            self.model.setRowCount(0)
            for officer in officers:
                officer_data = officer.to_dict()
                name_item = QStandardItem(officer_data.get("name", ""))
                area_item = QStandardItem(officer_data.get("service_area", ""))

                self.model.appendRow([name_item, area_item])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load officers: {e}")

    def on_new_clicked(self):
        # 새로운 오피서 등록을 위한 UI 활성화
        self.officerName.clear()
        self.officerServiceArea.clear()

        self.officerName.setEnabled(True)
        self.officerServiceArea.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.current_officer_id = None  # 신규 등록 시 기존 ID 없음

    def on_edit_clicked(self):
        # 오피서 정보를 수정할 수 있도록 필드 활성화
        self.officerName.setEnabled(True)
        self.officerServiceArea.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

    def on_save_clicked(self):
        # 오피서 정보 저장
        name = self.officerName.text()
        service_area = self.officerServiceArea.text()

        if not name or not service_area:
            QMessageBox.warning(self, "Validation Error", "Name and Service Area cannot be empty.")
            return

        officer_data = {
            "name": name,
            "service_area": service_area
        }

        try:
            if self.current_officer_id:
                # 기존 오피서 정보 수정
                DB.collection('Officer').document(self.current_officer_id).update(officer_data)
                QMessageBox.information(self, "Success", "Officer information updated successfully.")
            else:
                # 새로운 오피서 정보 추가
                DB.collection('Officer').add(officer_data)
                QMessageBox.information(self, "Success", "New officer added successfully.")

            # UI 초기화 및 데이터 다시 로드
            self.clear_fields()
            self.load_officers()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save officer data: {e}")

    def on_delete_clicked(self):
        # 선택된 오피서 정보 삭제
        if not self.current_officer_id:
            QMessageBox.warning(self, "Selection Error", "No officer selected.")
            return

        try:
            DB.collection('Officer').document(self.current_officer_id).delete()
            QMessageBox.information(self, "Success", "Officer deleted successfully.")
            self.clear_fields()
            self.load_officers()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete officer: {e}")

    def on_table_row_clicked(self, index):
        # 테이블에서 선택된 행의 데이터를 필드에 표시
        row = index.row()
        model = self.officerTable.model()
        name = model.index(row, 0).data()
        service_area = model.index(row, 1).data()

        self.officerName.setText(name)
        self.officerServiceArea.setText(service_area)

        # Firestore에서 선택된 오피서의 ID를 가져옴
        officers = DB.collection('Officer').where('name', '==', name).get()
        if officers:
            self.current_officer_id = officers[0].id

        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.saveButton.setEnabled(False)

        # 필드를 비활성화하여 선택된 행이 수정되지 않도록 함
        self.officerName.setEnabled(False)
        self.officerServiceArea.setEnabled(False)

    def clear_fields(self):
        # 필드 초기화 및 비활성화
        self.officerName.clear()
        self.officerServiceArea.clear()
        self.officerName.setEnabled(False)
        self.officerServiceArea.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = LoanOfficerApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
