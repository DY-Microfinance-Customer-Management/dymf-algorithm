from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import math

class LoanCalculator:
    
    def __init__(self, start_date: datetime, principal: int, num_payments: int, cycle_days: int, annual_interest_rate: float = 0.28):
        self.start_date = start_date
        self.principal = principal
        self.num_payments = num_payments
        self.annual_interest_rate = annual_interest_rate
        self.cycle_days = cycle_days
        self.total_days = self.cycle_days * num_payments
        self.expire_date = start_date + relativedelta(days=self.total_days)

    def round_up_100(self, value):
        return math.ceil(value / 100) * 100

    def equal_payment(self) -> pd.DataFrame:
        period_interest_rate = self.annual_interest_rate / 365 * self.cycle_days
        # 매 상환 금액을 계산 후 100 단위로 올림
        amount_per_period = self.round_up_100(
            self.principal * period_interest_rate * (1 + period_interest_rate) ** self.num_payments /
            ((1 + period_interest_rate) ** self.num_payments - 1)
        )

        total_calculated = amount_per_period * self.num_payments  # 전체 상환 금액
        schedule = []
        current_date = self.start_date
        principal = self.principal

        for period in range(1, self.num_payments + 1):
            # 이자 계산 후 100 단위로 올림
            interest_payment = self.round_up_100(principal * period_interest_rate)
            # 원금 계산 후 100 단위로 올림
            principal_payment = self.round_up_100(amount_per_period - interest_payment)

            # 마지막 회차에서 잔액 조정
            if period == self.num_payments:
                # 남은 총 상환액과 마지막 회차에서의 총 상환액이 차이가 나면 그 차이를 조정
                remaining_difference = self.round_up_100(total_calculated - (principal_payment + interest_payment))
                if remaining_difference != 0:
                    principal_payment += remaining_difference  # 남은 차이만큼 마지막 원금 상환액에 반영
                amount_per_period = principal_payment + interest_payment  # 최종 상환 금액

            # 총 상환 금액에서 원금과 이자를 차감하여 남은 총 금액 계산
            total_calculated -= (principal_payment + interest_payment)

            # 상환 날짜 업데이트
            current_date += relativedelta(days=self.cycle_days)

            # 상환 스케줄 기록
            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': self.round_up_100(principal_payment),
                'Interest': interest_payment,
                'Total': self.round_up_100(amount_per_period),  # 100 단위로 올림
                'Remaining Balance': 0 if period == self.num_payments else self.round_up_100(total_calculated),  # 마지막 잔액은 0
            })

            # 원금에서 상환된 부분 차감
            principal -= principal_payment

        return pd.DataFrame(schedule)

    def round_to_100(self, value: float) -> int:
        return int(math.ceil(value / 100) * 100)

    def equal_principal_payment(self) -> pd.DataFrame:
        # 원금 상환액을 100 단위로 반올림
        principal_payment = self.round_to_100(self.principal / self.num_payments)
        period_interest_rate = self.annual_interest_rate / 365 * self.cycle_days

        schedule = []
        current_date = self.start_date
        principal = self.principal

        for period in range(1, self.num_payments + 1):
            # 이자 계산 후 100 단위로 반올림
            interest_payment = self.round_to_100(principal * period_interest_rate)
            amount_per_period = principal_payment + interest_payment

            if period == self.num_payments:
                # 마지막 회차에서 남은 모든 원금을 상환
                principal_payment = self.round_to_100(principal)
                amount_per_period = principal_payment + interest_payment

            # 원금에서 상환된 부분 차감
            principal -= principal_payment

            # 상환 날짜 업데이트
            current_date += relativedelta(days=self.cycle_days)

            # 스케줄 기록
            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': self.round_to_100(amount_per_period),
                'Remaining Balance': 0 if period == self.num_payments else self.round_to_100(principal),
            })

        return pd.DataFrame(schedule)

    def bullet_payment(self) -> pd.DataFrame:
        period_interest_rate = self.annual_interest_rate / 12

        schedule = []
        current_date = self.start_date
        principal = self.principal

        for period in range(1, self.num_payments + 1):
            # 이자 지급액을 100 단위로 반올림
            interest_payment = self.round_to_100(principal * period_interest_rate)

            current_date += relativedelta(days=self.cycle_days)

            if period == self.num_payments:
                # 마지막 회차에서 총 상환 금액과 원금 상환
                principal_payment = self.round_to_100(principal)
                total_payment = principal_payment + interest_payment
                principal = 0
            else:
                total_payment = interest_payment
                principal_payment = 0

            # 총 상환액과 잔액을 반올림하여 기록
            schedule.append({
                'Period': period,
                'Payment Date': current_date.strftime('%Y-%m-%d'),
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Total': self.round_to_100(total_payment),
                'Remaining Balance': 0 if period == self.num_payments else self.round_to_100(principal),
            })

        return pd.DataFrame(schedule)

    def overdue_interest(self, amount: int, overdue_days: int, overdue_interest_rate: float) -> int:
        overdue_interest = amount * (overdue_interest_rate / 365 * overdue_days)

        return overdue_interest
