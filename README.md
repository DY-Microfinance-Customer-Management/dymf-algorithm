# DY Microfinance
- Loan Program developed by Tkinter
- [PyQt5 Doc](https://wikidocs.net/21849)

### Installation
```
pip install firebase-admin
pip install PyQt5
pip install pyqt5-tools
```

### Change .ui file into .py
```
pyuic5 login_page.ui -o ui_login_page.py
```

### Git Force Pull
```
git fetch --all
git reset --hard origin/master
git pull origin master
```

### Stylesheet example
```
ui->textBrowser_1->setStyleSheet("background-color: rgb(238, 238, 236);");
```

### Build
```
pyinstaller --onefile --icon=src/icon.ico --noconsole --add-data="src/pages/customer/icon.ico;src/pages/customer" --add-data="src/pages/loan/icon.ico;src/pages/loan" --add-data="src/pages/main/icon.ico;src/pages/main" --add-data="src/pages/overdue/icon.ico;src/pages/overdue" --add-data="src/pages/repayment/icon.ico;src/pages/repayment" --add-data="src/pages/setting/icon.ico;src/pages/setting" --add-data="src/pages/main/dymf_logo.png;src/pages/main" --add-data="src/pages/main/dymf_logo.qrc;src/pages/main" --add-data="src/components/dymfsys-firebase-adminsdk-3fkh3-957df8a288.json;." --add-data="src/pages/customer/registration.ui;src/pages/customer" --add-data="src/pages/loan/calculator.ui;src/pages/loan" --add-data="src/pages/loan/collateral_search.ui;src/pages/loan" --add-data="src/pages/loan/counseling_search.ui;src/pages/loan" --add-data="src/pages/loan/guarantor_search.ui;src/pages/loan" --add-data="src/pages/loan/kor_loan.ui;src/pages/loan" --add-data="src/pages/loan/loan.ui;src/pages/loan" --add-data="src/pages/loan/select_customer.ui;src/pages/loan" --add-data="src/pages/main/login.ui;src/pages/main" --add-data="src/pages/main/home.ui;src/pages/main" --add-data="src/pages/overdue/overdue_loan_management.ui;src/pages/overdue" --add-data="src/pages/overdue/overdue_loan_registration.ui;src/pages/overdue" --add-data="src/pages/overdue/select_loan.ui;src/pages/overdue" --add-data="src/pages/repayment/details.ui;src/pages/repayment" --add-data="src/pages/repayment/repayment_search.ui;src/pages/repayment" --add-data="src/pages/setting/loan_officer.ui;src/pages/setting" --add-data="src/pages/setting/user_management.ui;src/pages/setting" dymf.py
```