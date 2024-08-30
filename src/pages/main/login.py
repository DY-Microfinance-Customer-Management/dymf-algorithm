import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic

from src.components import DB

class LoginApp(QDialog):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "login.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # img_widget = QLabel(text='dymf_logo')
        # logo_path = os.path.join(current_dir, 'dymf_logo.png')
        # img_widget.setPixmap(QPixmap(logo_path))
        # img_widget.setScaledContents(True)
        
        # 로그인 버튼 클릭 시 login 함수 연결
        self.login_button.clicked.connect(self.login)
        self.show()

    def login(self):
        user_id = self.id_text.text()
        password = self.pw_text.text()

        users_ref = DB.collection('User')
        query = users_ref.where('id', '==', user_id).where('pw', '==', password).get()

        if query:
            self.open_home()
        else:
            self.error_text.setText("Invalid ID or Password")

    def open_home(self):
        from src.pages.main.home import HomeApp
        self.home_window = HomeApp()
        self.home_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    sys.exit(app.exec_())
