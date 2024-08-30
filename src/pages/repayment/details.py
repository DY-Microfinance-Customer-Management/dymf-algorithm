import os, sys
import uuid
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableView, QAbstractItemView
from PyQt5.QtCore import Qt, QDate, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from firebase_admin import firestore

from src.components import DB
from src.pages.loan.select_customer import SelectCustomerWindow

class RepaymentDetailsWindow(QMainWindow):
    def __init__(self, loan_data):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "details.ui")
        uic.loadUi(ui_path, self)

        self.loan_data = loan_data
        self.is_guarantor_edit_mode = False
        self.is_collateral_edit_mode = False
        self.is_counseling_edit_mode = False

        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        self.guarantorSaveButton.setEnabled(False)
        self.guarantorEditButton.setEnabled(False)
        self.guarantorDeleteButton.setEnabled(False)
        self.guarantorSearchButton.setEnabled(False)
        self.guarantorType.setEnabled(False)
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
        self.setup_table_selection()
        self.setup_connections()
        self.show()

    def init_loan_data(self, loan_data):
        self.load_loan_schedule(loan_data)
        self.load_guarantor_data(loan_data)
        self.load_collateral_data(loan_data)
        self.load_counseling_data(loan_data)

    def setup_connections(self):
        self.paidButton.clicked.connect(self.on_paid_button_clicked)
        self.deleteButton.clicked.connect(self.on_delete_button_clicked)
        
        self.guarantorNewButton.clicked.connect(self.on_guarantor_new_clicked)
        self.guarantorEditButton.clicked.connect(self.on_guarantor_edit_clicked)
        self.guarantorSaveButton.clicked.connect(self.on_guarantor_save_clicked)
        self.guarantorDeleteButton.clicked.connect(self.on_guarantor_delete_clicked)
        self.guarantorSearchButton.clicked.connect(self.open_select_guarantor_window)

        self.collateralNewButton.clicked.connect(self.on_collateral_new_clicked)
        self.collateralEditButton.clicked.connect(self.on_collateral_edit_clicked)
        self.collateralSaveButton.clicked.connect(self.on_collateral_save_clicked)
        self.collateralDeleteButton.clicked.connect(self.on_collateral_delete_clicked)

        self.counselingNewButton.clicked.connect(self.on_counseling_new_clicked)
        self.counselingEditButton.clicked.connect(self.on_counseling_edit_clicked)
        self.counselingSaveButton.clicked.connect(self.on_counseling_save_clicked)
        self.counselingDeleteButton.clicked.connect(self.on_counseling_delete_clicked)

    def setup_table_selection(self):
        self.repaymentScheduleTable.setSelectionBehavior(QTableView.SelectRows)
        self.repaymentScheduleTable.setSelectionMode(QTableView.SingleSelection)
        self.repaymentScheduleTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.receivedTable.setSelectionBehavior(QTableView.SelectRows)
        self.receivedTable.setSelectionMode(QTableView.SingleSelection)
        self.receivedTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.guarantorTable.setSelectionBehavior(QTableView.SelectRows)
        self.guarantorTable.setSelectionMode(QTableView.SingleSelection)
        self.guarantorTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.collateralTable.setSelectionBehavior(QTableView.SelectRows)
        self.collateralTable.setSelectionMode(QTableView.SingleSelection)
        self.collateralTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.counselingTable.setSelectionBehavior(QTableView.SelectRows)
        self.counselingTable.setSelectionMode(QTableView.SingleSelection)
        self.counselingTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 테이블 클릭 이벤트 연결
        self.repaymentScheduleTable.clicked.connect(self.handle_repayment_schedule_table_click)
        self.receivedTable.clicked.connect(self.handle_received_table_click)
        self.guarantorTable.clicked.connect(self.handle_guarantor_table_click)
        self.collateralTable.clicked.connect(self.handle_collateral_table_click)
        self.counselingTable.clicked.connect(self.handle_counseling_table_click)

    def handle_repayment_schedule_table_click(self, index):
        self.receivedTable.clearSelection()
        model = self.repaymentScheduleTable.model()
        selected_row = index.row()

        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        self.paidButton.setEnabled(self.selected_schedule_data["Status"] == "Scheduled")

    def handle_received_table_click(self, index):
        self.repaymentScheduleTable.clearSelection()
        model = self.receivedTable.model()
        selected_row = index.row()

        self.selected_schedule_data = {
            "Payment Date": model.item(selected_row, 0).text(),
            "Principal": model.item(selected_row, 1).text(),
            "Interest": model.item(selected_row, 2).text(),
            "Total": model.item(selected_row, 3).text(),
            "Status": model.item(selected_row, 4).text(),
        }

        self.deleteButton.setEnabled(self.selected_schedule_data["Status"] == "Paid")

    def handle_guarantor_table_click(self, index):
        self.selected_guarantor_row = index.row()
        model = self.guarantorTable.model()

        # 선택된 데이터를 입력란에 표시
        self.guarantorName.setText(model.item(self.selected_guarantor_row, 0).text())
        self.guarantorType.setCurrentText(model.item(self.selected_guarantor_row, 1).text())
        self.guarantorRelation.setCurrentText(model.item(self.selected_guarantor_row, 2).text())

        self.guarantorName.setEnabled(False)
        self.guarantorType.setEnabled(False)
        self.guarantorRelation.setEnabled(False)

        self.guarantorEditButton.setEnabled(True)
        self.guarantorDeleteButton.setEnabled(True)

    def handle_collateral_table_click(self, index):
        self.selected_collateral_row = index.row()
        model = self.collateralTable.model()

        # 선택된 데이터를 입력란에 표시
        self.collateralType.setCurrentText(model.item(self.selected_collateral_row, 0).text())
        self.collateralName.setText(model.item(self.selected_collateral_row, 1).text())
        self.collateralDetails.setText(model.item(self.selected_collateral_row, 2).text())

        self.collateralType.setEnabled(False)
        self.collateralName.setEnabled(False)
        self.collateralDetails.setEnabled(False)

        self.collateralEditButton.setEnabled(True)
        self.collateralDeleteButton.setEnabled(True)

    def handle_counseling_table_click(self, index):
        self.selected_counseling_row = index.row()
        model = self.counselingTable.model()

        # 선택된 데이터를 입력란에 표시
        date_str = model.item(self.selected_counseling_row, 0).text()
        counseling_date = QDate.fromString(date_str, "yyyy-MM-dd")
        self.counselingDate.setDate(counseling_date)
        self.counselingSubject.setText(model.item(self.selected_counseling_row, 1).text())
        self.counselingDetails.setText(model.item(self.selected_counseling_row, 2).text())
        self.counselingCorrectiveMeasure.setText(model.item(self.selected_counseling_row, 3).text())

        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)

        self.counselingEditButton.setEnabled(True)
        self.counselingDeleteButton.setEnabled(True)

    def on_paid_button_clicked(self):
        selected_schedule = self.selected_schedule_data
        if not selected_schedule:
            QMessageBox.warning(self, "Error", "No repayment schedule selected.")
            return

        payment_date = selected_schedule.get("Payment Date")

        try:
            loan_schedule = self.loan_data.get("loanSchedule", [])
            for schedule in loan_schedule:
                if schedule.get("Payment Date") == payment_date:
                    schedule["status"] = 1

            loan_id = self.loan_data.get("loan_id")
            DB.collection("Loan").document(loan_id).update({"loanSchedule": loan_schedule})

            QMessageBox.information(self, "Success", f"Payment for {payment_date} marked as paid.")
            self.load_loan_schedule(self.loan_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def on_delete_button_clicked(self):
        if not self.selected_schedule_data:
            QMessageBox.warning(self, "No Selection", "Please select a repayment record.")
            return

        payment_date = self.selected_schedule_data["Payment Date"]

        try:
            loan_schedule = self.loan_data.get("loanSchedule", [])
            for schedule in self.loan_data['loanSchedule']:
                if schedule.get("Payment Date") == payment_date:
                    schedule['status'] = 0

            loan_id = self.loan_data['loan_id']
            DB.collection("Loan").document(loan_id).update({"loanSchedule": loan_schedule})

            QMessageBox.information(self, "Success", "Payment status updated to Paid.")
            self.load_loan_schedule(self.loan_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {e}")

    def on_guarantor_new_clicked(self):
        self.guarantorName.clear()
        self.guarantorType.setCurrentText("[Select]")
        self.guarantorRelation.setCurrentText("[Select]")
        self.guarantorSearchButton.setEnabled(True)
        self.guarantorType.setEnabled(True)
        self.guarantorRelation.setEnabled(True)
        self.guarantorSaveButton.setEnabled(True)
        self.guarantor_uid = None
        self.is_guarantor_edit_mode = False

    def on_guarantor_edit_clicked(self):
        self.guarantorSearchButton.setEnabled(True)
        self.guarantorType.setEnabled(True)
        self.guarantorRelation.setEnabled(True)
        self.guarantorSaveButton.setEnabled(True)
        self.is_guarantor_edit_mode = True

    def on_guarantor_save_clicked(self):
        if not self.guarantorName.text():
            QMessageBox.warning(self, "Warning", "Guarantor Name is required.")
            return

        if self.guarantorType.currentText() == "[Select]" or self.guarantorRelation.currentText() == "[Select]":
            QMessageBox.warning(self, "Warning", "Please select Guarantor Type and Relation.")
            return

        if not self.is_guarantor_edit_mode:
            guarantor_info = {
                "name": self.guarantorName.text(),
                "type": self.guarantorType.currentText(),
                "relation": self.guarantorRelation.currentText(),
                "uid": str(uuid.uuid4())
            }
            self.loan_data.setdefault("guarantors", []).append(guarantor_info)
            QMessageBox.information(self, "Success", "Guarantor added successfully.")
        else:
            if self.selected_guarantor_row is not None:
                self.loan_data["guarantors"][self.selected_guarantor_row] = {
                    "name": self.guarantorName.text(),
                    "type": self.guarantorType.currentText(),
                    "relation": self.guarantorRelation.currentText(),
                    "uid": self.guarantor_uid
                }
                QMessageBox.information(self, "Success", "Guarantor updated successfully.")

        loan_id = self.loan_data.get("loan_id")
        try:
            DB.collection("Loan").document(loan_id).update({"guarantors": firestore.ArrayUnion(self.loan_data["guarantors"])})
        except Exception:
            DB.collection("Loan").document(loan_id).set({"guarantors": self.loan_data["guarantors"]}, merge=True)

        self.load_guarantor_table(self.loan_data["guarantors"])
        self.clear_guarantor_inputs()

    def on_guarantor_delete_clicked(self):
        if self.selected_guarantor_row is None:
            QMessageBox.warning(self, "Warning", "Please select a guarantor to delete.")
            return

        loan_id = self.loan_data.get("loan_id")
        loan_ref = DB.collection("Loan").document(loan_id)
        loan_data = loan_ref.get().to_dict()

        if loan_data and "guarantors" in loan_data:
            guarantors = loan_data["guarantors"]

            if 0 <= self.selected_guarantor_row < len(guarantors):
                reply = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete '{guarantors[self.selected_guarantor_row]['name']}'?", QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    deleted_guarantor = guarantors.pop(self.selected_guarantor_row)
                    loan_ref.update({"guarantors": guarantors})
                    QMessageBox.information(self, "Success", f"Guarantor '{deleted_guarantor['name']}' deleted successfully.")
                    self.load_guarantor_table(guarantors)
                    self.clear_guarantor_inputs()
            else:
                QMessageBox.warning(self, "Error", "Selected guarantor not found.")

    def clear_guarantor_inputs(self):
        self.guarantorName.clear()
        self.guarantorType.setCurrentText("[Select]")
        self.guarantorRelation.setCurrentText("[Select]")
        self.guarantorSaveButton.setEnabled(False)
        self.guarantorEditButton.setEnabled(False)
        self.guarantorDeleteButton.setEnabled(False)
        self.guarantorType.setEnabled(False)
        self.guarantorRelation.setEnabled(False)
        self.selected_guarantor_row = None
    
    def open_select_guarantor_window(self):
        self.select_guarantor_window = SelectCustomerWindow()
        self.select_guarantor_window.customer_selected.connect(self.handle_guarantor_selected)
        self.select_guarantor_window.show()
    
    @pyqtSlot(dict)
    def handle_guarantor_selected(self, guarantor_data):
        # print(f"Guarantor selected: {guarantor_data}")
        self.guarantorName.setText(guarantor_data.get('name', ''))
        self.guarantor_uid = guarantor_data.get('uid', '')
        
    def on_collateral_new_clicked(self):
        self.clear_collateral_inputs()
        self.collateralType.setEnabled(True)
        self.collateralName.setEnabled(True)
        self.collateralDetails.setEnabled(True)
        self.collateralSaveButton.setEnabled(True)
        self.collateralEditButton.setEnabled(False)
        self.collateralDeleteButton.setEnabled(False)
        self.is_collateral_edit_mode = False

    def on_collateral_edit_clicked(self):
        if self.selected_collateral_row is None:
            QMessageBox.warning(self, "Warning", "Please select a guarantor to edit.")
            return

        self.collateralType.setEnabled(True)
        self.collateralName.setEnabled(True)
        self.collateralDetails.setEnabled(True)
        self.collateralSaveButton.setEnabled(True)
        self.is_collateral_edit_mode = True

    def on_collateral_save_clicked(self):
        if self.collateralType.currentText() == "[Select]":
            QMessageBox.warning(self, "Warning", "Please select Collateral Type")
            return

        if not self.collateralName.text():
            QMessageBox.warning(self, "Warning", "Collateral Name is required.")
            return

        if not self.collateralDetails.text():
            QMessageBox.warning(self, "Warning", "Collateral Details is required.")
            return

        if not self.is_collateral_edit_mode:
            collateral_info = {
                "details": self.collateralDetails.text(),
                "name": self.collateralName.text(),
                "type": self.collateralType.currentText()
            }
            self.loan_data.setdefault("collaterals", []).append(collateral_info)
            QMessageBox.information(self, "Success", "Collateral added successfully.")
        else:
            if self.selected_collateral_row is not None:
                self.loan_data["collaterals"][self.selected_collateral_row] = {
                    "details": self.collateralDetails.text(),
                    "name": self.collateralName.text(),
                    "type": self.collateralType.currentText()
                }
                QMessageBox.information(self, "Success", "Collateral updated successfully.")

        loan_id = self.loan_data.get("loan_id")
        try:
            DB.collection("Loan").document(loan_id).update({"collaterals": firestore.ArrayUnion(self.loan_data["collaterals"])})
        except Exception:
            DB.collection("Loan").document(loan_id).set({"collaterals": self.loan_data["collaterals"]}, merge=True)

        self.load_collateral_table(self.loan_data["collaterals"])
        self.clear_collateral_inputs()

    def on_collateral_delete_clicked(self):
        if self.selected_collateral_row is None:
            QMessageBox.warning(self, "Warning", "Please select a collateral to delete.")
            return

        loan_id = self.loan_data.get("loan_id")
        loan_ref = DB.collection("Loan").document(loan_id)
        loan_data = loan_ref.get().to_dict()

        if loan_data and "collaterals" in loan_data:
            collaterals = loan_data["collaterals"]

            if 0 <= self.selected_collateral_row < len(collaterals):
                reply = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete '{collaterals[self.selected_collateral_row]['name']}'?", QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    deleted_collateral = collaterals.pop(self.selected_collateral_row)
                    loan_ref.update({"collaterals": collaterals})
                    QMessageBox.information(self, "Success", f"Collateral '{deleted_collateral['name']}' deleted successfully.")
                    self.load_collateral_table(collaterals)
                    self.clear_collateral_inputs()
            else:
                QMessageBox.warning(self, "Error", "Selected collateral not found.")

    def clear_collateral_inputs(self):
        self.collateralType.setCurrentText("[Select]")
        self.collateralName.clear()
        self.collateralDetails.clear()
        self.collateralSaveButton.setEnabled(False)
        self.collateralEditButton.setEnabled(False)
        self.collateralDeleteButton.setEnabled(False)
        self.collateralType.setEnabled(False)
        self.collateralName.setEnabled(False)
        self.collateralDetails.setEnabled(False)
        self.selected_collateral_row = None

    def on_counseling_new_clicked(self):
        self.clear_counseling_inputs()
        self.counselingDate.setEnabled(True)
        self.counselingSubject.setEnabled(True)
        self.counselingDetails.setEnabled(True)
        self.counselingCorrectiveMeasure.setEnabled(True)
        self.counselingSaveButton.setEnabled(True)
        self.counselingEditButton.setEnabled(False)
        self.counselingDeleteButton.setEnabled(False)
        self.is_counseling_edit_mode = False

    def on_counseling_edit_clicked(self):
        if self.selected_counseling_row is None:
            QMessageBox.warning(self, "Warning", "Please select a counseling info to edit.")
            return

        self.counselingDate.setEnabled(True)
        self.counselingSubject.setEnabled(True)
        self.counselingDetails.setEnabled(True)
        self.counselingCorrectiveMeasure.setEnabled(True)
        self.counselingSaveButton.setEnabled(True)
        self.is_counseling_edit_mode = True

    def on_counseling_save_clicked(self):
        if not self.counselingSubject.text() or not self.counselingDetails.text() or not self.counselingCorrectiveMeasure.text():
            QMessageBox.warning(self, "Warning", "All fields are required.")
            return

        if not self.is_counseling_edit_mode:
            counseling_info = {
                "corrective_measure": self.counselingCorrectiveMeasure.text(),
                "date": self.counselingDate.date().toString("yyyy-MM-dd"),
                "details": self.counselingDetails.text(),
                "subject": self.counselingSubject.text()
            }
            self.loan_data.setdefault("counselings", []).append(counseling_info)
            QMessageBox.information(self, "Success", "Counseling added successfully.")
        else:
            if self.selected_counseling_row is not None:
                self.loan_data["counselings"][self.selected_counseling_row] = {
                    "corrective_measure": self.counselingCorrectiveMeasure.text(),
                    "date": self.counselingDate.date().toString("yyyy-MM-dd"),
                    "details": self.counselingDetails.text(),
                    "subject": self.counselingSubject.text()
                }
                QMessageBox.information(self, "Success", "Counseling updated successfully.")

        loan_id = self.loan_data.get("loan_id")
        try:
            DB.collection("Loan").document(loan_id).update({"counselings": firestore.ArrayUnion(self.loan_data["counselings"])})
        except Exception:
            DB.collection("Loan").document(loan_id).set({"counselings": self.loan_data["counselings"]}, merge=True)

        self.load_counseling_table(self.loan_data["counselings"])
        self.clear_counseling_inputs()

    def on_counseling_delete_clicked(self):
        if self.selected_counseling_row is None:
            QMessageBox.warning(self, "Warning", "Please select a counseling to delete.")
            return

        loan_id = self.loan_data.get("loan_id")
        loan_ref = DB.collection("Loan").document(loan_id)
        loan_data = loan_ref.get().to_dict()

        if loan_data and "counselings" in loan_data:
            counselings = loan_data["counselings"]

            if 0 <= self.selected_counseling_row < len(counselings):
                reply = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete?", QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    deleted_counseling = counselings.pop(self.selected_counseling_row)
                    loan_ref.update({"counselings": counselings})
                    QMessageBox.information(self, "Success", f"Counseling deleted successfully.")
                    self.load_counseling_table(counselings)
                    self.clear_counseling_inputs()
            else:
                QMessageBox.warning(self, "Error", "Selected counseling not found.")

    def clear_counseling_inputs(self):
        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

        self.counselingSaveButton.setEnabled(False)
        self.counselingEditButton.setEnabled(False)
        self.counselingDeleteButton.setEnabled(False)

        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)
        self.selected_counseling_row = None

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
            self.load_guarantor_table(loan_data['guarantors'])

    def load_guarantor_table(self, guarantors):
        model = QStandardItemModel(len(guarantors), 3)
        model.setHorizontalHeaderLabels(["Name", "Type", "Relation"])

        for row_idx, guarantor in enumerate(guarantors):
            model.setItem(row_idx, 0, QStandardItem(guarantor["name"]))
            model.setItem(row_idx, 1, QStandardItem(guarantor["type"]))
            model.setItem(row_idx, 2, QStandardItem(guarantor["relation"]))

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
            self.load_collateral_table(collateral_data)

    def load_collateral_table(self, data):
        columns = ["Type", "Name", "Details"]
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
            self.load_counseling_table(counseling_data)

    def load_counseling_table(self, data):
        columns = ["Date", "Subject", "Details", "Corrective Measure"]
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
            columns = ["Payment Date", "Principal", "Interest", "Total", "Status"]

            repayment_data = [item for item in schedule_data if item.get('status') == 0]
            received_data = [item for item in schedule_data if item.get('status') in [1, 2]]
 
            self.load_table(self.repaymentScheduleTable, repayment_data, columns)
            self.load_table(self.receivedTable, received_data, columns)

    def load_table(self, table_view, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        status_mapping = {0: 'Scheduled', 1: 'Paid', 2: 'Overdue'}

        for row_idx, item in enumerate(data):
            is_overdue = item.get("status") == 2
            
            for col_idx, column_name in enumerate(columns):
                item_value = self.create_read_only_item(item.get(column_name, ""))

                if is_overdue:
                    item_value.setForeground(QColor(Qt.red))

                model.setItem(row_idx, col_idx, item_value)

            status = item.get("status", 0)
            status_text = status_mapping.get(status, 'Unknown')
            status_item = self.create_read_only_item(status_text)

            if is_overdue:
                status_item.setForeground(QColor(Qt.red))

            model.setItem(row_idx, 4, status_item)

        table_view.setModel(model)
        table_view.resizeColumnsToContents()

    def create_read_only_item(self, text):
        item = QStandardItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item
