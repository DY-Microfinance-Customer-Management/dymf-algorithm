import sys
import os
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QLineEdit
from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal

from src.components import DB

class SelectLoanWindow(QMainWindow):
    loan_selected = pyqtSignal(dict)

    def __init__(self):
        super(SelectLoanWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "select_loan.ui")
        uic.loadUi(ui_path, self)
        
        self.searchBox = self.findChild(QLineEdit, "searchBox")
        self.tableView = self.findChild(QTableView, "tableView")

        self.tableView.setSelectionBehavior(QTableView.SelectRows)

        self.searchBox.textChanged.connect(self.filter_data)

        self.tableView.clicked.connect(self.handle_table_click)
        self.tableView.doubleClicked.connect(self.handle_table_double_click)

        self.load_data()

    def load_data(self):
        loans_ref = DB.collection(u'Overdue')
        docs = loans_ref.stream()

        data = []
        self.all_loans = {}  # 전체 데이터를 저장할 딕셔너리

        for doc in docs:
            loan_data = doc.to_dict()
            loan_data['id'] = doc.id  # document ID를 포함
            self.all_loans[loan_data['loan_number']] = loan_data  # loan_number를 키로 전체 데이터를 저장

            # 필요한 열만 추출하여 테이블에 표시 (열 이름 변경)
            filtered_loan_data = {
                'Loan No.': loan_data.get('loan_number', ''),
                'Customer Name': loan_data.get('customer_name', ''),
                'Loan Officer': loan_data.get('loan_officer', '')
            }
            data.append(filtered_loan_data)

        self.df = pd.DataFrame(data)
        self.filtered_df = self.df.copy()
        self.model = PandasModel(self.filtered_df)
        self.tableView.setModel(self.model)

    def filter_data(self):
        search_text = self.searchBox.text().lower()
        self.filtered_df = self.df[self.df['Loan No.'].str.lower().str.contains(search_text)]
        self.model._df = self.filtered_df
        self.model.layoutChanged.emit()

    def handle_table_click(self, index):
        if index.isValid():
            row = index.row()
            selected_data = self.filtered_df.iloc[row].to_dict()

    def handle_table_double_click(self, index):
        if index.isValid():
            row = index.row()
            selected_data = self.filtered_df.iloc[row].to_dict()
            loan_number = selected_data['Loan No.']

            # 전체 loan_data에서 해당 loan_number로 전체 데이터를 찾아서 전달
            full_loan_data = self.all_loans.get(loan_number, {})
            self.loan_selected.emit(full_loan_data)
            self.close()

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return section
        return None

def main():
    app = QApplication(sys.argv)
    window = SelectLoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()