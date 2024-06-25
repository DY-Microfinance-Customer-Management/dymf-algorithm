import sys

from PyQt5.QtCore import QDate, Qt, QTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QDesktopWidget

now = QDate.currentDate()
print(now.toString(Qt.ISODate))

time = QTime.currentTime()
print(time.toString())

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Customer Submenus        
        customerRegistrationAction = QAction('Registeration', self)
        customerRegistrationAction.setStatusTip('Register Customer')
        customerSearchAction = QAction('Search', self)
        customerSearchAction.setStatusTip('Search Customer')

        # General Submenus
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # Define Menubar
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # Add Menu to Menubar
        CustomerMenu = menubar.addMenu('&Customer')
        CustomerMenu.addAction(customerRegistrationAction)
        CustomerMenu.addAction(customerSearchAction)
        GeneralMenu = menubar.addMenu('&General')
        GeneralMenu.addAction(exitAction)




        # Window Default Options
        self.setWindowTitle('DY Microfinance')
        self.setWindowIcon(QIcon('dy_logo.jpg'))
        self.resize(1000, 600)
        self.center()
        self.show()

    # Functions
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
