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
pyinstaller --add-data "src/components/test-hungun-firebase-adminsdk-rl8wp-7e30142f0f.json;." --onefile dymf.py
```