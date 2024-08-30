import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView, QTableWidgetItem
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from src.components import DB  # Firestore DB 임포트

class UserManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "user_management.ui")
        uic.loadUi(ui_path, self)

        self.current_user_id = None
        self.initialize_ui()
        self.show()

    def initialize_ui(self):
        # 버튼 초기 설정 및 테이블 설정
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.userName.setEnabled(False)
        self.userID.setEnabled(False)
        self.userPassword.setEnabled(False)

        self.setup_table()

        # 버튼 클릭 연결
        self.newButton.clicked.connect(self.on_new_clicked)
        self.editButton.clicked.connect(self.on_edit_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.deleteButton.clicked.connect(self.on_delete_clicked)
        self.userTable.clicked.connect(self.on_table_row_clicked)

        # 초기 데이터 로드
        self.load_users()

    def setup_table(self):
        # 테이블 모델 설정
        self.model = QStandardItemModel(0, 2)
        self.model.setHorizontalHeaderLabels(["Name", "User ID", "User Password"])
        self.userTable.setModel(self.model)
        self.userTable.resizeColumnsToContents()
        self.userTable.setSelectionBehavior(QTableView.SelectRows)

    def load_users(self):
        try:
            users = DB.collection('User').get()

            self.model.setRowCount(0)
            for user in users:
                user_data = user.to_dict()
                name_item = QStandardItem(user_data.get("name", ""))
                id_item = QStandardItem(user_data.get("id", ""))
                pw_item = QStandardItem(user_data.get("pw", ""))

                self.model.appendRow([name_item, id_item, pw_item])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {e}")

    def on_new_clicked(self):
        # 새로운 사용자 등록을 위한 UI 활성화
        self.userName.clear()
        self.userID.clear()
        self.userPassword.clear()

        self.userName.setEnabled(True)
        self.userID.setEnabled(True)
        self.userPassword.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.current_user_id = None  # 신규 등록 시 기존 ID 없음

    def on_edit_clicked(self):
        # 사용자 정보를 수정할 수 있도록 필드 활성화
        self.userName.setEnabled(True)
        self.userID.setEnabled(True)
        self.userPassword.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

    def on_save_clicked(self):
        # 사용자 정보 저장
        name = self.userName.text()
        user_id = self.userID.text()
        password = self.userPassword.text()

        if not name or not user_id or not password:
            QMessageBox.warning(self, "Validation Error", "Name, User ID, and Password cannot be empty.")
            return

        user_data = {
            "name": name,
            "id": user_id,
            "pw": password
        }

        try:
            if self.current_user_id:
                # 기존 사용자 정보 수정
                DB.collection('User').document(self.current_user_id).update(user_data)
                QMessageBox.information(self, "Success", "User information updated successfully.")
            else:
                # 새로운 사용자 정보 추가
                new_user_ref = DB.collection('User').add(user_data)
                # UID(Document ID)를 저장
                DB.collection('User').document(new_user_ref[1].id).update({"uid": new_user_ref[1].id})
                QMessageBox.information(self, "Success", "New user added successfully.")

            # UI 초기화 및 데이터 다시 로드
            self.clear_fields()
            self.load_users()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save user data: {e}")

    def on_delete_clicked(self):
        # 선택된 사용자 정보 삭제
        if not self.current_user_id:
            QMessageBox.warning(self, "Selection Error", "No user selected.")
            return

        try:
            DB.collection('User').document(self.current_user_id).delete()
            QMessageBox.information(self, "Success", "User deleted successfully.")
            self.clear_fields()
            self.load_users()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete user: {e}")

    def on_table_row_clicked(self, index):
        # 테이블에서 선택된 행의 데이터를 필드에 표시
        row = index.row()
        model = self.userTable.model()
        name = model.index(row, 0).data()
        user_id = model.index(row, 1).data()

        self.userName.setText(name)
        self.userID.setText(user_id)

        # Firestore에서 선택된 사용자의 ID를 가져옴
        users = DB.collection('User').where('id', '==', user_id).get()
        if users:
            self.current_user_id = users[0].id

        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.saveButton.setEnabled(False)

        # 필드를 비활성화하여 선택된 행이 수정되지 않도록 함
        self.userName.setEnabled(False)
        self.userID.setEnabled(False)
        self.userPassword.setEnabled(False)

    def clear_fields(self):
        # 필드 초기화 및 비활성화
        self.userName.clear()
        self.userID.clear()
        self.userPassword.clear()
        self.userName.setEnabled(False)
        self.userID.setEnabled(False)
        self.userPassword.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = UserManagementApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()