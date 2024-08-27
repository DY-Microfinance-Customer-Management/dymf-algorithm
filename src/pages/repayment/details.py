import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableView, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class RepaymentDetailsWindow(QMainWindow):
    def __init__(self, loan_data):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "details.ui")
        uic.loadUi(ui_path, self)

        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.toExcelButton.setEnabled(False)

        self.guarantorSaveButton.setEnabled(False)
        self.guarantorEditButton.setEnabled(False)
        self.guarantorDeleteButton.setEnabled(False)
        self.guarantorType.setEnabled(False)
        self.guarantorSearchButton.setEnabled(False)
        self.guarantorRelation.setEnabled(False)

        self.collateralSaveButton.setEnabled(False)
        self.collateralEditButton.setEnabled(False)
        self.collateralDeleteButton.setEnabled(False)
        self.collateralType.setEnabled(False)
        self.collateralName.setEnabled(False)
        self.collateralDetails.setEnabled(False)

        self.counselingSaveButton.setEnabled(False)
        self.counselingEditButton.setEnabled(False)
        self.counselingDeleteButton.setEnabled(False)
        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)
        
        self.init_loan_data(loan_data)
        self.show()

    def init_loan_data(self, loan_data):
        self.load_guarantor_data(loan_data)
        self.load_collateral_data(loan_data)
        self.load_counseling_data(loan_data)
        self.load_loan_schedule(loan_data)

    def load_guarantor_data(self, loan_data):
        self.guarantorLoanNumber.setText(str(loan_data.get('loanNumber', '')))
        self.guarantorLoanStatus.setText(str(loan_data.get('loanStatus', '')))
        self.guarantorLoanOfficer.setText(loan_data.get('loanOfficer', ''))
        self.guarantorContractDate.setText(loan_data.get('contractDate', ''))
        self.guarantorLoanType.setText(loan_data.get('loanType', ''))
        self.guarantorLoanAmount.setText(str(loan_data.get('loanAmount', '')))
        self.guarantorInterestRate.setText(str(loan_data.get('interestRate', '')))
        self.guarantorExpiry.setText(loan_data.get('expiry', ''))
        self.guarantorRepaymentCycle.setText(loan_data.get('loanRepaymentCycle', ''))

        if 'guarantors' in loan_data:
            guarantor_data = loan_data['guarantors']
            columns = ["Name", "Type", "Relation"]
            self.load_guarantor_table(guarantor_data, columns)

    def load_guarantor_table(self, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, guarantor in enumerate(data):
            model.setItem(row_idx, 0, self.create_read_only_item(guarantor.get("name", "")))
            model.setItem(row_idx, 1, self.create_read_only_item(guarantor.get("type", "")))
            model.setItem(row_idx, 2, self.create_read_only_item(guarantor.get("relation", "")))

        self.guarantorTable.setModel(model)
        self.guarantorTable.resizeColumnsToContents()

    def load_collateral_data(self, loan_data):
        self.collateralLoanNumber.setText(str(loan_data.get('loanNumber', '')))
        self.collateralLoanStatus.setText(str(loan_data.get('loanStatus', '')))
        self.collateralLoanOfficer.setText(loan_data.get('loanOfficer', ''))
        self.collateralContractDate.setText(loan_data.get('contractDate', ''))
        self.collateralLoanType.setText(loan_data.get('loanType', ''))
        self.collateralLoanAmount.setText(str(loan_data.get('loanAmount', '')))
        self.collateralInterestRate.setText(str(loan_data.get('interestRate', '')))
        self.collateralExpiry.setText(loan_data.get('expiry', ''))
        self.collateralRepaymentCycle.setText(loan_data.get('loanRepaymentCycle', ''))

        if 'collaterals' in loan_data:
            collateral_data = loan_data['collaterals']
            columns = ["Type", "Name", "Details"]
            self.load_collateral_table(collateral_data, columns)

    def load_collateral_table(self, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, collateral in enumerate(data):
            model.setItem(row_idx, 0, self.create_read_only_item(collateral.get("type", "")))
            model.setItem(row_idx, 1, self.create_read_only_item(collateral.get("name", "")))
            model.setItem(row_idx, 2, self.create_read_only_item(collateral.get("details", "")))

        self.collateralTable.setModel(model)
        self.collateralTable.resizeColumnsToContents()

    def load_counseling_data(self, loan_data):
        self.counselingLoanNumber.setText(str(loan_data.get('loanNumber', '')))
        self.counselingLoanStatus.setText(str(loan_data.get('loanStatus', '')))
        self.counselingLoanOfficer.setText(loan_data.get('loanOfficer', ''))
        self.counselingContractDate.setText(loan_data.get('contractDate', ''))
        self.counselingLoanType.setText(loan_data.get('loanType', ''))
        self.counselingLoanAmount.setText(str(loan_data.get('loanAmount', '')))
        self.counselingInterestRate.setText(str(loan_data.get('interestRate', '')))
        self.counselingExpiry.setText(loan_data.get('expiry', ''))
        self.counselingRepaymentCycle.setText(loan_data.get('loanRepaymentCycle', ''))

        if 'counselings' in loan_data:
            counseling_data = loan_data['counselings']
            columns = ["Date", "Subject", "Details", "Corrective Measure"]
            self.load_counseling_table(counseling_data, columns)

    def load_counseling_table(self, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, counseling in enumerate(data):
            model.setItem(row_idx, 0, self.create_read_only_item(counseling.get("date", "")))
            model.setItem(row_idx, 1, self.create_read_only_item(counseling.get("subject", "")))
            model.setItem(row_idx, 2, self.create_read_only_item(counseling.get("details", "")))
            model.setItem(row_idx, 3, self.create_read_only_item(counseling.get("corrective_measure", "")))

        self.counselingTable.setModel(model)
        self.counselingTable.resizeColumnsToContents()

    def load_loan_schedule(self, loan_data):
        if 'loanSchedule' in loan_data:
            schedule_data = loan_data['loanSchedule']
            columns = ["Payment Date", "Period", "Principal", "Interest", "Total"]

            repayment_data = [item for item in schedule_data if item.get('status') == 0]
            received_data = [item for item in schedule_data if item.get('status') in [1, 2]]
 
            self.load_table(self.repaymentScheduleTable, repayment_data, columns)
            self.load_table(self.receivedTable, received_data, columns)

    def load_table(self, table_view, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, item in enumerate(data):
            model.setItem(row_idx, 0, self.create_read_only_item(item.get("Payment Date", "")))
            model.setItem(row_idx, 1, self.create_read_only_item(item.get("Period", "")))
            model.setItem(row_idx, 2, self.create_read_only_item(item.get("Principal", "")))
            model.setItem(row_idx, 3, self.create_read_only_item(item.get("Interest", "")))
            model.setItem(row_idx, 4, self.create_read_only_item(item.get("Total", "")))

        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def create_read_only_item(self, text):
        item = QStandardItem(text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
