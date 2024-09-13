import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView

from src.components import DB

class SelectLoanWindow(QDialog):
    loan_selected = pyqtSignal(dict)  # Signal to emit selected loan data

    def __init__(self):
        super(SelectLoanWindow, self).__init__()

        # Set window properties
        self.setWindowTitle("Select Loan")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search by loan number")
        self.layout.addWidget(self.searchBox)

        # Table view for displaying loans
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)  # Allow only single selection
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
        loans_ref = DB.collection(u'Loan')
        docs = loans_ref.stream()

        data = []
        for doc in docs:
            loan_data = doc.to_dict()

            # Skip loans where the loan status is 'Overdue'
            if loan_data.get('loan_status') == 'Overdue':
                continue  # Skip this loan

            loan_data['loan_id'] = doc.id  # Store the document ID
            customer_data = self.get_customer_data(loan_data.get('uid'))  # Fetch customer details
            loan_data.update(customer_data)  # Add customer data to loan_data
            data.append(loan_data)

        self.df = pd.DataFrame(data)

        # Select display columns: Loan Number, Loan Type, Contract Date, Customer Name, and NRC No.
        self.display_df = self.df[['loan_number', 'loan_type', 'contract_date', 'customer_name', 'nrc_no']]

        # Rename the columns to match the required capitalization
        self.display_df.columns = ['Loan Number', 'Loan Type', 'Contract Date', 'Customer Name', 'NRC No.']

        # Copy the display dataframe for filtering purposes
        self.filtered_df = self.display_df.copy()
        self.model = self.create_model(self.filtered_df)
        self.tableView.setModel(self.model)

    def get_customer_data(self, customer_uid):
        try:
            customer_doc = DB.collection('Customer').document(customer_uid).get()
            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                return {
                    'customer_name': customer_data.get('name', 'Unknown'),
                    'nrc_no': customer_data.get('nrc_no', 'Unknown')
                }
            else:
                return {'customer_name': 'Unknown', 'nrc_no': 'Unknown'}
        except Exception as e:
            print(f"Error loading customer data: {e}")
            return {'customer_name': 'Error', 'nrc_no': 'Error'}

    def filter_data(self):
        search_text = self.searchBox.text().lower()
        self.filtered_df = self.display_df[self.display_df['Loan Number'].str.lower().str.contains(search_text)]
        self.model = self.create_model(self.filtered_df)
        self.tableView.setModel(self.model)

    def create_model(self, df):
        model = QStandardItemModel(df.shape[0], df.shape[1])
        
        # Set the correct headers explicitly with capitalization
        model.setHorizontalHeaderLabels(['Loan Number', 'Loan Type', 'Contract Date', 'Customer Name', 'NRC No.'])

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(str(df.iat[row, col]))
                item.setEditable(False)  # Set to read-only
                model.setItem(row, col, item)

        return model

    def handle_select_button(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        if selected_indexes:
            # Get the first selected row (since only one can be selected)
            index = selected_indexes[0]
            row = index.row()
            selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()

            # Create a dict with loan_id and customer_name for returning
            return_data = {
                'loan_id': selected_data['loan_id'],  # Return loan_id
                'customer_name': selected_data['customer_name']  # Return customer name
            }

            self.loan_selected.emit(return_data)  # Emit the selected loan and customer name
            self.accept()

def main():
    app = QApplication(sys.argv)
    window = SelectLoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()