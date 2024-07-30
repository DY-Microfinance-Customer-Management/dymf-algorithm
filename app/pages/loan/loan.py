import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel
import pandas as pd
from fire import db

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi("eng_loan.ui", self)
        
        # Connect the search button to the function
        self.customerSearchButton.clicked.connect(self.open_select_customer_window)
        self.show()

    def open_select_customer_window(self):
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.show()

class SelectCustomerWindow(QMainWindow):
    def __init__(self):
        super(SelectCustomerWindow, self).__init__()
        uic.loadUi("select_customer.ui", self)
        
        self.tableView = self.findChild(QTableView, "tableView")
        self.load_data()

    def load_data(self):
        # Firestore에서 데이터 가져오기
        customers_ref = db.collection(u'Customer')
        docs = customers_ref.stream()

        data = []
        for doc in docs:
            data.append(doc.to_dict())

        df = pd.DataFrame(data)
        self.model = PandasModel(df)
        self.tableView.setModel(self.model)

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
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()