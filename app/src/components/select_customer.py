import sys
import os
import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QLineEdit
from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal
from PyQt5.QtGui import QIcon

from src.components import DB

class SelectCustomerWindow(QMainWindow):
    customer_selected = pyqtSignal(dict)

    def __init__(self):
        super(SelectCustomerWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "select_customer.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.searchBox = self.findChild(QLineEdit, "searchBox")
        self.tableView = self.findChild(QTableView, "tableView")

        self.tableView.setSelectionBehavior(QTableView.SelectRows)

        self.searchBox.textChanged.connect(self.filter_data)

        self.tableView.clicked.connect(self.handle_table_click)
        self.tableView.doubleClicked.connect(self.handle_table_double_click)

        self.load_data()

    def load_data(self):
        customers_ref = DB.collection(u'Customer')
        docs = customers_ref.stream()

        data = []
        for doc in docs:
            customer_data = doc.to_dict()
            customer_data['customer_uid'] = doc.id  # UID 추가
            data.append(customer_data)

        self.df = pd.DataFrame(data)

        # 핸드폰 번호를 하나의 문자열로 합침
        self.df['Phone No.'] = self.df[['phone1', 'phone2', 'phone3']].apply(lambda x: '-'.join(filter(None, x)), axis=1)

        # 표시할 열만 선택
        self.display_df = self.df[['name', 'date_of_birth', 'Phone No.', 'loan_officer']]

        self.filtered_df = self.display_df.copy()
        self.model = PandasModel(self.filtered_df)
        self.tableView.setModel(self.model)

    def filter_data(self):
        search_text = self.searchBox.text().lower()
        self.filtered_df = self.display_df[self.display_df['name'].str.lower().str.contains(search_text)]
        self.model._df = self.filtered_df
        self.model.layoutChanged.emit()

    def handle_table_click(self, index):
        if index.isValid():
            row = index.row()
            selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()

    def handle_table_double_click(self, index):
        if index.isValid():
            row = index.row()
            selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()
            self.customer_selected.emit(selected_data)
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
    window = SelectCustomerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()