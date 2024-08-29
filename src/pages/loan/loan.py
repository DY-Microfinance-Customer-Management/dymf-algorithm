import sys, os
from datetime import datetime

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableView, QApplication
from PyQt5.QtCore import pyqtSlot, Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from pages.loan.select_customer import SelectCustomerWindow
from components import DB
from components.loan_calculator import LoanCalculator

class LoanWindow(QMainWindow):
    def __init__(self):
        super(LoanWindow, self).__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan.ui")
        uic.loadUi(ui_path, self)

        self.interestRate.setText("28")

        self.set_read_only(True)

        self.loanNumber.setReadOnly(True)
        self.loanStatus.setEnabled(False)

        self.customer_uid = None

        self.customerSearchButton.clicked.connect(self.check_and_open_select_customer_window)
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)

        self.setAttribute(Qt.WA_DeleteOnClose)
        self.existing_loan_id = None

        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        self.guarantorNewButton.setEnabled(True)
        self.guarantorSaveButton.setEnabled(False)
        self.guarantorEditButton.setEnabled(False)
        self.guarantorDeleteButton.setEnabled(False)

        self.collateralNewButton.clicked.connect(self.on_collateral_new_clicked)
        self.collateralSaveButton.clicked.connect(self.on_collateral_save_clicked)
        self.collateralEditButton.clicked.connect(self.on_collateral_edit_clicked)
        self.collateralDeleteButton.clicked.connect(self.on_collateral_delete_clicked)
        self.collateralTable.clicked.connect(self.on_collateral_table_clicked)

        self.collateralNewButton.setEnabled(True)
        self.collateralSaveButton.setEnabled(False)
        self.collateralEditButton.setEnabled(False)
        self.collateralDeleteButton.setEnabled(False)

        self.clear_collateral_fields()

        self.counselingNewButton.clicked.connect(self.on_counseling_new_clicked)
        self.counselingSaveButton.clicked.connect(self.on_counseling_save_clicked)
        self.counselingEditButton.clicked.connect(self.on_counseling_edit_clicked)
        self.counselingDeleteButton.clicked.connect(self.on_counseling_delete_clicked)
        self.counselingTable.clicked.connect(self.on_counseling_table_clicked)

        self.counselingNewButton.setEnabled(True)
        self.counselingSaveButton.setEnabled(False)
        self.counselingEditButton.setEnabled(False)
        self.counselingDeleteButton.setEnabled(False)
        
        self.clear_counseling_fields()
        
        self.guarantorSearchButton.setEnabled(False)

        self.guarantorType.setEnabled(False)
        self.guarantorRelation.setEnabled(False)

        self.repaymentScheduleTable.setSelectionBehavior(QTableView.SelectRows)
        self.receivedTable.setSelectionBehavior(QTableView.SelectRows)

        self.repaymentScheduleTable.clicked.connect(self.handle_table_click)
        self.receivedTable.clicked.connect(self.handle_received_table_click)

        self.paidButton.clicked.connect(self.on_paid_button_clicked)
        self.deleteButton.clicked.connect(self.on_delete_button_clicked)

        self.guarantorNewButton.clicked.connect(self.on_guarantor_new_clicked)
        self.guarantorSaveButton.clicked.connect(self.on_guarantor_save_clicked)
        self.guarantorSearchButton.clicked.connect(self.open_select_guarantor_window)
        self.guarantorEditButton.clicked.connect(self.on_guarantor_edit_clicked)
        self.guarantorDeleteButton.clicked.connect(self.on_guarantor_delete_clicked)

        self.selected_row = None
        self.selected_received_row = None

        self.guarantorTable.clicked.connect(self.on_guarantor_table_clicked)

        self.selected_guarantor_row = None

        self.loanNewButton.clicked.connect(self.on_loan_new_button_clicked)
        self.loanNewButton.setEnabled(False)

        self.show()

    def set_read_only(self, read_only):
        line_edits = [
            self.loanAmount, self.interestRate, self.expiry, self.counselingDate, self.counselingSubject, self.counselingDetails, self.counselingCorrectiveMeasure
        ]
        date_edits = [
            self.contractDate
        ]
        combo_boxes = [
            self.loanType, self.loanOfficer, self.loanRepaymentCycle
        ]
        check_boxes = [
            self.checkBoxMale, self.checkBoxFemale
        ]

        for line_edit in line_edits:
            line_edit.setReadOnly(read_only)
        
        for date_edit in date_edits:
            date_edit.setReadOnly(read_only)
        
        for combo_box in combo_boxes:
            combo_box.setEnabled(not read_only)
        
        for check_box in check_boxes:
            check_box.setEnabled(False)

    def check_and_open_select_customer_window(self):
        if self.customerName.text():
            reply = QMessageBox.question(
                self,
                'Confirm',
                'There is already data being entered. Do you want to clear it?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                self.clear_all_fields()
                self.reset_ui_state_after_clear()  # 상태 초기화를 위해 추가된 메서드 호출
                self.open_select_customer_window()
        else:
            self.open_select_customer_window()

    def reset_ui_state_after_clear(self):
        # clear_all_fields() 후 필요한 UI 상태 재설정
        self.interestRate.setText("28")  # interestRate를 28로 다시 설정
        self.set_read_only(True)  # 고객을 다시 선택하기 전까지는 모든 필드를 비활성화
        self.customer_uid = None  # customer_uid 초기화

    def open_select_customer_window(self):
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    def open_select_guarantor_window(self):
        self.select_guarantor_window = SelectCustomerWindow()
        self.select_guarantor_window.customer_selected.connect(self.handle_guarantor_selected)
        self.select_guarantor_window.show()

    @pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        print(f"Customer selected: {customer_data}")

        self.customerName.setText(customer_data.get('name', ''))
        self.customerContact.setText(customer_data.get('phone', ''))
        self.customer_uid = customer_data.get('uid', '')  # 고객 UID 저장
        
        birth_timestamp = customer_data.get('birth', 0)
        if isinstance(birth_timestamp, (int, float)):
            birth_date = datetime.fromtimestamp(birth_timestamp).strftime('%Y-%m-%d')
            self.customerDateOfBirth.setText(birth_date)
        else:
            self.customerDateOfBirth.setText('')

        gender = customer_data.get('gender', '')
        self.checkBoxMale.setChecked(gender == 0)
        self.checkBoxFemale.setChecked(gender == 1)

        current_date = QDate.currentDate()
        self.contractDate.setDate(current_date)
        self.contractDate.setReadOnly(False)

        # 고객이 선택된 후 버튼 활성화
        self.enable_new_buttons()

        self.check_existing_customer_loan()

    @pyqtSlot(dict)
    def handle_guarantor_selected(self, guarantor_data):
        # print(f"Guarantor selected: {guarantor_data}")
        self.guarantorName.setText(guarantor_data.get('name', ''))
        self.guarantor_uid = guarantor_data.get('uid', '')

    def handle_table_click(self, index):
        if index.isValid():
            self.selected_row = index.row()
            model = index.model()
            status_value = model.data(model.index(self.selected_row, 1))

            if status_value == "Scheduled":
                self.paidButton.setEnabled(True)
            else:
                self.paidButton.setEnabled(False)

    def handle_received_table_click(self, index):
        if index.isValid():
            self.selected_received_row = index.row()
            self.deleteButton.setEnabled(True)
            self.receivedTable.selectRow(self.selected_received_row)

    def on_guarantor_new_clicked(self):
        self.guarantorName.clear()
        self.guarantorType.setCurrentText("[Select]")
        self.guarantorRelation.setCurrentText("[Select]")
        self.guarantorSearchButton.setEnabled(True)
        self.guarantorType.setEnabled(True)
        self.guarantorRelation.setEnabled(True)
        self.guarantorSaveButton.setEnabled(True)

        self.guarantor_uid = None
        self.is_edit_mode = False

    def on_guarantor_edit_clicked(self):
        self.guarantorSearchButton.setEnabled(True)
        self.guarantorType.setEnabled(True)
        self.guarantorRelation.setEnabled(True)
        self.guarantorSaveButton.setEnabled(True)
        self.is_edit_mode = True

    def on_guarantor_save_clicked(self):
        if not self.guarantorName.text():
            QMessageBox.warning(self, "Warning", "Guarantor Name is required.")
            return

        if self.guarantorType.currentText() == "[Select]" or self.guarantorRelation.currentText() == "[Select]":
            QMessageBox.warning(self, "Warning", "Please select Guarantor Type and Relation.")
            return

        if not self.existing_loan_id:
            QMessageBox.critical(self, "Error", "Loan ID is missing.")
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        guarantor_info = {
            "name": self.guarantorName.text(),
            "type": self.guarantorType.currentText(),
            "relation": self.guarantorRelation.currentText(),
            "uid": self.guarantor_uid
        }

        if not self.is_edit_mode:
            if "guarantors" not in loan_data:
                loan_data["guarantors"] = []

            if any(guarantor["uid"] == self.guarantor_uid for guarantor in loan_data["guarantors"]):
                QMessageBox.warning(self, "Warning", "This guarantor has already been added.")
                return

            loan_data["guarantors"].append(guarantor_info)
            QMessageBox.information(self, "Success", "Guarantor added successfully.")
        else:
            if self.selected_guarantor_row is not None and self.selected_guarantor_row < len(loan_data["guarantors"]):
                loan_data["guarantors"][self.selected_guarantor_row] = guarantor_info
                QMessageBox.information(self, "Success", "Guarantor updated successfully.")
            else:
                QMessageBox.warning(self, "Error", "Selected row is out of bounds.")
                return

        loan_ref.update({"guarantors": loan_data["guarantors"]})

        self.load_guarantor_table(loan_data["guarantors"])

        self.guarantorName.clear()
        self.guarantorType.setCurrentText("[Select]")
        self.guarantorRelation.setCurrentText("[Select]")
        self.guarantorType.setEnabled(False)
        self.guarantorRelation.setEnabled(False)
        self.guarantorSearchButton.setEnabled(False)
        self.guarantorSaveButton.setEnabled(False)
        self.is_edit_mode = False

    def on_guarantor_delete_clicked(self):
        if self.selected_guarantor_row is None:
            QMessageBox.warning(self, "Warning", "Please select a guarantor to delete.")
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        if loan_data and "guarantors" in loan_data:
            guarantors = loan_data["guarantors"]

            if 0 <= self.selected_guarantor_row < len(guarantors):
                reply = QMessageBox.question(self, 'Confirm', f"Are you sure you want to delete '{guarantors[self.selected_guarantor_row]['name']}'?", QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    deleted_guarantor = guarantors.pop(self.selected_guarantor_row)
                    loan_ref.update({"guarantors": guarantors})
                    QMessageBox.information(self, "Success", f"Guarantor '{deleted_guarantor['name']}' deleted successfully.")

                    self.load_guarantor_table(guarantors)
                    self.selected_guarantor_row = None
                    self.guarantorDeleteButton.setEnabled(False)
                    self.guarantorEditButton.setEnabled(False)
            else:
                QMessageBox.warning(self, "Error", "The selected row is out of bounds.")
        else:
            QMessageBox.warning(self, "Error", "No guarantors found in the loan document.")

    def load_guarantor_table(self, guarantors):
        model = QStandardItemModel(len(guarantors), 3)
        model.setHorizontalHeaderLabels(["Guarantor Name", "Guarantor Type", "Guarantor Relation"])

        for row_idx, guarantor in enumerate(guarantors):
            model.setItem(row_idx, 0, QStandardItem(guarantor["name"]))
            model.setItem(row_idx, 1, QStandardItem(guarantor["type"]))
            model.setItem(row_idx, 2, QStandardItem(guarantor["relation"]))

        self.guarantorTable.setModel(model)
        self.guarantorTable.resizeColumnsToContents()

    def load_guarantors_to_table(self):
        if self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "guarantors" in loan_data:
                guarantor_data = loan_data["guarantors"]

                self.clear_table(self.guarantorTable)

                column_order = ["name", "type", "relation"]

                model = QStandardItemModel(len(guarantor_data), len(column_order))
                model.setHorizontalHeaderLabels(["Name", "Type", "Relation"])

                for row_idx, guarantor in enumerate(guarantor_data):
                    for col_idx, column in enumerate(column_order):
                        value = guarantor.get(column, "")
                        item = QStandardItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        model.setItem(row_idx, col_idx, item)

                self.guarantorTable.setModel(model)
                self.guarantorTable.resizeColumnsToContents()

    def on_guarantor_table_clicked(self, index):
        if index.isValid():
            self.selected_guarantor_row = index.row()
            
            self.guarantorEditButton.setEnabled(True)
            self.guarantorDeleteButton.setEnabled(True)
            
            model = self.guarantorTable.model()
            self.guarantorName.setText(model.index(self.selected_guarantor_row, 0).data())
            self.guarantorType.setCurrentText(model.index(self.selected_guarantor_row, 1).data())
            self.guarantorRelation.setCurrentText(model.index(self.selected_guarantor_row, 2).data())

    def on_collateral_new_clicked(self):
        self.collateralType.setCurrentText("[Select]")
        self.collateralName.clear()
        self.collateralDetails.clear()

        self.collateralType.setEnabled(True)
        self.collateralName.setEnabled(True)
        self.collateralDetails.setEnabled(True)
        self.collateralSaveButton.setEnabled(True)

        self.selected_collateral_row = None

    def on_collateral_save_clicked(self):
        collateral_info = {
            "type": self.collateralType.currentText(),
            "name": self.collateralName.text(),
            "details": self.collateralDetails.text()
        }

        if collateral_info["type"] == "[Select]" or not collateral_info["name"] or not collateral_info["details"]:
            QMessageBox.warning(self, "Warning", "Please fill in all collateral fields.")
            return

        if not self.existing_loan_id:
            QMessageBox.critical(self, "Error", "Loan ID is missing.")
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        if loan_data:
            if "collaterals" not in loan_data:
                loan_data["collaterals"] = []

            if self.selected_collateral_row is not None:
                loan_data["collaterals"][self.selected_collateral_row] = collateral_info
            else:
                loan_data["collaterals"].append(collateral_info)

            loan_ref.update(loan_data)
            QMessageBox.information(self, "Success", "Collateral information saved successfully.")
            self.load_collateral_data()

        self.clear_collateral_fields()

    def on_collateral_edit_clicked(self):
        if self.selected_collateral_row is not None:
            self.collateralType.setEnabled(True)
            self.collateralName.setEnabled(True)
            self.collateralDetails.setEnabled(True)
            self.collateralSaveButton.setEnabled(True)

    def on_collateral_delete_clicked(self):
        if self.selected_collateral_row is not None and self.existing_loan_id:
            reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this collateral?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                loan_ref = DB.collection("Loan").document(self.existing_loan_id)
                loan_doc = loan_ref.get()
                loan_data = loan_doc.to_dict()

                if loan_data and "collaterals" in loan_data:
                    del loan_data["collaterals"][self.selected_collateral_row]
                    loan_ref.update(loan_data)
                    QMessageBox.information(self, "Success", "Collateral entry deleted successfully.")
                    self.load_collateral_data()

                    self.collateralEditButton.setEnabled(False)
                    self.collateralDeleteButton.setEnabled(False)
                    self.clear_collateral_fields()

    def load_collateral_data(self):
        if self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "collaterals" in loan_data:
                collateral_data = loan_data["collaterals"]

                self.clear_table(self.collateralTable)

                self.load_collateral_table(self.collateralTable, collateral_data, columns=["Type", "Name", "Details"])

    def clear_collateral_fields(self):
        self.collateralType.setCurrentText("[Select]")
        self.collateralName.clear()
        self.collateralDetails.clear()

        self.collateralType.setEnabled(False)
        self.collateralName.setEnabled(False)
        self.collateralDetails.setEnabled(False)
        self.collateralSaveButton.setEnabled(False)

    def on_collateral_table_clicked(self, index):
        if index.isValid():
            self.selected_collateral_row = index.row()

            self.collateralEditButton.setEnabled(True)
            self.collateralDeleteButton.setEnabled(True)

            model = self.collateralTable.model()
            self.collateralType.setCurrentText(model.index(self.selected_collateral_row, 0).data())
            self.collateralName.setText(model.index(self.selected_collateral_row, 1).data())
            self.collateralDetails.setText(model.index(self.selected_collateral_row, 2).data())

    def load_collateral_table(self, table, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, row_data in enumerate(data):
            for col_idx, column in enumerate(columns):
                value = row_data.get(column.lower(), "")
                item = QStandardItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model.setItem(row_idx, col_idx, item)

        table.setModel(model)
        table.resizeColumnsToContents()

    def on_counseling_new_clicked(self):
        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

        self.counselingDate.setEnabled(True)
        self.counselingSubject.setEnabled(True)
        self.counselingDetails.setEnabled(True)
        self.counselingCorrectiveMeasure.setEnabled(True)
        self.counselingSaveButton.setEnabled(True)

        self.selected_counseling_row = None

    def on_counseling_save_clicked(self):
        counseling_info = {
            "date": self.counselingDate.date().toString("yyyy-MM-dd"),
            "subject": self.counselingSubject.text(),
            "details": self.counselingDetails.text(),
            "corrective_measure": self.counselingCorrectiveMeasure.text()
        }

        if not counseling_info["subject"] or not counseling_info["details"] or not counseling_info["corrective_measure"]:
            QMessageBox.warning(self, "Warning", "Please fill in all counseling fields.")
            return

        if not self.existing_loan_id:
            QMessageBox.critical(self, "Error", "Loan ID is missing.")
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        if loan_data:
            if "counselings" not in loan_data:
                loan_data["counselings"] = []

            if self.selected_counseling_row is not None:
                loan_data["counselings"][self.selected_counseling_row] = counseling_info
            else:
                loan_data["counselings"].append(counseling_info)

            loan_ref.update(loan_data)
            QMessageBox.information(self, "Success", "Counseling information saved successfully.")
            self.load_counseling_data()

        self.clear_counseling_fields()

    def on_counseling_edit_clicked(self):
        if self.selected_counseling_row is not None:
            self.counselingDate.setEnabled(True)
            self.counselingSubject.setEnabled(True)
            self.counselingDetails.setEnabled(True)
            self.counselingCorrectiveMeasure.setEnabled(True)
            self.counselingSaveButton.setEnabled(True)

    def on_counseling_delete_clicked(self):
        if self.selected_counseling_row is not None and self.existing_loan_id:
            reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this counseling?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                loan_ref = DB.collection("Loan").document(self.existing_loan_id)
                loan_doc = loan_ref.get()
                loan_data = loan_doc.to_dict()

                if loan_data and "counselings" in loan_data:
                    del loan_data["counselings"][self.selected_counseling_row]
                    loan_ref.update(loan_data)
                    QMessageBox.information(self, "Success", "Counseling entry deleted successfully.")
                    self.load_counseling_data()

                    self.counselingEditButton.setEnabled(False)
                    self.counselingDeleteButton.setEnabled(False)
                    self.clear_counseling_fields()

    def load_counseling_data(self):
        if self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "counselings" in loan_data:
                counseling_data = loan_data["counselings"]

                self.clear_table(self.counselingTable)

                self.load_counseling_table(self.counselingTable, counseling_data, columns=["Date", "Subject", "Details", "Corrective Measure"])

    def clear_counseling_fields(self):
        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)
        self.counselingSaveButton.setEnabled(False)

    def on_counseling_table_clicked(self, index):
        if index.isValid():
            self.selected_counseling_row = index.row()

            self.counselingEditButton.setEnabled(True)
            self.counselingDeleteButton.setEnabled(True)

            model = self.counselingTable.model()
            self.counselingDate.setDate(QDate.fromString(model.index(self.selected_counseling_row, 0).data(), "yyyy-MM-dd"))
            self.counselingSubject.setText(model.index(self.selected_counseling_row, 1).data())
            self.counselingDetails.setText(model.index(self.selected_counseling_row, 2).data())
            self.counselingCorrectiveMeasure.setText(model.index(self.selected_counseling_row, 3).data())

    def clear_counseling_fields(self):
        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)
        self.counselingSaveButton.setEnabled(False)

    def load_counseling_table(self, table, data, columns):
        model = QStandardItemModel(len(data), len(columns))
        model.setHorizontalHeaderLabels(columns)

        for row_idx, row_data in enumerate(data):
            for col_idx, column in enumerate(columns):
                value = row_data.get(column.lower().replace(" ", "_"), "")
                item = QStandardItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model.setItem(row_idx, col_idx, item)

        table.setModel(model)
        table.resizeColumnsToContents()

    def check_existing_customer_loan(self):
        if not self.customer_uid:
            QMessageBox.warning(self, "Warning", "Customer UID is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("customer_uid", "==", self.customer_uid).get()

        if len(query) > 0:
            reply = QMessageBox.question(
                self,
                'Confirm',
                'A loan already exists for this customer. Do you want to continue?',
                QMessageBox.Ok | QMessageBox.Cancel
            )

            if reply != QMessageBox.Ok:
                self.clear_all_fields()
                return

        self.generate_loan_number()
        self.set_read_only(False)

    def generate_loan_number(self):
        current_year_month = datetime.now().strftime("%Y%m")

        loans_ref = DB.collection("Loan")
        loans = loans_ref.order_by("loanNumber", direction="DESCENDING").limit(1).stream()

        max_sequence_number = 0
        for loan in loans:
            loan_number = loan.to_dict().get("loanNumber", "")
            if loan_number.startswith(current_year_month):
                sequence_number = int(loan_number[6:])
                max_sequence_number = max(max_sequence_number, sequence_number)

        new_sequence_number = max_sequence_number + 1
        new_loan_number = f"{current_year_month}{new_sequence_number:07d}"

        self.loanNumber.setText(new_loan_number)

    def enable_new_buttons(self):
        # 고객 선택 후 필요한 버튼 활성화
        self.guarantorNewButton.setEnabled(True)
        self.collateralNewButton.setEnabled(True)
        self.counselingNewButton.setEnabled(True)

    def clear_all_fields(self):
        # 모든 필드를 초기화
        self.customerName.clear()
        self.customerContact.clear()
        self.customerDateOfBirth.clear()
        self.loanAmount.clear()
        self.interestRate.setText("28")
        self.checkBoxMale.setChecked(False)
        self.checkBoxFemale.setChecked(False)
        self.loanNumber.clear()
        self.contractDate.setDate(QDate.currentDate())

        self.guarantorLoanNumber.clear()
        self.guarantorLoanStatus.clear()
        self.guarantorLoanOfficer.clear()
        self.guarantorContractDate.clear()
        self.guarantorLoanType.clear()
        self.guarantorLoanAmount.clear()
        self.guarantorExpiry.clear()
        self.guarantorRepaymentCycle.clear()
        self.guarantorInterestRate.clear()

        self.collateralLoanNumber.clear()
        self.collateralLoanStatus.clear()
        self.collateralLoanOfficer.clear()
        self.collateralContractDate.clear()
        self.collateralLoanType.clear()
        self.collateralLoanAmount.clear()
        self.collateralExpiry.clear()
        self.collateralRepaymentCycle.clear()
        self.collateralInterestRate.clear()

        self.counselingLoanNumber.clear()
        self.counselingLoanStatus.clear()
        self.counselingLoanOfficer.clear()
        self.counselingContractDate.clear()
        self.counselingLoanType.clear()
        self.counselingLoanAmount.clear()
        self.counselingExpiry.clear()
        self.counselingRepaymentCycle.clear()
        self.counselingInterestRate.clear()
        
        self.existing_loan_id = None
        self.customer_uid = None
        self.expiry.clear()
        self.set_read_only(True)

        self.clear_table(self.repaymentScheduleTable)
        self.clear_table(self.receivedTable)
        self.clear_table(self.loanScheduleTable)
        
        self.guarantorName.clear()
        self.guarantorType.setCurrentText("[Select]")
        self.guarantorRelation.setCurrentText("[Select]")
        self.guarantor_uid = None
        self.clear_table(self.guarantorTable)

        self.guarantorSearchButton.setEnabled(False)
        self.guarantorType.setEnabled(False)
        self.guarantorRelation.setEnabled(False)
        self.guarantorSaveButton.setEnabled(False)
        self.guarantorEditButton.setEnabled(False)
        self.guarantorDeleteButton.setEnabled(False)

        self.collateralType.setCurrentText("[Select]")
        self.collateralName.clear()
        self.collateralDetails.clear()
        self.clear_table(self.collateralTable)

        self.collateralType.setEnabled(False)
        self.collateralName.setEnabled(False)
        self.collateralDetails.setEnabled(False)
        self.collateralSaveButton.setEnabled(False)
        self.collateralEditButton.setEnabled(False)
        self.collateralDeleteButton.setEnabled(False)

        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()
        self.clear_table(self.counselingTable)

        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)
        self.counselingSaveButton.setEnabled(False)
        self.counselingEditButton.setEnabled(False)
        self.counselingDeleteButton.setEnabled(False)

        self.paidButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.loanNewButton.setEnabled(False)

    def closeEvent(self, event):
        if self.customerName.text():
            reply = QMessageBox.question(
                self,
                'Confirm',
                'You have unsaved data. Are you sure you want to exit?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def on_calculate_button_clicked(self):
        self.check_existing_loan()

    def check_existing_loan(self):
        loan_number = self.loanNumber.text()
        if not loan_number:
            QMessageBox.warning(self, "Warning", "Loan number is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("loanNumber", "==", loan_number).get()

        if len(query) > 0:
            self.existing_loan_id = query[0].id
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Do you want to re-register the repayment schedule?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
        else:
            self.existing_loan_id = None
            reply = QMessageBox.question(
                self,
                'Confirm',
                'Do you want to register the repayment schedule?',
                QMessageBox.Ok | QMessageBox.Cancel
            )

        if reply == QMessageBox.Ok:
            self.calculate_loan_schedule()
            self.save_loan_to_firestore()

    def save_loan_to_firestore(self):
        loan_info = {
            "customer_uid": self.customer_uid,
            "customerName": self.customerName.text(),
            "customerContact": self.customerContact.text(),
            "customerDateOfBirth": self.customerDateOfBirth.text(),
            "loanAmount": self.loanAmount.text(),
            "interestRate": self.interestRate.text(),
            "expiry": self.expiry.text(),
            "loanType": self.loanType.currentText(),
            "loanOfficer": self.loanOfficer.currentText(),
            "loanRepaymentCycle": self.loanRepaymentCycle.currentText(),
            "loanNumber": self.loanNumber.text(),
            "contractDate": self.contractDate.date().toString("yyyy-MM-dd"),
            "loanStatus": self.loanStatus.currentText(),
            "loan_id": self.existing_loan_id if self.existing_loan_id else None
        }

        if hasattr(self, 'schedule_df'):
            loan_schedule = self.schedule_df.to_dict(orient="records")
            for schedule_item in loan_schedule:
                schedule_item['status'] = 0
            loan_info["loanSchedule"] = loan_schedule

        try:
            if self.existing_loan_id:
                loan_info["loan_id"] = self.existing_loan_id
                DB.collection("Loan").document(self.existing_loan_id).set(loan_info)
            else:
                doc_ref = DB.collection("Loan").add(loan_info)
                self.existing_loan_id = doc_ref[1].id
                loan_info["loan_id"] = self.existing_loan_id
                DB.collection("Loan").document(self.existing_loan_id).set(loan_info)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the loan: {e}")

    def calculate_loan_schedule(self):
        if not self.customerName.text():
            QMessageBox.warning(self, "Warning", "Please select a customer before calculating.")
            return

        if not all([
            self.loanType.currentText(),
            self.loanAmount.text(),
            self.interestRate.text(),
            self.expiry.text(),
            self.loanRepaymentCycle.currentText()
        ]):
            QMessageBox.warning(self, "Warning", "Please fill in Loan Type, Loan Amount, Interest Rate, Expiry, and Repayment Cycle.")
            return

        try:
            principal = int(self.loanAmount.text())
            annual_interest_rate = float(self.interestRate.text()) / 100
            expiration_months = int(self.expiry.text())

            cycle_text = self.loanRepaymentCycle.currentText()
            cycle_mapping = {
                "Monthly": "month",
                "4 Week": "4week",
                "2 Week": "2week",
                "Weekly": "week"
            }
            cycle = cycle_mapping.get(cycle_text)

            if not cycle:
                QMessageBox.critical(self, "Error", "Invalid repayment cycle selected.")
                return

            calculator = LoanCalculator(
                start_date=self.contractDate.date().toPyDate(),
                principal=principal,
                expiration_months=expiration_months,
                annual_interest_rate=annual_interest_rate
            )

            loan_type = self.loanType.currentText().lower()
            if loan_type == "equal":
                self.schedule_df = calculator.equal_payment(cycle=cycle)
            elif loan_type == "equal principal":
                self.schedule_df = calculator.equal_principal_payment(cycle=cycle)
            elif loan_type == "bullet":
                self.schedule_df = calculator.bullet_payment(cycle=cycle)
            else:
                QMessageBox.critical(self, "Error", "Invalid loan type selected.")
                return

            self.display_schedule(self.schedule_df)
            self.update_other_tabs()

            self.loanNewButton.setEnabled(True)

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def on_loan_new_button_clicked(self):
        if self.customerName.text():
            reply = QMessageBox.question(
                self,
                'Confirm',
                'There is already data being entered. Do you want to clear it?',
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if reply == QMessageBox.Ok:
                self.clear_all_fields()
                self.reset_ui_state_after_clear()
                self.open_select_customer_window()
        else:
            self.open_select_customer_window()

    def display_schedule(self, df: pd.DataFrame):
        df_with_status = df.copy()

        if 'Status' not in df_with_status.columns:
            df_with_status['Status'] = 0

        df_with_status['Status'] = df_with_status['Status'].apply(lambda x: 'Scheduled' if x == 0 else 'Paid')

        if 'Remaining Balance' in df_with_status.columns:
            df_with_status = df_with_status.drop(columns=['Remaining Balance'])

        if 'Total' in df_with_status['Payment Date'].values:
            df_with_status = df_with_status[df_with_status['Payment Date'] != 'Total']

        cols = df_with_status.columns.tolist()
        status_idx = cols.index('Payment Date') + 1
        cols.insert(status_idx, cols.pop(cols.index('Status')))
        df_with_status = df_with_status[cols]

        vertical_header = [str(i) for i in df['Period'].values]
        df_loan_table = df.drop(columns=['Period'])
        df_with_status = df_with_status.drop(columns=['Period'])

        def format_number(value):
            try:
                return "{:,}".format(int(value))
            except ValueError:
                return value

        for column in df_loan_table.columns:
            df_loan_table[column] = df_loan_table[column].apply(format_number)

        for column in df_with_status.columns:
            df_with_status[column] = df_with_status[column].apply(format_number)

        model_loan_table = QStandardItemModel(df_loan_table.shape[0], df_loan_table.shape[1])
        model_loan_table.setHorizontalHeaderLabels(df_loan_table.columns.tolist())
        model_loan_table.setVerticalHeaderLabels(vertical_header)

        for row in range(df_loan_table.shape[0]):
            for col in range(df_loan_table.shape[1]):
                item = QStandardItem(df_loan_table.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model_loan_table.setItem(row, col, item)

        model_repayment_table = QStandardItemModel(df_with_status.shape[0], df_with_status.shape[1])
        model_repayment_table.setHorizontalHeaderLabels(df_with_status.columns.tolist())
        model_repayment_table.setVerticalHeaderLabels(vertical_header)

        for row in range(df_with_status.shape[0]):
            for col in range(df_with_status.shape[1]):
                item = QStandardItem(df_with_status.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model_repayment_table.setItem(row, col, item)

        self.loanScheduleTable.setModel(model_loan_table)
        self.loanScheduleTable.resizeColumnsToContents()

        self.repaymentScheduleTable.setModel(model_repayment_table)
        self.repaymentScheduleTable.resizeColumnsToContents()

    def update_other_tabs(self):
        self.guarantorLoanNumber.setText(self.loanNumber.text())
        self.collateralLoanNumber.setText(self.loanNumber.text())
        self.counselingLoanNumber.setText(self.loanNumber.text())

        self.guarantorLoanStatus.setText(self.loanStatus.currentText())
        self.collateralLoanStatus.setText(self.loanStatus.currentText())
        self.counselingLoanStatus.setText(self.loanStatus.currentText())

        self.guarantorLoanOfficer.setText(self.loanOfficer.currentText())
        self.collateralLoanOfficer.setText(self.loanOfficer.currentText())
        self.counselingLoanOfficer.setText(self.loanOfficer.currentText())

        contract_date_str = self.contractDate.date().toString("yyyy-MM-dd")
        self.guarantorContractDate.setText(contract_date_str)
        self.collateralContractDate.setText(contract_date_str)
        self.counselingContractDate.setText(contract_date_str)

        self.guarantorLoanType.setText(self.loanType.currentText())
        self.collateralLoanType.setText(self.loanType.currentText())
        self.counselingLoanType.setText(self.loanType.currentText())

        self.guarantorLoanAmount.setText(self.loanAmount.text())
        self.collateralLoanAmount.setText(self.loanAmount.text())
        self.counselingLoanAmount.setText(self.loanAmount.text())

        self.guarantorInterestRate.setText(self.interestRate.text())
        self.collateralInterestRate.setText(self.interestRate.text())
        self.counselingInterestRate.setText(self.interestRate.text())

        self.guarantorExpiry.setText(self.expiry.text())
        self.collateralExpiry.setText(self.expiry.text())
        self.counselingExpiry.setText(self.expiry.text())

        self.guarantorRepaymentCycle.setText(self.loanRepaymentCycle.currentText())
        self.collateralRepaymentCycle.setText(self.loanRepaymentCycle.currentText())
        self.counselingRepaymentCycle.setText(self.loanRepaymentCycle.currentText())

    def on_paid_button_clicked(self):
        if self.selected_row is not None and self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "loanSchedule" in loan_data:
                loan_schedule = loan_data["loanSchedule"]

                period_value = self.selected_row + 1

                for schedule in loan_schedule:
                    try:
                        schedule_period = int(schedule.get("Period", 0))
                    except ValueError:
                        schedule_period = 0

                    if schedule_period == period_value:
                        schedule["status"] = 1

                loan_ref.update({"loanSchedule": loan_schedule})
                self.load_data_into_tables()

    def on_delete_button_clicked(self):
        if self.selected_received_row is not None and self.existing_loan_id:
            loan_ref = DB.collection("Loan").document(self.existing_loan_id)
            loan_doc = loan_ref.get()
            loan_data = loan_doc.to_dict()

            if loan_data and "loanSchedule" in loan_data:
                loan_schedule = loan_data["loanSchedule"]

                period_value = self.selected_received_row + 1

                for schedule in loan_schedule:
                    try:
                        schedule_period = int(schedule.get("Period", 1))
                    except ValueError:
                        schedule_period = 1

                    if schedule_period == period_value:
                        schedule["status"] = 0

                loan_ref.update({"loanSchedule": loan_schedule})
                self.load_data_into_tables()

                self.selected_received_row = None
                self.deleteButton.setEnabled(False)

    def load_data_into_tables(self):
        if not self.existing_loan_id:
            return

        loan_ref = DB.collection("Loan").document(self.existing_loan_id)
        loan_doc = loan_ref.get()
        loan_data = loan_doc.to_dict()

        if loan_data and "loanSchedule" in loan_data:
            repayment_data = []
            received_data = []

            for schedule in loan_data["loanSchedule"]:
                schedule.pop("Remaining Balance", None)

                if schedule["status"] == 0:
                    repayment_data.append(schedule)
                elif schedule["status"] == 1:
                    received_data.append(schedule)

            self.clear_table(self.repaymentScheduleTable)
            self.clear_table(self.receivedTable)

            if repayment_data:
                self.load_table(self.repaymentScheduleTable, repayment_data, status_included=True)

            if received_data:
                self.load_table(self.receivedTable, received_data, status_included=True)

    def load_table(self, table, data, status_included=False):
        if not data:
            return

        column_order = ["Payment Date", "Status", "Principal", "Interest", "Total"]

        model = QStandardItemModel(len(data), len(column_order))
        model.setHorizontalHeaderLabels(column_order)

        for row_idx, row_data in enumerate(data):
            period_value = row_data.get("Period", 0)

            try:
                period_value = int(period_value)
            except ValueError:
                period_value = 0

            row_idx = period_value - 1

            for col_idx, column in enumerate(column_order):
                value = row_data.get(column, "")

                if column == "Status":
                    if status_included:
                        status_value = row_data.get("status", 0)
                        if status_value == 0:
                            value = "Scheduled"
                        elif status_value == 1:
                            value = "Paid"

                item = QStandardItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model.setItem(row_idx, col_idx, item)

        table.setModel(model)
        table.resizeColumnsToContents()

    def clear_table(self, table):
        model = QStandardItemModel(0, 0)
        table.setModel(model)

def main():
    app = QApplication(sys.argv)
    window = LoanWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
