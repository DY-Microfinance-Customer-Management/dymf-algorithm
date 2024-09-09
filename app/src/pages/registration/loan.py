import sys, os
from datetime import datetime

import pandas as pd
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QDialog
from PyQt5.QtCore import pyqtSlot, Qt, QDate, QModelIndex, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

from src.components import DB
from src.components.loan_calculator import LoanCalculator
from src.components.select_customer import SelectCustomerWindow
from src.components.select_loan_officer import SelectLoanOfficerWindow
from src.components.select_guarantors import SelectGuarantorWindow

class RegistrationLoanApp(QMainWindow):

    def __init__(self):
        # ui file
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "loan.ui")
        uic.loadUi(ui_path, self)

        # icon
        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # window
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(self.size())

        # init ui
        self.customer_uid = None
        self.checkBoxMale.setEnabled(False)
        self.checkBoxFemale.setEnabled(False)
        self.loanNewButton.setEnabled(False)
        self.loanStatus.setEnabled(False)
        self.loanNumber.setEnabled(False)
        self.loanType.setEnabled(False)
        self.set_input_enabled(False, False, False, False)
        self.interestRate.setText("28")
        self.contractDate.setDate(QDate.currentDate())

        # function connection
        self.set_connections()

    ### ---------------------------------- Function Connections ---------------------------------- ###
    def set_connections(self):
        # 1. Search and Select Customer + Select Loan Officer
        self.customerSearchButton.clicked.connect(self.check_and_open_select_customer_window)
        self.searchLoanOfficerButton.clicked.connect(self.on_select_loan_officer_button_clicked)
        
        # 2. Calculate Loan Schedule
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)

        # 3. Guarantor Management
        self.selected_guarantors = []
        self.addGuarantorButton.clicked.connect(self.on_add_guarantor_button_clicked)
        self.deleteGuarantorButton.clicked.connect(self.on_delete_guarantor_button_clicked)
        self.guarantorTable.clicked.connect(self.on_guarantor_table_clicked)

        # 4. Collateral Management
        self.collateralNewButton.clicked.connect(self.on_collateral_new_clicked)
        self.collateralSaveButton.clicked.connect(self.on_collateral_save_clicked)
        self.collateralEditButton.clicked.connect(self.on_collateral_edit_clicked)
        self.collateralDeleteButton.clicked.connect(self.on_collateral_delete_clicked)
        self.collateralTable.clicked.connect(self.on_collateral_table_clicked)

        # 5. Counseling Management
        self.counselingNewButton.clicked.connect(self.on_counseling_new_clicked)
        self.counselingSaveButton.clicked.connect(self.on_counseling_save_clicked)
        self.counselingEditButton.clicked.connect(self.on_counseling_edit_clicked)
        self.counselingDeleteButton.clicked.connect(self.on_counseling_delete_clicked)
        self.counselingTable.clicked.connect(self.on_counseling_table_clicked)

    ### ---------------------------------- 1. Search and Select Customer + Select Loan Officer ---------------------------------- ###
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
                self.set_input_enabled(False, False, False, False)
                self.customer_uid = None

                self.open_select_customer_window()
        else:
            self.open_select_customer_window()

    def open_select_customer_window(self):
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    @pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        # print(f"Customer selected: {customer_data}")
        self.customer_uid = customer_data.get('uid', '')  # 고객 UID 저장

        self.customerName.setText(customer_data.get('name', ''))

        gender = customer_data.get('gender', '')
        self.checkBoxMale.setChecked(gender == 'Male')
        self.checkBoxFemale.setChecked(gender == 'Female')

        birth_timestamp = customer_data.get('birth', 0)
        if isinstance(birth_timestamp, (int, float)):
            birth_date = datetime.fromtimestamp(birth_timestamp).strftime('%Y-%m-%d')
            self.customerDateOfBirth.setText(birth_date)
        else:
            self.customerDateOfBirth.setText('')

        self.customerContact.setText(customer_data.get('Phone No.', ''))
        
        self.contractDate.setDate(QDate.currentDate())
        self.contractDate.setReadOnly(False)

        loan_type = customer_data.get('loan_type', '')
        if loan_type == 'Special Loan':
            self.loanType.setCurrentText('Special Loan')
        elif loan_type == 'Group Loan':
            self.loanType.setCurrentText('Group Loan')
        self.loanType.setEnabled(False)

        self.check_existing_customer_loan()

    def check_existing_customer_loan(self):
        if not self.customer_uid:
            QMessageBox.warning(self, "Warning", "Customer UID is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("uid", "==", self.customer_uid).get()

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
        self.set_input_enabled(True, False, False, False)

    def generate_loan_number(self):
        current_year_month = datetime.now().strftime("%Y%m")

        loans_ref = DB.collection("Loan")
        loans = loans_ref.order_by("loan_number", direction="DESCENDING").limit(1).stream()

        max_sequence_number = 0
        for loan in loans:
            loan_number = loan.to_dict().get("loan_number", "")
            if loan_number.startswith(current_year_month):
                sequence_number = int(loan_number[6:])
                max_sequence_number = max(max_sequence_number, sequence_number)

        new_sequence_number = max_sequence_number + 1
        new_loan_number = f"{current_year_month}{new_sequence_number:05d}"

        self.loanNumber.setText(new_loan_number)

    def on_select_loan_officer_button_clicked(self):
        dialog = SelectLoanOfficerWindow(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_officer = dialog.get_selected_officer()
            if selected_officer:
                self.loanOfficer.setText(f"{selected_officer['name']} - {selected_officer['service_area']}")

    ### ---------------------------------- 2. Calculate Loan Schedule ---------------------------------- ###
    def on_calculate_button_clicked(self):
        loan_number = self.loanNumber.text()
        if not loan_number:
            QMessageBox.warning(self, "Warning", "Loan number is missing.")
            return

        loans_ref = DB.collection("Loan")
        query = loans_ref.where("loan_number", "==", loan_number).get()

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
            if self.calculate_loan_schedule():
                self.save_loan_to_firestore()

                self.addGuarantorButton.setEnabled(True)
                self.collateralNewButton.setEnabled(True)
                self.counselingNewButton.setEnabled(True)

    def calculate_loan_schedule(self) -> bool:
        if not self.customerName.text():
            QMessageBox.warning(self, "Warning", "Please select a customer before calculating.")
            return False

        if not all([
            self.loanOfficer.text(),
            self.loanAmount.text(),
            self.repaymentCycle.text(),
            self.interestRate.text(),
            self.numberOfRepayment.text(),
            self.repaymentMethod.currentText()
        ]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return False

        try:
            start_date = self.contractDate.date().toPyDate()
            principal = int(self.loanAmount.text())
            repayment_cycle_days = int(self.repaymentCycle.text())
            annual_interest_rate = float(self.interestRate.text()) / 100
            number_of_repayment = int(self.numberOfRepayment.text())
            repayment_method = self.repaymentMethod.currentText().lower()

            calculator = LoanCalculator(
                start_date=start_date,
                principal=principal,
                num_payments=number_of_repayment,
                cycle_days=repayment_cycle_days,
                annual_interest_rate=annual_interest_rate
            )

            if repayment_method == "equal":
                self.schedule_df = calculator.equal_payment()
            elif repayment_method == "equal principal":
                self.schedule_df = calculator.equal_principal_payment()
            elif repayment_method == "bullet":
                self.schedule_df = calculator.bullet_payment()
            else:
                QMessageBox.critical(self, "Error", "Invalid loan type selected.")
                return False

            self.display_schedule(self.schedule_df)
            self.loanNewButton.setEnabled(True)
            return True

        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
            return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return False
    
    def display_schedule(self, df: pd.DataFrame):
        df = df.copy()

        if 'Remaining Balance' in df.columns:
            df = df.drop(columns=['Remaining Balance'])

        if 'Total' in df['Payment Date'].values:
            df = df[df['Payment Date'] != 'Total']

        # 'Payment Date'에 요일 추가
        df['Payment Date'] = pd.to_datetime(df['Payment Date']).dt.strftime('%Y-%m-%d (%A)')

        vertical_header = [str(i) for i in df['Period'].values]
        df_loan_table = df.drop(columns=['Period'])
        df = df.drop(columns=['Period'])

        def format_number(value):
            try:
                return "{:,}".format(int(value))
            except ValueError:
                return value

        # 각 컬럼의 합계 계산
        total_principal = df['Principal'].sum()
        total_interest = df['Interest'].sum()
        total_remaining_balance = df['Total'].sum()

        # QLabel에 합계 출력
        self.totalPrincipal.setText(f"{format_number(total_principal)}")
        self.totalInterest.setText(f"{format_number(total_interest)}")
        self.totalRemainingBalance.setText(f"{format_number(total_remaining_balance)}")

        # DataFrame의 각 열에 대해 숫자를 포맷팅
        for column in df_loan_table.columns:
            df_loan_table[column] = df_loan_table[column].apply(format_number)

        for column in df.columns:
            df[column] = df[column].apply(format_number)

        model_loan_table = QStandardItemModel(df_loan_table.shape[0], df_loan_table.shape[1])
        model_loan_table.setHorizontalHeaderLabels(df_loan_table.columns.tolist())
        model_loan_table.setVerticalHeaderLabels(vertical_header)

        for row in range(df_loan_table.shape[0]):
            for col in range(df_loan_table.shape[1]):
                item = QStandardItem(df_loan_table.iat[row, col])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model_loan_table.setItem(row, col, item)

        self.loanScheduleTable.setModel(model_loan_table)
        self.loanScheduleTable.resizeColumnsToContents()

        self.update_other_tabs()

    def save_loan_to_firestore(self):
        loan_info = {
            "uid": self.customer_uid,
            "loan_number": self.loanNumber.text(),
            "contract_date": self.contractDate.date().toString("yyyy-MM-dd"),
            "loan_status": self.loanStatus.currentText(),
            "loan_type": self.loanType.currentText(),
            "loan_officer": self.loanOfficer.text(),
            "principal": self.loanAmount.text(),
            "repayment_cycle": self.repaymentCycle.text(),
            "interest_rate": self.interestRate.text(),
            "number_of_repayment": self.numberOfRepayment.text(),
            "repayment_method": self.repaymentMethod.currentText(),
            "guarantors": [],
            "collaterals": [],
            "counselings": [],
        }

        if hasattr(self, 'schedule_df'):
            loan_schedule = self.schedule_df.to_dict(orient="records")
            for schedule_item in loan_schedule:
                schedule_item['status'] = 0
            loan_info["loan_schedule"] = loan_schedule

        try:
            if self.existing_loan_id:
                loan_ref = DB.collection("Loan").document(self.existing_loan_id)
                loan_doc = loan_ref.get()
                existing_data = loan_doc.to_dict()

                if existing_data:
                    # Retain existing collateral and counseling data
                    if "collaterals" in existing_data:
                        loan_info["collaterals"] = existing_data["collaterals"]
                    if "counselings" in existing_data:
                        loan_info["counselings"] = existing_data["counselings"]
                    if "guarantors" in existing_data:
                        loan_info["guarantors"] = existing_data["guarantors"]

                loan_ref.update(loan_info)
            else:
                doc_ref = DB.collection("Loan").add(loan_info)
                self.existing_loan_id = doc_ref[1].id

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the loan: {e}")

    def update_other_tabs(self):
        self.guarantorLoanNumber.setText(self.loanNumber.text())
        self.collateralLoanNumber.setText(self.loanNumber.text())
        self.counselingLoanNumber.setText(self.loanNumber.text())

        contract_date_str = self.contractDate.date().toString("yyyy-MM-dd")
        self.guarantorContractDate.setText(contract_date_str)
        self.collateralContractDate.setText(contract_date_str)
        self.counselingContractDate.setText(contract_date_str)

        self.guarantorLoanStatus.setText(self.loanStatus.currentText())
        self.collateralLoanStatus.setText(self.loanStatus.currentText())
        self.counselingLoanStatus.setText(self.loanStatus.currentText())

        self.guarantorLoanType.setText(self.loanType.currentText())
        self.collateralLoanType.setText(self.loanType.currentText())
        self.counselingLoanType.setText(self.loanType.currentText())

        self.guarantorLoanOfficer.setText(self.loanOfficer.text())
        self.collateralLoanOfficer.setText(self.loanOfficer.text())
        self.counselingLoanOfficer.setText(self.loanOfficer.text())

        self.guarantorLoanAmount.setText(self.loanAmount.text())
        self.collateralLoanAmount.setText(self.loanAmount.text())
        self.counselingLoanAmount.setText(self.loanAmount.text())

        self.guarantorRepaymentCycle.setText(self.repaymentCycle.text())
        self.collateralRepaymentCycle.setText(self.repaymentCycle.text())
        self.counselingRepaymentCycle.setText(self.repaymentCycle.text())

        self.guarantorInterestRate.setText(self.interestRate.text())
        self.collateralInterestRate.setText(self.interestRate.text())
        self.counselingInterestRate.setText(self.interestRate.text())

        self.guarantorNumberOfRepayment.setText(self.numberOfRepayment.text())
        self.collateralNumberOfRepayment.setText(self.numberOfRepayment.text())
        self.counselingNumberOfRepayment.setText(self.numberOfRepayment.text())

        self.guarantorRepaymentMethod.setText(self.repaymentMethod.currentText())
        self.collateralRepaymentMethod.setText(self.repaymentMethod.currentText())
        self.counselingRepaymentMethod.setText(self.repaymentMethod.currentText())

    ### ---------------------------------- 3. Guarantor Management ---------------------------------- ###
    def on_add_guarantor_button_clicked(self):
        # Guarantor 컬렉션에서 데이터가 있는지 확인
        guarantors_ref = DB.collection('Guarantor').get()

        if not guarantors_ref:
            # Guarantor 데이터가 없는 경우 경고 메시지 띄우기
            QMessageBox.warning(self, "No Guarantors", "Please register a guarantor first.")
            return

        # Guarantor 데이터가 있는 경우 선택 창 열기
        dialog = SelectGuarantorWindow()
        dialog.guarantors_selected.connect(self.handle_guarantors_selected)
        dialog.exec_()

    def handle_guarantors_selected(self, selected_guarantors):
        if selected_guarantors:
            # 선택한 Guarantor UID를 Loan 문서에 추가
            for guarantor_uid in selected_guarantors:
                if guarantor_uid not in self.selected_guarantors:
                    self.selected_guarantors.append(guarantor_uid)

            # Firestore의 Loan 컬렉션에 Guarantor 목록 업데이트
            if self.existing_loan_id:
                loan_ref = DB.collection('Loan').document(self.existing_loan_id)
                loan_ref.update({'guarantors': self.selected_guarantors})

            # 테이블을 다시 로드
            self.load_guarantor_data()

    def on_guarantor_table_clicked(self, index):
        if index.isValid():
            selected_row = index.row()

            if self.guarantorTable.selectionModel().isRowSelected(selected_row, QModelIndex()):
                
                self.guarantorTable.selectionModel().select(
                    self.guarantorTable.model().index(selected_row, 0), 
                    QItemSelectionModel.Deselect | QItemSelectionModel.Rows
                )

                self.deleteGuarantorButton.setEnabled(False)
                self.addGuarantorButton.setEnabled(True)
            else:
                self.guarantorTable.selectionModel().select(
                    self.guarantorTable.model().index(selected_row, 0), 
                    QItemSelectionModel.Select | QItemSelectionModel.Rows
                )
                
                self.deleteGuarantorButton.setEnabled(True)
                
    def on_delete_guarantor_button_clicked(self):
        indexes = self.guarantorTable.selectionModel().selectedRows()
        if indexes:
            
            for index in sorted(indexes, reverse=True):
                row = index.row()

                sorted_guarantors = sorted(self.selected_guarantors)

                if 0 <= row < len(sorted_guarantors):
                    guarantor_uid = sorted_guarantors[row]

                    try:
                        loan_ref = DB.collection('Loan').document(self.existing_loan_id)
                        self.selected_guarantors.remove(guarantor_uid)
                        loan_ref.update({'guarantors': self.selected_guarantors})
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to delete guarantor: {str(e)}")

            self.load_guarantor_data()

    def load_guarantor_data(self):
        if self.selected_guarantors:
            sorted_guarantors = sorted(self.selected_guarantors)

            guarantors_ref = DB.collection('Guarantor').where('uid', 'in', sorted_guarantors).get()
            data = [doc.to_dict() for doc in guarantors_ref]

            model = QStandardItemModel(len(data), 3)
            model.setHorizontalHeaderLabels(['Name', 'NRC No.', 'Phone No.'])

            for row, guarantor in enumerate(data):
                item_name = QStandardItem(guarantor.get('name', ''))
                item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                item_nrc_no = QStandardItem(guarantor.get('nrc_no', ''))
                item_nrc_no.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                item_phone_no = QStandardItem('-'.join([guarantor.get('tel1ByOne', ''), guarantor.get('tel1ByTwo', ''), guarantor.get('tel1ByThree', '')]))
                item_phone_no.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                model.setItem(row, 0, item_name)
                model.setItem(row, 1, item_nrc_no)
                model.setItem(row, 2, item_phone_no)

            self.guarantorTable.setModel(model)

            self.deleteGuarantorButton.setEnabled(False)
            self.addGuarantorButton.setEnabled(True)

    ### ---------------------------------- 4. Collateral Management ---------------------------------- ###
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

    ### ---------------------------------- 5. Counseling Management ---------------------------------- ###
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

    ### ---------------------------------- Input and Field Management ---------------------------------- ###
    def clear_table(self, table):
        model = QStandardItemModel(0, 0)
        table.setModel(model)

    def clear_all_fields(self):
        self.customerName.clear()
        self.checkBoxMale.setChecked(False)
        self.checkBoxFemale.setChecked(False)
        self.customerDateOfBirth.clear()
        self.customerContact.clear()

        self.loanNumber.clear()
        self.contractDate.setDate(QDate.currentDate())
        self.loanType.setCurrentText("Special Loan")
        self.loanOfficer.clear()
        self.loanAmount.clear()
        self.repaymentCycle.clear()
        self.interestRate.setText("28")
        self.numberOfRepayment.clear()
        self.repaymentMethod.setCurrentText("Equal")
        self.clear_table(self.loanScheduleTable)

        self.guarantorLoanNumber.clear()
        self.guarantorContractDate.clear()
        self.guarantorLoanStatus.clear()
        self.guarantorLoanType.clear()
        self.guarantorLoanOfficer.clear()
        self.guarantorLoanAmount.clear()
        self.guarantorRepaymentCycle.clear()
        self.guarantorInterestRate.clear()
        self.guarantorNumberOfRepayment.clear()
        self.guarantorRepaymentMethod.clear()
        self.clear_table(self.guarantorTable)

        self.collateralLoanNumber.clear()
        self.collateralContractDate.clear()
        self.collateralLoanStatus.clear()
        self.collateralLoanType.clear()
        self.collateralLoanOfficer.clear()
        self.collateralLoanAmount.clear()
        self.collateralRepaymentCycle.clear()
        self.collateralInterestRate.clear()
        self.collateralNumberOfRepayment.clear()
        self.collateralRepaymentMethod.clear()
        self.clear_table(self.collateralTable)
        self.collateralType.setCurrentText("[Select]")
        self.collateralName.clear()
        self.collateralDetails.clear()

        self.counselingLoanNumber.clear()
        self.counselingContractDate.clear()
        self.counselingLoanStatus.clear()
        self.counselingLoanType.clear()
        self.counselingLoanOfficer.clear()
        self.counselingLoanAmount.clear()
        self.counselingRepaymentCycle.clear()
        self.counselingInterestRate.clear()
        self.counselingNumberOfRepayment.clear()
        self.counselingRepaymentMethod.clear()
        self.clear_table(self.counselingTable)
        self.counselingDate.setDate(QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

    def set_input_enabled(self, loan: bool, guarantor: bool, collateral: bool, counseling: bool):
        # Calculate Loan tab input
        self.contractDate.setEnabled(loan)
        self.loanOfficer.setEnabled(loan)
        self.searchLoanOfficerButton.setEnabled(loan)
        self.loanAmount.setEnabled(loan)
        self.repaymentCycle.setEnabled(loan)
        self.interestRate.setEnabled(loan)
        self.numberOfRepayment.setEnabled(loan)
        self.repaymentMethod.setEnabled(loan)
        self.calculateButton.setEnabled(loan)

        # Guarantor Management tab input
        self.addGuarantorButton.setEnabled(guarantor)
        self.deleteGuarantorButton.setEnabled(guarantor)

        # Collateral Management tab input
        self.collateralNewButton.setEnabled(collateral)
        self.collateralSaveButton.setEnabled(collateral)
        self.collateralEditButton.setEnabled(collateral)
        self.collateralDeleteButton.setEnabled(collateral)
        self.collateralType.setEnabled(collateral)
        self.collateralName.setEnabled(collateral)
        self.collateralDetails.setEnabled(collateral)

        # Counseling Info tab input
        self.counselingNewButton.setEnabled(counseling)
        self.counselingSaveButton.setEnabled(counseling)
        self.counselingEditButton.setEnabled(counseling)
        self.counselingDeleteButton.setEnabled(counseling)
        self.counselingDate.setEnabled(counseling)
        self.counselingSubject.setEnabled(counseling)
        self.counselingDetails.setEnabled(counseling)
        self.counselingCorrectiveMeasure.setEnabled(counseling)

    def clear_table(self, table):
        model = QStandardItemModel(0, 0)
        table.setModel(model)

def main():
    app = QApplication(sys.argv)
    window = RegistrationLoanApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
