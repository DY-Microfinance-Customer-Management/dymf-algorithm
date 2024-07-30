import sys
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from loan_calculator import LoanCalculator

class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("calculator.ui", self)
        self.show()

        # Connect the Calculate button to the function
        self.calculateButton.clicked.connect(self.calculate)

        # Set validators to ensure only numbers can be entered
        self.principal.setValidator(QDoubleValidator(0.0, 99999999.99, 2, self))
        self.interestRate.setValidator(QDoubleValidator(0.0, 100.0, 2, self))
        self.expirationMonths.setValidator(QIntValidator(0, 1200, self))

    def calculate(self):
        try:
            # Get input values
            principal = float(self.principal.text())
            interest_rate = float(self.interestRate.text()) / 100  # Convert percentage to decimal
            expiration_months = int(self.expirationMonths.text())
            cycle = self.cycle.currentText().lower().replace(' ', '')
            payment_type = self.paymentType.currentText().lower().replace(' ', '')

            # Create a LoanCalculator instance
            loan_calculator = LoanCalculator(datetime.now(), principal, expiration_months, interest_rate)
            
            # Calculate the result based on the selected payment type
            if payment_type == 'equal':
                result_df = loan_calculator.equal_payment(cycle)
            elif payment_type == 'equalprincipal':
                result_df = loan_calculator.equal_principal_payment(cycle)
            elif payment_type == 'bullet':
                result_df = loan_calculator.bullet_payment(cycle)

            # Display the result DataFrame in the resultTable
            self.display_result(result_df)

        except ValueError:
            print("Invalid input. Please enter numeric values.")

    def display_result(self, df: pd.DataFrame):
        vertical_header = [str(i) for i in df['Period'].values]
        df = df.drop(columns=['Period'])
        
        # Define a function to format numbers with commas
        def format_number(value):
            try:
                return "{:,}".format(int(value))  # Format with commas and 2 decimal places
            except ValueError:
                return value  # Return the value as-is if it's not a number
        
        # Apply formatting to all numerical columns
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
