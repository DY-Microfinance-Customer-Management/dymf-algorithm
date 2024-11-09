# DY Microfinance
- Loan Program developed by PyQt5
- [PyQt5 Doc](https://wikidocs.net/21849)

### Execute
```
cd app
python dymf.py
```

### Installation
```
pip install firebase-admin
pip install PyQt5
pip install pyqt5-tools
```

### Git Force Pull
```
git fetch --all
git reset --hard origin/master
git pull origin master
```

### Build
```
pyinstaller --onefile --icon=src/icon.ico --noconsole --add-data="src/pages/customer/icon.ico:src/pages/customer" --add-data="src/pages/loan/icon.ico:src/pages/loan" --add-data="src/pages/main/icon.ico:src/pages/main" --add-data="src/pages/overdue/icon.ico:src/pages/overdue" --add-data="src/pages/repayment/icon.ico:src/pages/repayment" --add-data="src/pages/setting/icon.ico:src/pages/setting" --add-data="src/pages/main/dymf_logo.png:src/pages/main" --add-data="src/components/dymfsys-firebase-adminsdk-3fkh3-957df8a288.json:." --add-data="src/pages/customer/registration.ui:src/pages/customer" --add-data="src/pages/loan/calculator.ui:src/pages/loan" --add-data="src/pages/loan/collateral_search.ui:src/pages/loan" --add-data="src/pages/loan/counseling_search.ui:src/pages/loan" --add-data="src/pages/loan/guarantor_search.ui:src/pages/loan" --add-data="src/pages/loan/kor_loan.ui:src/pages/loan" --add-data="src/pages/loan/loan.ui:src/pages/loan" --add-data="src/pages/loan/select_customer.ui:src/pages/loan" --add-data="src/pages/main/login.ui:src/pages/main" --add-data="src/pages/main/home.ui:src/pages/main" --add-data="src/pages/overdue/overdue_loan_management.ui:src/pages/overdue" --add-data="src/pages/overdue/overdue_loan_registration.ui:src/pages/overdue" --add-data="src/pages/overdue/select_loan.ui:src/pages/overdue" --add-data="src/pages/repayment/details.ui:src/pages/repayment" --add-data="src/pages/repayment/repayment_search.ui:src/pages/repayment" --add-data="src/pages/setting/loan_officer.ui:src/pages/setting" --add-data="src/pages/setting/user_management.ui:src/pages/setting" dymf.py

pyinstaller --noconfirm --onefile --icon=src/icon.ico --noconsole --add-data="src/components/dymfsys-firebase-adminsdk-3fkh3-ca4acef8e5.json:." --add-data="src/components/icon.ico:src/components" --add-data="src/pages/main/dymf_logo.png:src/pages/main" --add-data="src/pages/main/home.ui:src/pages/main" --add-data="src/pages/main/icon.ico:src/pages/main" --add-data="src/pages/main/login.ui:src/pages/main" --add-data="src/pages/overdue/icon.ico:src/pages/overdue" --add-data="src/pages/overdue/management.ui:src/pages/overdue" --add-data="src/pages/overdue/post_registration.ui:src/pages/overdue" --add-data="src/pages/overdue/registration.ui:src/pages/overdue" --add-data="src/pages/overdue/search.ui:src/pages/overdue" --add-data="src/pages/registration/icon.ico:src/pages/registration" --add-data="src/pages/registration/calculator.ui:src/pages/registration" --add-data="src/pages/registration/customer.ui:src/pages/registration" --add-data="src/pages/registration/guarantor.ui:src/pages/registration" --add-data="src/pages/registration/loan.ui:src/pages/registration" --add-data="src/pages/repayment/icon.ico:src/pages/repayment" --add-data="src/pages/repayment/batch.ui:src/pages/repayment" --add-data="src/pages/repayment/details.ui:src/pages/repayment" --add-data="src/pages/repayment/single.ui:src/pages/repayment" --add-data="src/pages/search/icon.ico:src/pages/search" --add-data="src/pages/search/collateral.ui:src/pages/search" --add-data="src/pages/search/counseling.ui:src/pages/search" --add-data="src/pages/search/customer.ui:src/pages/search" --add-data="src/pages/search/guarantor.ui:src/pages/search" --add-data="src/pages/search/loan.ui:src/pages/search" --add-data="src/pages/search/loan_details.ui:src/pages/search" --add-data="src/pages/settings/icon.ico:src/pages/settings" --add-data="src/pages/settings/officer.ui:src/pages/settings" --add-data="src/pages/settings/user.ui:src/pages/settings" --add-data="src/pages/report/periodic_balance.ui:src/pages/report" --add-data="src/pages/personnel/registration.ui:src/pages/personnel" dymf.py
```

- 코드를 제외한 모든 파일은 현재 디렉토리를 기준으로 os.path.join(current_dir, '파일명') 참조되어야 함
- 참조된 모든 파일들은 빌드할 때 --add-data 옵션으로 추가해야 함
- app 폴더 내부에서 실행