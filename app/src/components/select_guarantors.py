import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from src.components import DB

class SelectGuarantorWindow(QDialog):
    guarantors_selected = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Select Guarantors")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search by guarantor name")
        self.layout.addWidget(self.searchBox)

        # Table view for displaying guarantors
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.MultiSelection)
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
        guarantors_ref = DB.collection(u'Guarantor')
        docs = guarantors_ref.stream()

        data = []
        for doc in docs:
            guarantor_data = doc.to_dict()
            guarantor_data['uid'] = doc.id
            data.append(guarantor_data)

        self.df = pd.DataFrame(data)

        # Combine phone number fields into a single string
        self.df['Phone No.'] = self.df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)

        # Select display columns, excluding address
        self.display_df = self.df[['name', 'nrc_no', 'Phone No.']]

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
        model.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(str(df.iat[row, col]))
                item.setEditable(False)  # read-only 설정
                model.setItem(row, col, item)

        return model

    def handle_select_button(self):
        selected_indexes = self.tableView.selectionModel().selectedRows()
        selected_guarantors = []
        if selected_indexes:
            for index in selected_indexes:
                row = index.row()
                selected_data = self.df.iloc[self.filtered_df.index[row]].to_dict()
                selected_guarantors.append(selected_data['uid'])

            self.guarantors_selected.emit(selected_guarantors)
            self.accept()


def main():
    app = QApplication(sys.argv)
    window = SelectGuarantorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()