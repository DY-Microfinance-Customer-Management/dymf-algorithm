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
        self.layout.addWidget(self.searchBox)

        # Table view for displaying staff
        self.tableView = QTableView(self)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.layout.addWidget(self.tableView)

        # Select button
        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.handle_select_button)
        self.selectButton.setFocusPolicy(Qt.StrongFocus)
        self.selectButton.setDefault(True)
        self.layout.addWidget(self.selectButton)

        # Signal for search
        self.searchBox.textChanged.connect(self.filter_data)

        # Apply styles
        self.apply_stylesheet()

        # Initialize empty DataFrame for displaying search results
        self.display_df = pd.DataFrame(columns=['name', 'nrc_no', 'date_of_birth', 'Phone No.'])
        self.model = self.create_model(self.display_df)
        self.tableView.setModel(self.model)

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
        search_text = self.searchBox.text().strip().lower()

        if search_text:
            # Load data from Firestore with search text filtering
            try:
                staff_ref = DB.collection('Staff').where('name_lower', '>=', search_text).where('name_lower', '<=', search_text + '\uf8ff')
                docs = staff_ref.stream()

                data = []
                for doc in docs:
                    staff_data = doc.to_dict()
                    staff_data['uid'] = doc.id
                    data.append(staff_data)

                # Create DataFrame from the retrieved data
                if data:
                    df = pd.DataFrame(data)
                    df['Phone No.'] = df[['tel1ByOne', 'tel1ByTwo', 'tel1ByThree']].apply(lambda x: '-'.join(filter(None, x)), axis=1)
                    self.display_df = df[['name', 'nrc_no', 'date_of_birth', 'Phone No.']]
                else:
                    self.display_df = pd.DataFrame(columns=['name', 'nrc_no', 'date_of_birth', 'Phone No.'])

                # Update the table view with the new filtered data
                self.model = self.create_model(self.display_df)
                self.tableView.setModel(self.model)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while searching for staff: {e}")

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
            selected_data = self.display_df.iloc[row].to_dict()
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
