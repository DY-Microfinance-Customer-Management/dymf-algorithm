import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.ui_company_info import Ui_MainWindow  # design.py 파일에서 UI 클래스를 가져옵니다

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 초기화

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
