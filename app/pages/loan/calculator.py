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

class LoanCalculator:
    
    def __init__(self, start_date: datetime, principal: int, expiration_months: int, annual_interest_rate: float=0.28):
        self.start_date = start_date
        self.principal = principal
        self.expiration_months = expiration_months
        self.annual_interest_rate = annual_interest_rate
        self.expire_date = start_date + relativedelta(months=expiration_months)
        self.total_days = (self.expire_date - start_date).days
        
    def _get_schedule_details(self, cycle: str) -> Tuple[int, int]:
        if cycle == 'month':
            cycle_cnt = 12
            total_period = self.expiration_months
        elif cycle == '4week':
            cycle_cnt = 13
            total_period = math.ceil(self.total_days / 28)
        elif cycle == '2week':
            cycle_cnt = 26
            total_period = math.ceil(self.total_days / 14)
        elif cycle == 'week':
            cycle_cnt = 52
            total_period = math.ceil(self.total_days / 7)
        return cycle_cnt, total_period
    
    def equal_payment(self, cycle: str='month') -> pd.DataFrame:
        cycle_cnt, total_period = self._get_schedule_details(cycle)
        period_interest_rate = ((1 + self.annual_interest_rate / cycle_cnt) ** total_period) - 1
        amount_per_period = round((self.principal * self.annual_interest_rate / cycle_cnt * (1 + self.annual_interest_rate / cycle_cnt) ** total_period) / period_interest_rate)
        
        schedule = []
        current_date = self.start_date
        principal = self.principal
        total_principal_payment = total_interest_payment = total_principal_n_interest = 0
        
        for period in range(1, total_period + 1):
            interest_payment = round(principal * self.annual_interest_rate / cycle_cnt)
            principal_payment = round(amount_per_period - interest_payment)
            principal -= principal_payment

            total_principal_payment += principal_payment
            total_interest_payment += interest_payment
            total_principal_n_interest += amount_per_period

            current_date += relativedelta(months=1) if cycle == 'month' else relativedelta(weeks=int(cycle[:-4]) if 'week' in cycle else 1)

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d (%A)'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': amount_per_period,
                'Remaining Balance': round(principal),
            })

        schedule.append({
            'Period': 'Total',
            'Payment Date': '-',
            'Principal': total_principal_payment,
            'Interest': total_interest_payment,
            'Total': total_principal_n_interest,
            'Remaining Balance': '-',
        })
        
        return pd.DataFrame(schedule)
    
    def equal_principal_payment(self, cycle: str='month') -> pd.DataFrame:
        cycle_cnt, total_period = self._get_schedule_details(cycle)
        period_interest_rate = self.annual_interest_rate / cycle_cnt
        
        schedule = []
        current_date = self.start_date
        principal = self.principal
        principal_payment = round(principal / total_period)
        total_principal_payment = total_interest_payment = total_principal_n_interest = 0
        
        for period in range(1, total_period + 1):
            interest_payment = round(principal * period_interest_rate)
            amount_per_period = principal_payment + interest_payment
            principal -= principal_payment

            total_principal_payment += principal_payment
            total_interest_payment += interest_payment
            total_principal_n_interest += amount_per_period

            current_date += relativedelta(months=1) if cycle == 'month' else relativedelta(weeks=int(cycle[:-4]) if 'week' in cycle else 1)

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d (%A)'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': amount_per_period,
                'Remaining Balance': round(principal),
            })

        schedule.append({
            'Period': 'Total',
            'Payment Date': '-',
            'Principal': total_principal_payment,
            'Interest': total_interest_payment,
            'Total': total_principal_n_interest,
            'Remaining Balance': '-',
        })
        
        return pd.DataFrame(schedule)
    
    def bullet_payment(self, cycle: str='month') -> pd.DataFrame:
        cycle_cnt, total_period = self._get_schedule_details(cycle)
        period_interest_rate = self.annual_interest_rate / cycle_cnt
        
        schedule = []
        current_date = self.start_date
        principal = self.principal
        total_interest_payment = total_principal_n_interest = 0
        
        for period in range(1, total_period + 1):
            interest_payment = round(principal * period_interest_rate)
            total_interest_payment += interest_payment
            total_principal_n_interest += interest_payment

            current_date += relativedelta(months=1) if cycle == 'month' else relativedelta(weeks=int(cycle[:-4]) if 'week' in cycle else 1)

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d (%A)'),
                'Principal': 0,
                'Interest': interest_payment,
                'Total': interest_payment,
                'Remaining Balance': round(principal),
            })

        total_principal_payment = principal
        schedule.append({
            'Period': 'Total',
            'Payment Date': '-',
            'Principal': total_principal_payment,
            'Interest': total_interest_payment,
            'Total': total_principal_n_interest + principal,
            'Remaining Balance': '-',
        })
        
        return pd.DataFrame(schedule)

# Load the UI file directly
Ui_Calculator, _ = uic.loadUiType("calculator.ui")

class CalculatorApp(QMainWindow, Ui_Calculator):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Set up the UI components

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

    # def display_result(self, df: pd.DataFrame):
    #     vertical_header = [str(i) for i in df['Period'].values]
    #     df = df.drop(columns=['Period'])
    #     model = QStandardItemModel(df.shape[0], df.shape[1])
    #     model.setHorizontalHeaderLabels(df.columns.tolist())
    #     model.setVerticalHeaderLabels(vertical_header)
        
    #     for row in range(df.shape[0]):
    #         for col in range(df.shape[1]):
    #             item = QStandardItem(str(df.iat[row, col]))
    #             item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item non-editable
    #             model.setItem(row, col, item)
        
    #     self.resultTable.setModel(model)
    #     self.resultTable.resizeColumnsToContents()

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
