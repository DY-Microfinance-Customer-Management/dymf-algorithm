from PyQt5.QtWidgets import QVBoxLayout, QDialog, QPushButton, QListWidget
from src.components import DB

class SelectLoanOfficerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Loan Officer")
        self.setGeometry(300, 300, 300, 400)

        self.layout = QVBoxLayout(self)

        self.listWidget = QListWidget(self)
        self.layout.addWidget(self.listWidget)

        self.selectButton = QPushButton("Select", self)
        self.selectButton.clicked.connect(self.accept)
        self.layout.addWidget(self.selectButton)

        self.officer_data = self.load_officer_data()

        for officer in self.officer_data:
            self.listWidget.addItem(f"{officer['name']} - {officer['service_area']}")

    def load_officer_data(self):
        officers_ref = DB.collection('Officer')
        docs = officers_ref.stream()
        return [doc.to_dict() for doc in docs]

    def get_selected_officer(self):
        selected_row = self.listWidget.currentRow()
        if selected_row != -1:
            return self.officer_data[selected_row]
        return None
