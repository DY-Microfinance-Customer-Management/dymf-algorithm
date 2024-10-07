import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from src.components import DB
from google.cloud.firestore_v1.base_query import FieldFilter


class SelectCustomerWindow(QDialog):
    customer_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(SelectCustomerWindow, self).__init__(parent)

        # Set window properties
        self.setWindowTitle("Select Customer")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Enter customer name")
        self.layout.addWidget(self.searchBox)

        # Search button
        self.searchButton = QPushButton("Search", self)
        self.searchButton.clicked.connect(self.search_customer_data)
        self.layout.addWidget(self.searchButton)

        # Table view for displaying customers
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
        self.model = QStandardItemModel(0, 4)
        self.model.setHorizontalHeaderLabels(['Name', 'NRC No.', 'Date of Birth', 'Phone No.'])
        self.tableView.setModel(self.model)

        # Customer Data for Selection
        self.customer_data = None

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

    def search_customer_data(self):
        try:
            customer_name = self.searchBox.text().strip()

            lower_keyword = customer_name.lower()
            upper_keyword = customer_name.title()

            if customer_name:
                filtered_customers = []

                # Fetch customer data using the given condition
                lower_keyword_customers = DB.collection('Customer').where(
                    filter=FieldFilter('name', '>=', lower_keyword)
                ).where(
                    filter=FieldFilter('name', '<=', lower_keyword + '\uf8ff')
                ).stream()
                
                upper_keyword_customers = DB.collection('Customer').where(
                    filter=FieldFilter('name', '>=', upper_keyword)
                ).where(
                    filter=FieldFilter('name', '<=', upper_keyword + '\uf8ff')
                ).stream()

                for lower_doc in lower_keyword_customers:
                    customer_dict = lower_doc.to_dict()
                    customer_dict['uid'] = lower_doc.id
                    filtered_customers.append(customer_dict)

                for upper_doc in upper_keyword_customers:
                    customer_dict = upper_doc.to_dict()
                    customer_dict['uid'] = upper_doc.id
                    filtered_customers.append(customer_dict)

                if not filtered_customers:
                    QMessageBox.warning(self, "No Data", "No customer found with the entered name.")
                    return

                # Save the complete customer data for later selection
                self.customer_data = pd.DataFrame(filtered_customers)

                # Combine phone number fields into a single string
                self.customer_data['Phone No.'] = self.customer_data[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(
                    lambda x: '-'.join(filter(None, x)), axis=1
                )

                # Select display columns for the table view
                self.display_df = self.customer_data[['name', 'nrc_no', 'date_of_birth', 'Phone No.']]
                self.model = self.create_model(self.display_df)
                self.tableView.setModel(self.model)

            else:
                QMessageBox.warning(self, "Input Error", "Please enter the customer's name.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while searching for customer data: {e}")

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

            # Get the original data for the selected customer using the filtered row index
            selected_data = self.customer_data.iloc[self.display_df.index[row]].to_dict()

            # Emit the selected customer data without explicitly listing fields
            self.customer_selected.emit(selected_data)
            self.accept()

def main():
    app = QApplication(sys.argv)
    window = SelectCustomerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
