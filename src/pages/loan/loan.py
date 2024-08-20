import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel
import pandas as pd
from components import DB

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "eng_loan.ui")
        uic.loadUi(ui_path, self)
        
        # Connect the search button to the function
        self.customerSearchButton.clicked.connect(self.open_select_customer_window)
        self.show()

    def open_select_customer_window(self):
        from pages.loan.select_customer import SelectCustomerWindow  # import the SelectCustomerWindow class
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.show()

    def set_customer_data(self, customer_data):
        self.customerName.setText(customer_data.get('name', ''))
        self.customerID.setText(customer_data.get('customer_id', ''))
        self.customerAddress.setText(customer_data.get('address', ''))
        # Add other fields as necessary

def main():
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
