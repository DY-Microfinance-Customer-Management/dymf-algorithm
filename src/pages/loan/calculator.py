import sys
import os
from datetime import datetime

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from src.components.loan_calculator import LoanCalculator

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "calculator.ui")
        uic.loadUi(ui_path, self)
        self.show()

        self.calculateButton.clicked.connect(self.calculate)

        self.principal.setValidator(QDoubleValidator(0.0, 99999999.99, 2, self))
        self.interestRate.setValidator(QDoubleValidator(0.0, 100.0, 2, self))
        self.expirationMonths.setValidator(QIntValidator(0, 1200, self))

    def calculate(self):
        try:
            principal = float(self.principal.text())
            interest_rate = float(self.interestRate.text()) / 100  # Convert percentage to decimal
            expiration_months = int(self.expirationMonths.text())
            cycle = self.cycle.currentText().lower().replace(' ', '')
            payment_type = self.paymentType.currentText().lower().replace(' ', '')

            loan_calculator = LoanCalculator(datetime.now(), principal, expiration_months, interest_rate)
            
            if payment_type == 'equal':
                result_df = loan_calculator.equal_payment(cycle)
            elif payment_type == 'equalprincipal':
                result_df = loan_calculator.equal_principal_payment(cycle)
            elif payment_type == 'bullet':
                result_df = loan_calculator.bullet_payment(cycle)

            self.display_result(result_df)

        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def display_result(self, df: pd.DataFrame):
        vertical_header = [str(i) for i in df['Period'].values]
        df = df.drop(columns=['Period'])
        
        def format_number(value):
            try:
                return "{:,}".format(int(value))
            except ValueError:
                return value
        
        for column in df.columns:
            df[column] = df[column].apply(format_number)
        
        model = QStandardItemModel(df.shape[0], df.shape[1])
        model.setHorizontalHeaderLabels(df.columns.tolist())
        model.setVerticalHeaderLabels(vertical_header)
        
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(df.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item non-editable
                model.setItem(row, col, item)
        
        self.resultTable.setModel(model)
        self.resultTable.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CalculatorApp()
    main_window.show()
    sys.exit(app.exec_())
