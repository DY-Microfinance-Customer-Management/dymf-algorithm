import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QWidget, QLabel, QGridLayout
import firebase_admin
from firebase_admin import credentials, db

# Firebase Admin SDK 초기화
cred = credentials.Certificate('test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-hungun-default-rtdb.firebaseio.com/'
})

class FirebaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Firebase와 PyQt5 연동 예제')
        self.setGeometry(100, 100, 400, 300)

        # 레이아웃 설정
        self.layout = QVBoxLayout()

        # 회원가입 버튼
        self.signup_button = QPushButton('회원가입', self)
        self.signup_button.clicked.connect(self.show_signup)
        self.layout.addWidget(self.signup_button)

        # 로그인 버튼
        self.login_button = QPushButton('로그인', self)
        self.login_button.clicked.connect(self.show_login)
        self.layout.addWidget(self.login_button)

        # 메시지 라벨
        self.message_label = QLabel('', self)
        self.layout.addWidget(self.message_label)

        # 중앙 위젯 설정
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def show_signup(self):
        self.signup_window = SignupWindow(self)
        self.signup_window.show()

    def show_login(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def set_message(self, message):
        self.message_label.setText(message)

    def show_calculator(self):
        self.calculator_window = CalculatorWindow()
        self.calculator_window.show()
        self.hide()

class SignupWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('회원가입')
        self.setGeometry(100, 100, 300, 200)
        self.layout = QVBoxLayout()

        # 아이디 입력 필드
        self.id_field = QLineEdit(self)
        self.id_field.setPlaceholderText('아이디 입력')
        self.layout.addWidget(self.id_field)

        # 비밀번호 입력 필드
        self.pw_field = QLineEdit(self)
        self.pw_field.setPlaceholderText('비밀번호 입력')
        self.pw_field.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.pw_field)

        # 회원가입 버튼
        self.signup_button = QPushButton('회원가입', self)
        self.signup_button.clicked.connect(self.signup)
        self.layout.addWidget(self.signup_button)

        self.setLayout(self.layout)

    def signup(self):
        user_id = self.id_field.text()
        user_pw = self.pw_field.text()

        if user_id and user_pw:
            # Firebase Realtime Database에 아이디와 비밀번호 저장
            ref = db.reference('users')
            ref.child(user_id).set({'password': user_pw})
            self.parent().set_message('회원가입 성공!')
            self.close()
        else:
            self.parent().set_message('아이디와 비밀번호를 입력하세요.')

class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('로그인')
        self.setGeometry(100, 100, 300, 200)
        self.layout = QVBoxLayout()

        # 아이디 입력 필드
        self.id_field = QLineEdit(self)
        self.id_field.setPlaceholderText('아이디 입력')
        self.layout.addWidget(self.id_field)

        # 비밀번호 입력 필드
        self.pw_field = QLineEdit(self)
        self.pw_field.setPlaceholderText('비밀번호 입력')
        self.pw_field.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.pw_field)

        # 로그인 버튼
        self.login_button = QPushButton('로그인', self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def login(self):
        user_id = self.id_field.text()
        user_pw = self.pw_field.text()

        if user_id and user_pw:
            # Firebase Realtime Database에서 아이디와 비밀번호 확인
            ref = db.reference('users').child(user_id)
            user_data = ref.get()
            if user_data and user_data['password'] == user_pw:
                self.parent().set_message('로그인 성공!')
                self.parent().show_calculator()
                self.close()
            else:
                self.parent().set_message('아이디 또는 비밀번호가 잘못되었습니다.')
        else:
            self.parent().set_message('아이디와 비밀번호를 입력하세요.')

class CalculatorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('계산기')
        self.setGeometry(100, 100, 300, 400)
        self.layout = QVBoxLayout()

        self.display = QLineEdit(self)
        self.display.setReadOnly(True)
        self.layout.addWidget(self.display)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row, col = 0, 0
        for button in buttons:
            btn = QPushButton(button, self)
            btn.clicked.connect(self.on_button_click)
            self.grid_layout.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.setLayout(self.layout)

    def on_button_click(self):
        sender = self.sender()
        if sender.text() == '=':
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except:
                self.display.setText('Error')
        else:
            self.display.setText(self.display.text() + sender.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = FirebaseApp()
    mainWindow.show()
    sys.exit(app.exec_())