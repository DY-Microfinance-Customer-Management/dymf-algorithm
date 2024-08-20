import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QPushButton
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QItemDelegate
import pandas as pd
from components import DB

class SelectCustomerWindow(QMainWindow):
    def __init__(self):
        super(SelectCustomerWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "select_customer.ui")
        uic.loadUi(ui_path, self)
        
        self.tableView = self.findChild(QTableView, "tableView")
        self.load_data()

    def load_data(self):
        # Firestore에서 데이터 가져오기
        customers_ref = DB.collection(u'Customer')
        docs = customers_ref.stream()

        data = []
        for doc in docs:
            data.append(doc.to_dict())

        self.df = pd.DataFrame(data)
        self.model = PandasModel(self.df)
        self.tableView.setModel(self.model)

        # Set ButtonDelegate for the last column
        delegate = ButtonDelegate(self.tableView, self.df)
        self.tableView.setItemDelegateForColumn(self.df.shape[1], delegate)

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1] + 1  # Add one column for the button

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                if index.column() == self._df.shape[1]:
                    return "Select"
                return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self._df.shape[1]:
                    return "Action"
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return section
        return None

class ButtonDelegate(QItemDelegate):
    def __init__(self, parent=None, df=pd.DataFrame()):
        super(ButtonDelegate, self).__init__(parent)
        self._df = df
    
    def createEditor(self, parent, option, index):
        button = QPushButton(parent)
        button.setText("Select")
        button.clicked.connect(lambda: self.handle_button_click(index))
        return button

    def setEditorData(self, editor, index):
        pass

    def setModelData(self, editor, model, index):
        pass

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def handle_button_click(self, index):
        if index.isValid():
            row = index.row()
            selected_data = self._df.iloc[row].to_dict()
            print(f"Selected data: {selected_data}")
            # Add logic to handle the selected customer data

def main():
    app = QApplication(sys.argv)
    window = SelectCustomerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
