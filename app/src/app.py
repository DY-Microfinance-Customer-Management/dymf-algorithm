import os
import sys
from PyQt5.QtWidgets import QApplication

# Use relative import paths directly
from src.pages.main.login import LoginApp

def main():
    app = QApplication(sys.argv)
    window = LoginApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
