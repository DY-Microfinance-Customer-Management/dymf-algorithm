import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QDialog, QTableView, QLineEdit, QPushButton, QVBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem

from src.components import DB

class SelectStaffWindow(QDialog):
    staff_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super(SelectStaffWindow, self).__init__(parent)

        # Set window properties
        self.setWindowTitle("Select Staff")
        self.setGeometry(300, 300, 600, 700)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Search box
        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText("Search by staff name")
        self.searchBox.textChanged.connect(self.filter_data)  # Connect to filter function for real-time search
        self.layout.addWidget(self.searchBox)

        # Table view for displaying staff
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.layout.addWidget(self.tableView)

        # Select button
        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.handle_select_button)
        self.selectButton.setFocusPolicy(Qt.StrongFocus)  # Ensure button can take focus
        self.selectButton.setDefault(True)  # Set as default button
        self.layout.addWidget(self.selectButton)

        # Apply styles
        self.apply_stylesheet()

        # Load all data initially
        self.load_all_staff()

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

    def load_all_staff(self):
        # Load all staff data from Firestore
        try:
            staff_ref = DB.collection('Staff')
            docs = staff_ref.stream()

            data = []
            for doc in docs:
                staff_data = doc.to_dict()
                staff_data['uid'] = doc.id
                data.append(staff_data)

            # Create DataFrame from the retrieved data
            if data:
                self.df = pd.DataFrame(data)
                self.df['Phone No.'] = self.df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)
                self.display_df = self.df[['name', 'nrc_no', 'date_of_birth', 'Phone No.', 'uid']]
            else:
                self.display_df = pd.DataFrame(columns=['name', 'nrc_no', 'date_of_birth', 'Phone No.', 'uid'])

            # Initially, filtered_df should be equal to display_df
            self.filtered_df = self.display_df.copy()

            # Update the table view with all data
            self.update_table_view(self.filtered_df)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading staff data: {e}")

    def filter_data(self):
        search_text = self.searchBox.text().strip().lower()

        if search_text:
            # Filter the DataFrame based on the search text
            self.filtered_df = self.display_df[self.display_df['name'].str.lower().str.contains(search_text)]
        else:
            # If no search text is provided, show all data
            self.filtered_df = self.display_df.copy()

        # Update the table view with the filtered data
        self.update_table_view(self.filtered_df)

    def update_table_view(self, df):
        self.model = self.create_model(df)
        self.tableView.setModel(self.model)
        # Hide the 'uid' column
        self.tableView.setColumnHidden(df.columns.get_loc('uid'), True)

    def create_model(self, df):
        model = QStandardItemModel(df.shape[0], df.shape[1])

        # Set the correct headers explicitly with capitalization
        model.setHorizontalHeaderLabels(['Name', 'NRC No.', 'Date of Birth', 'Phone No.', 'UID'])

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
            selected_data = self.filtered_df.iloc[row].to_dict()
            self.staff_selected.emit(selected_data)  # Emit the selected staff data
            self.accept()

def main():
    app = QApplication(sys.argv)

    # Create and show the selection window
    window = SelectStaffWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
