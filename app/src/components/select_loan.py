import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from google.cloud.firestore_v1.base_query import FieldFilter

from src.components import DB

class SelectLoanWindow(QDialog):
    loan_selected = pyqtSignal(dict)  # Signal to emit selected loan data

    def __init__(self, collection_type='Loan'):
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
        self.searchBox.setPlaceholderText("Enter loan number or customer name")
        self.layout.addWidget(self.searchBox)

        # Search button
        self.searchButton = QPushButton("Search", self)
        self.searchButton.clicked.connect(self.search_loan_data)
        self.layout.addWidget(self.searchButton)

        # Table view for displaying loans
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.layout.addWidget(self.tableView)

        # Select button
        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.handle_select_button)
        self.selectButton.setFocusPolicy(Qt.StrongFocus)
        self.selectButton.setDefault(True)
        self.layout.addWidget(self.selectButton)

        # Apply styles
        self.apply_stylesheet()

        # Set up an empty model for the table view initially
        self.model = QStandardItemModel(0, 5)
        self.model.setHorizontalHeaderLabels(['Loan Number', 'Loan Type', 'Contract Date', 'Customer Name', 'NRC No.'])
        self.tableView.setModel(self.model)

        # Store collection type
        self.collection_type = collection_type

    def apply_stylesheet(self):
        stylesheet = """
        QWidget {
            background-color: #fbfbfb;
        }

        QTableView {
            background-color: #f1f1f1;
            border: 1px solid transparent;
            border-radius: 10px;
        }

        QPushButton {
            background-color: #0077c2;
            color: white;
            border: 1px solid transparent;
            border-radius: 10px;
            padding: 5px 10px;
        }

        QPushButton:hover {
            border: 1px solid white;
        }

        QPushButton:pressed {
            background-color: #005f9e;
            padding-top: 6px;
            padding-bottom: 4px;
        }

        QPushButton:disabled {
            background-color: lightgray;
            color: gray;
            border: 1px solid gray;
        }

        QLineEdit {
            border: none;
            border-bottom: 1px solid black;
            background-color: transparent;
            color: black;
        }

        QLineEdit:disabled {
            border: none;
            border-bottom: 1px solid lightgray;
            background-color: lightgray;
            color: lightgray;
        }
        """
        self.setStyleSheet(stylesheet)

    def search_loan_data(self):
        try:
            search_text = self.searchBox.text().strip()

            lower_keyword = search_text.lower()
            upper_keyword = search_text.title()

            if search_text:
                filtered_loans = []

                # Fetch loan data using the given condition
                lower_keyword_loans = DB.collection(self.collection_type).where(
                    filter=FieldFilter('loan_number', '>=', lower_keyword)
                ).where(
                    filter=FieldFilter('loan_number', '<=', lower_keyword + '\uf8ff')
                ).stream()

                upper_keyword_loans = DB.collection(self.collection_type).where(
                    filter=FieldFilter('loan_number', '>=', upper_keyword)
                ).where(
                    filter=FieldFilter('loan_number', '<=', upper_keyword + '\uf8ff')
                ).stream()

                for lower_doc in lower_keyword_loans:
                    filtered_loans.append(lower_doc.to_dict())

                for upper_doc in upper_keyword_loans:
                    filtered_loans.append(upper_doc.to_dict())

                if not filtered_loans:
                    QMessageBox.warning(self, "No Data", "No loan found with the entered information.")
                    return

                # Prepare the data for displaying in the table
                loan_data = pd.DataFrame(filtered_loans)

                # Add customer information
                loan_data['customer_name'], loan_data['nrc_no'] = zip(
                    *loan_data['uid'].apply(self.get_customer_data)
                )

                # Select display columns
                self.display_df = loan_data[['loan_number', 'loan_type', 'contract_date', 'customer_name', 'nrc_no']]
                self.model = self.create_model(self.display_df)
                self.tableView.setModel(self.model)

            else:
                QMessageBox.warning(self, "Input Error", "Please enter the loan number or customer name.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while searching for loan data: {e}")

    def get_customer_data(self, customer_uid):
        try:
            customer_doc = DB.collection('Customer').document(customer_uid).get()
            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                return customer_data.get('name', 'Unknown'), customer_data.get('nrc_no', 'Unknown')
            else:
                return 'Unknown', 'Unknown'
        except Exception as e:
            print(f"Error loading customer data: {e}")
            return 'Error', 'Error'

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
            # Get the first selected row
            index = selected_indexes[0]
            row = index.row()

            # Get the original data for the selected loan using the filtered row index
            selected_data = self.display_df.iloc[row].to_dict()

            # Emit the selected loan data, including the original document ID
            self.loan_selected.emit(selected_data)
            self.accept()

def main():
    app = QApplication(sys.argv)
    window = SelectLoanWindow(collection_type='Loan')  # Specify 'Loan' or 'Overdue'
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
