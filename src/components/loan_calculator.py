import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Tuple

import pandas as pd

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
    
    def overdue_interest(self, loan_period_years: int, overdue_days: int, overdue_interest_rate: float) -> int:
        loan_period_months = loan_period_years * 12
        monthly_interest_rate = self.annual_interest_rate / 12
        monthly_payment = self.principal * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_period_months) / ((1 + monthly_interest_rate) ** loan_period_months - 1)
        overdue_amount = monthly_payment
        overdue_interest = overdue_amount * (overdue_days * overdue_interest_rate / 365)
        
        return overdue_interest