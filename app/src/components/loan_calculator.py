from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

class LoanCalculator:
    
    def __init__(self, start_date: datetime, principal: int, num_payments: int, annual_interest_rate: float = 0.28):
        self.start_date = start_date
        self.principal = principal
        self.num_payments = num_payments
        self.annual_interest_rate = annual_interest_rate
        self.payment_interval_days = 30
        self.total_days = self.payment_interval_days * num_payments
        self.expire_date = start_date + relativedelta(days=self.total_days)

    def equal_payment(self) -> pd.DataFrame:
        period_interest_rate = self.annual_interest_rate / 12
        amount_per_period = self.principal * period_interest_rate * (1 + period_interest_rate) ** self.num_payments / ((1 + period_interest_rate) ** self.num_payments - 1)
        amount_per_period = round(amount_per_period)
        
        schedule = []
        current_date = self.start_date
        principal = self.principal

        for period in range(1, self.num_payments + 1):
            interest_payment = round(principal * period_interest_rate)
            principal_payment = round(amount_per_period - interest_payment)
            
            if period == self.num_payments:
                principal_payment = principal
                amount_per_period = principal_payment + interest_payment
                
            principal -= principal_payment

            current_date += relativedelta(days=self.payment_interval_days)

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': amount_per_period,
                'Remaining Balance': round(principal),
            })
        
        return pd.DataFrame(schedule)
    
    def equal_principal_payment(self) -> pd.DataFrame:
        principal_payment = round(self.principal / self.num_payments)
        period_interest_rate = self.annual_interest_rate / 12
        
        schedule = []
        current_date = self.start_date
        principal = self.principal
        
        for period in range(1, self.num_payments + 1):
            interest_payment = round(principal * period_interest_rate)
            amount_per_period = principal_payment + interest_payment
            
            if period == self.num_payments:
                principal_payment = principal
                amount_per_period = principal_payment + interest_payment
            
            principal -= principal_payment
            
            current_date += relativedelta(days=self.payment_interval_days)

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': amount_per_period,
                'Remaining Balance': round(principal),
            })
        
        return pd.DataFrame(schedule)
    
    def bullet_payment(self) -> pd.DataFrame:
        period_interest_rate = self.annual_interest_rate / 12
        
        schedule = []
        current_date = self.start_date
        principal = self.principal
        
        for period in range(1, self.num_payments + 1):
            interest_payment = round(principal * period_interest_rate)
            
            current_date += relativedelta(days=self.payment_interval_days)

            if period == self.num_payments:
                total_payment = principal + interest_payment
                principal_payment = principal
                principal = 0
            else:
                total_payment = interest_payment
                principal_payment = 0

            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': total_payment,
                'Remaining Balance': round(principal),
            })
        
        return pd.DataFrame(schedule)
    
    def overdue_interest(self, amount: int, overdue_days: int, overdue_interest_rate: float) -> int:
        overdue_interest = amount * (overdue_interest_rate / 365 * overdue_days)

        return overdue_interest
