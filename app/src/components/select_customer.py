import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableView, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QAbstractTableModel, pyqtSignal
from PyQt5.QtGui import QIcon

from src.components import DB

class SelectCustomerWindow(QMainWindow):
    customer_selected = pyqtSignal(dict)

    def __init__(self):
        super(SelectCustomerWindow, self).__init__()

        # Set window properties
        self.setWindowTitle("Select Customer")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search by customer name")
        self.layout.addWidget(self.searchBox)

        # Table view for displaying customers
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.layout.addWidget(self.tableView)

        # Select button
        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.handle_select_button)
        self.layout.addWidget(self.selectButton)

        # Signal for search
        self.searchBox.textChanged.connect(self.filter_data)
        
        # Load data
        self.load_data()

    def load_data(self):
        customers_ref = DB.collection(u'Customer')
        docs = customers_ref.stream()

        data = []
        for doc in docs:
            customer_data = doc.to_dict()
            customer_data['uid'] = doc.id
            data.append(customer_data)
            print(data)

        self.df = pd.DataFrame(data)

        # Combine phone number fields into a single string
        self.df['Phone No.'] = self.df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)

        # Select display columns
        self.display_df = self.df[['name', 'date_of_birth', 'Phone No.', 'loan_officer']]

        # Copy the display dataframe for filtering purposes
        self.filtered_df = self.display_df.copy()
        self.model = PandasModel(self.filtered_df)
        self.tableView.setModel(self.model)

    def filter_data(self):
        search_text = self.searchBox.text().lower()
        self.filtered_df = self.display_df[self.display_df['name'].str.lower().str.contains(search_text)]
        self.model._df = self.filtered_df
        self.model.layoutChanged.emit()

    def handle_select_button(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            # Get the first selected row
            index = selected_indexes[0]
            row = index.row()
            selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()
            self.customer_selected.emit(selected_data)  # Emit the selected customer data
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