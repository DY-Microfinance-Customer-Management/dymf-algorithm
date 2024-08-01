import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QLabel, QStackedWidget, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, db
from PyQt5 import QtCore, QtGui, QtWidgets

from pages.login import Ui_MainWindow as Ui_LoginWindow
from pages.home import Ui_MainWindow as Ui_HomeWindow
from pages.customer.registration import Ui_Customer as Ui_CustomerRegistration


# Firebase Admin SDK 초기화
cred = credentials.Certificate("configs/test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-hungun-default-rtdb.firebaseio.com/'
})

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('로그인')
        self.setFixedSize(self.size())

        # 로그인 버튼 클릭 시 이벤트 핸들러 연결
        self.ui.login_button.clicked.connect(self.login)

        # error_text 라벨 초기 상태 설정
        self.ui.error_text.setText('')
        self.ui.error_text.setAlignment(Qt.AlignCenter)

        self.set_logo_image('assets/logo.jpg')

    def set_logo_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.ui.logo_image.setPixmap(pixmap)
        self.ui.logo_image.setScaledContents(True)

    def login(self):
        user_id = self.ui.id_text.text()
        user_pw = self.ui.pw_text.text()

        if user_id and user_pw:
            try:
                # Firebase Realtime Database에서 아이디와 비밀번호 확인
                ref = db.reference('users').child(user_id)
                user_data = ref.get()
                if user_data and user_data.get('password') == user_pw:
                    self.ui.error_text.setText('로그인에 성공했습니다.')
                    self.open_main_window()
                else:
                    self.ui.error_text.setText('사용자 정보가 없습니다.')
            except Exception as e:
                self.ui.error_text.setText('오류가 발생했습니다: ' + str(e))
        else:
            self.ui.error_text.setText('아이디와 비밀번호를 입력하세요.')

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_HomeWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('메인 화면')

        # Connect the customer search button to the method
        self.ui.action.triggered.connect(self.open_customer_registration)

    def open_customer_registration(self):
        self.customer_registration_window = QMainWindow()
        self.customer_registration_ui = Ui_CustomerRegistration()
        self.customer_registration_ui.setupUi(self.customer_registration_window)
        self.customer_registration_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loginDialog = LoginDialog()
    loginDialog.show()
    sys.exit(app.exec_())
