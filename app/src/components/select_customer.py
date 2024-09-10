import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from src.components import DB

class SelectCustomerWindow(QDialog):
    customer_selected = pyqtSignal(dict)

    def __init__(self):
        super(SelectCustomerWindow, self).__init__()

        # Set window properties
        self.setWindowTitle("Select Customer")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.layout = QVBoxLayout(self)

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
        self.selectButton.setFocusPolicy(Qt.StrongFocus)  # Ensure button can take focus
        self.selectButton.setDefault(True)  # Set as default button
        self.layout.addWidget(self.selectButton)

        # Signal for search
        self.searchBox.textChanged.connect(self.filter_data)

        # Load data
        self.load_data()

        # Set focus to Select button when window is shown
        self.selectButton.setFocus()

    def load_data(self):
        customers_ref = DB.collection(u'Customer')
        docs = customers_ref.stream()

        data = []
        for doc in docs:
            customer_data = doc.to_dict()
            customer_data['uid'] = doc.id
            data.append(customer_data)

        self.df = pd.DataFrame(data)

        # Combine phone number fields into a single string
        self.df['Phone No.'] = self.df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)

        # Select display columns
        # Replace 'loan_officer' with 'nrc_no' and set the correct order and capitalization
        self.display_df = self.df[['name', 'nrc_no', 'date_of_birth', 'Phone No.']]

        # Rename the columns to match the required capitalization
        self.display_df.columns = ['Name', 'NRC No.', 'Date of Birth', 'Phone No.']

        # Copy the display dataframe for filtering purposes
        self.filtered_df = self.display_df.copy()
        self.model = self.create_model(self.filtered_df)
        self.tableView.setModel(self.model)

    def filter_data(self):
        search_text = self.searchBox.text().lower()
        self.filtered_df = self.display_df[self.display_df['name'].str.lower().str.contains(search_text)]
        self.model = self.create_model(self.filtered_df)
        self.tableView.setModel(self.model)

    def create_model(self, df):
        model = QStandardItemModel(df.shape[0], df.shape[1])
        
        # Set the correct headers explicitly with capitalization
        model.setHorizontalHeaderLabels(['Name', 'NRC No.', 'Date of Birth', 'Phone No.'])

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(str(df.iat[row, col]))
                item.setEditable(False)  # Set to read-only
                model.setItem(row, col, item)

        return model

    def handle_select_button(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            # Get the first selected row
            index = selected_indexes[0]
            row = index.row()
            selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()
            self.customer_selected.emit(selected_data)  # Emit the selected customer data
            self.accept()


def main():
    app = QApplication(sys.argv)
    window = SelectCustomerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()