from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

class LoanCalculator:
    
    def __init__(self, start_date: datetime, principal: int, num_payments: int, cycle_days: int, annual_interest_rate: float = 0.28):
        self.start_date = start_date
        self.principal = principal
        self.num_payments = num_payments
        self.annual_interest_rate = annual_interest_rate
        self.cycle_days = cycle_days
        self.total_days = self.cycle_days * num_payments
        self.expire_date = start_date + relativedelta(days=self.total_days)

    def equal_payment(self) -> pd.DataFrame:
        period_interest_rate = self.annual_interest_rate / 365 * self.cycle_days
        # 매 상환 금액을 계산 후 반올림 (100 단위로 반올림)
        amount_per_period = round(
            self.principal * period_interest_rate * (1 + period_interest_rate) ** self.num_payments /
            ((1 + period_interest_rate) ** self.num_payments - 1), -2
        )

        total_calculated = amount_per_period * self.num_payments  # 전체 상환 금액
        schedule = []
        current_date = self.start_date
        principal = self.principal

        for period in range(1, self.num_payments + 1):
            # 이자 계산 후 100 단위로 반올림
            interest_payment = round(principal * period_interest_rate, -2)
            # 원금 계산 후 100 단위로 반올림
            principal_payment = round(amount_per_period - interest_payment, -2)

            # 마지막 회차에서 잔액 조정
            if period == self.num_payments:
                principal_payment = round(principal, -2)  # 남은 모든 원금을 상환
                amount_per_period = principal_payment + interest_payment  # 최종 상환 금액

                # 남은 총 상환액과 마지막 회차에서의 총 상환액이 차이가 나면 그 차이를 조정
                remaining_difference = total_calculated - (principal_payment + interest_payment)
                if round(remaining_difference, -2) != 0:
                    principal_payment += round(remaining_difference, -2)  # 남은 차이만큼 마지막 원금 상환액에 반영
                    amount_per_period = principal_payment + interest_payment
                    total_calculated = 0  # 마지막 상환 후 잔액을 0으로 설정

            # 총 상환 금액에서 원금과 이자를 차감하여 남은 총 금액 계산
            total_calculated -= (principal_payment + interest_payment)

            # 상환 날짜 업데이트
            current_date += relativedelta(days=self.cycle_days)

            # 상환 스케줄 기록
            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': round(amount_per_period, -2),  # 100 단위로 반올림
                'Remaining Balance': 0 if period == self.num_payments else round(total_calculated, -2),  # 마지막 잔액은 0
            })

            # 원금에서 상환된 부분 차감
            principal -= principal_payment

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
            
            current_date += relativedelta(days=self.cycle_days)

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
            
            current_date += relativedelta(days=self.cycle_days)

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
