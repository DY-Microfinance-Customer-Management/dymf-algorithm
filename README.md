# DYMF Algorithm (DY-Microfinance Algorithm)

마이크로파이낸스 대출 계산 알고리즘입니다. 다양한 대출 상품에 대한 이자 계산, 상환 일정 생성, 고객 신용 평가 등의 기능을 제공합니다.

## 프로젝트 개요

이 프로젝트는 DY마이크로파이낸스에서 소액 대출 업무를 효율적으로 관리하기 위해 개발한 데스크톱 애플리케이션입니다. 복잡한 대출 금리 계산, 상환 스케줄 생성, 고객별 대출 이력 관리를 자동화합니다.

**핵심 기능:**
- 원리금 균등상환 및 원금 균등상환 계산
- 유연한 대출 기간 및 이자율 설정
- 실시간 상환 계획 시뮬레이션
- CSV 파일 기반 대량 고객 관리

---

## 핵심 구현: 유연한 상환 주기

### 미얀마 금융 시장의 특수성

일반적인 대출 계산 시스템은 **월별 상환**을 전제로 설계되지만, 미얀마 마이크로파이낸스 시장에서는:
- **월별(month)**: 전통적인 상환 방식
- **4주(4week)**: 농업 및 소규모 사업자 대출
- **2주(2week)**: 일용직 노동자를 위한 단기 대출
- **주간(week)**: 초단기 소액 대출

등 다양한 상환 주기가 혼재되어 사용됩니다.

### 기술적 해결 방법

#### 1. `cycle`과 `period` 분리 계산

```python
# cycle 설정: 상환 주기 선택
cycle: str = ['month', '4week', '2week', 'week']

# cycle_cnt: 연간 상환 횟수
if cycle == 'month':
    cycle_cnt = 12
elif cycle == '4week':
    cycle_cnt = 13  # 52주 / 4주
elif cycle == '2week':
    cycle_cnt = 26  # 52주 / 2주
elif cycle == 'week':
    cycle_cnt = 52

# total_period: 실제 상환 횟수 (일수 기반 계산)
total_days = (expire_date - start_date).days
if cycle == 'month':
    total_period = expiration_months
else:
    total_period = math.ceil(total_days / cycle_days)
```

#### 2. 주기별 이자율 자동 변환

```python
# 연 이자율을 상환 주기에 맞게 변환
period_interest_rate = annual_interest_rate / cycle_cnt

# 예시: 연 28% 이자율
# - 월별(12회): 28% / 12 = 2.33% per period
# - 4주별(13회): 28% / 13 = 2.15% per period  
# - 주간(52회): 28% / 52 = 0.54% per period
```

#### 3. 날짜 증가 로직

```python
# 주기에 따라 다음 상환일 계산
if cycle == 'month':
    current_date += relativedelta(months=1)
else:
    weeks = int(cycle[:-4]) if 'week' in cycle else 1
    current_date += relativedelta(weeks=weeks)
```

### 구현의 의미

이 설계를 통해:
- 단순히 월별 이자율을 12로 나누는 것이 아니라, **실제 상환 주기를 반영한 정확한 이자 계산**
- 대출 기간이 정확히 1년이 아닌 경우에도 **일수 기반으로 정확한 상환 횟수 산출**
- 동일한 알고리즘으로 **4가지 다른 상환 주기를 모두 처리**

**기존 방식**: 월별 고정 → 주간 상환 시 오차 발생  
**본 시스템**: 주기별 동적 계산 → 모든 케이스에서 정확한 계산

---

## 만든 알고리즘

### 1. 대출 이자 계산 알고리즘

#### 원리금 균등상환 (Equal Payment Loan / Amortized Loan)

**목표:** 매 주기마다 동일한 금액으로 원금과 이자를 함께 상환하는 방식

**주기별 상환액 계산식:**
```
M = P × [r(1 + r)^n] / [(1 + r)^n - 1]
```

**변수:**
- `M`: 주기별 상환액
- `P`: 대출 원금
- `r`: 주기별 이자율 (연 이자율 / cycle_cnt)
- `n`: 총 상환 횟수

**상환 일정 계산:**
- 매 주기 이자금 = 남은 원금 × 주기별 이자율
- 매 주기 원금 = 주기별 상환액 - 주기 이자금

#### 원금 균등상환 (Equal Principal Payment Loan)

**목표:** 매 주기마다 동일한 원금을 상환하고, 이자는 감소하는 방식

**주기별 상환액 계산식:**
```
Mt = P/n + [P - P(t-1)/n] × r
```

**변수:**
- `Mt`: t번째 주기의 상환액
- `P`: 대출 원금
- `n`: 총 상환 횟수
- `r`: 주기별 이자율
- `t`: 현재 상환 회차

**특징:**
- 초기 상환액이 높고, 시간이 지나면서 감소
- 원리금 균등상환보다 총 이자금이 적음
- 고객이 초기 부담이 큼

#### 만기일시상환 (Bullet Payment / Interest-Only Loan)

**목표:** 대출 기간 동안 이자만 납부하고 만기에 원금을 일시 상환하는 방식

**계산식:**
```
매 주기 이자 = P × r
만기 상환액 = P + (총 이자)
```

**특징:**
- 상환 부담이 만기에 집중
- 현금 흐름 관리가 용이한 사업자에게 적합
- 총 이자 부담이 가장 큼
