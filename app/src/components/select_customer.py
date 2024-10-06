import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from src.components import DB

class SelectCustomerWindow(QDialog):
    customer_selected = pyqtSignal(dict)

    def __init__(self, customer_data, parent=None):
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

        # Apply styles
        self.apply_stylesheet()

        # Load data
        self.df = customer_data

        # Combine phone number fields into a single string
        self.df['Phone No.'] = self.df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)

        # Select display columns
        self.display_df = self.df[['name', 'nrc_no', 'date_of_birth', 'Phone No.']]

        # Copy the display dataframe for filtering purposes
        self.filtered_df = self.display_df.copy()
        self.model = self.create_model(self.filtered_df)
        self.tableView.setModel(self.model)

        # Set focus to Select button when window is shown
        self.selectButton.setFocus()

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

def load_customer_data():
    """ 고객 데이터를 불러오는 함수. 창을 띄우기 전에 데이터를 확인 """
    customers_ref = DB.collection(u'Customer')
    docs = customers_ref.stream()

    data = []
    for doc in docs:
        customer_data = doc.to_dict()
        customer_data['uid'] = doc.id
        data.append(customer_data)

    if not data:
        # 데이터가 없으면 None을 반환하여 창을 띄우지 않음
        return None

    return pd.DataFrame(data)


def main():
    app = QApplication(sys.argv)

    # 고객 데이터를 먼저 로드
    customer_data = load_customer_data()

    # 데이터가 있으면 창을 띄움
    if customer_data is not None:
        window = SelectCustomerWindow(customer_data)
        window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
