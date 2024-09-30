from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QTableView, QAbstractItemView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from src.components import DB
import pandas as pd

class SelectLoanOfficerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Loan Officer")
        self.setGeometry(300, 300, 400, 300)

        self.layout = QVBoxLayout(self)

        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.layout.addWidget(self.tableView)

        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.accept)
        self.layout.addWidget(self.selectButton)

        # Apply styles
        self.apply_stylesheet()

        # Load the data and populate the table
        self.officer_data = self.load_officer_data()
        self.populate_table()

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

    def load_officer_data(self):
        officers_ref = DB.collection('Officer')
        docs = officers_ref.stream()
        officer_list = [doc.to_dict() for doc in docs]

        # Convert data to a pandas DataFrame for better management
        return pd.DataFrame(officer_list)

    def populate_table(self):
        model = QStandardItemModel(self.officer_data.shape[0], self.officer_data.shape[1])
        model.setHorizontalHeaderLabels(self.officer_data.columns)

        # Fill in the table with data
        for row in range(self.officer_data.shape[0]):
            for col in range(self.officer_data.shape[1]):
                item = QStandardItem(str(self.officer_data.iloc[row, col]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                model.setItem(row, col, item)

        self.tableView.setModel(model)

        # Hide the "oid" column if it exists
        if 'oid' in self.officer_data.columns:
            oid_col_index = self.officer_data.columns.get_loc('oid')
            self.tableView.hideColumn(oid_col_index)

    def get_selected_officer(self):
        selected_row = self.tableView.currentIndex().row()
        if selected_row != -1:
            # Return the name of the selected officer
            data = self.officer_data.iloc[selected_row].to_dict()
            print(data)
            return data
        return None
