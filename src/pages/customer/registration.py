import sys
import os
import re
import base64
from io import BytesIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QLabel
from PyQt5 import uic, QtCore
from components import DB
from pages.loan.select_customer import SelectCustomerWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap
class RegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)
        self.show()
        self.setup_connections()
        self.disable_all_fields()
        self.current_customer_id = None
        self.edit_mode = False  # edit 모드인지 new 모드인지 구분하는 변수
        self.initialize_buttons()  # 버튼 상태를 초기화
        self.setup_counseling_table()  # 상담 테이블 설정
        self.edit_mode = False  # 상담 데이터 수정 모드 플래그
        self.selected_counseling_row = None  # 선택된 상담 데이터의 인덱스

    def setup_counseling_table(self):
        # 테이블에 대한 QStandardItemModel을 설정
        model = QStandardItemModel(0, 4)  # 0개의 행과 4개의 열로 모델 생성
        model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])
        self.counselingTable.setModel(model)  # 모델을 QTableView에 설정
        self.counselingTable.setSelectionBehavior(self.counselingTable.SelectRows)

    def initialize_buttons(self):
        # 창이 처음 떴을 때, searchButton과 newButton만 활성화
        self.searchButton.setEnabled(True)
        self.newButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def setup_connections(self):
        self.newButton.clicked.connect(self.on_new_button_clicked)
        self.searchButton.clicked.connect(self.open_select_customer_window)  # SelectCustomerWindow 열기
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.editButton.clicked.connect(self.edit_customer_data)
        self.imageButton.clicked.connect(self.select_image)

        # Connect counselingSaveButton and counselingDeleteButton
        self.counselingNewButton.clicked.connect(self.on_counseling_new_clicked)
        self.counselingEditButton.clicked.connect(self.on_counseling_edit_clicked)
        self.counselingSaveButton.clicked.connect(self.save_counsel_data)
        self.counselingDeleteButton.clicked.connect(self.delete_counsel_data)
        self.counselingTable.clicked.connect(self.on_counseling_table_clicked)

        # Connect phone fields to the validation method
        self.phone2.textChanged.connect(self.limit_phone_length)
        self.phone3.textChanged.connect(self.limit_phone_length)
        self.tel2.textChanged.connect(self.limit_phone_length)
        self.tel3.textChanged.connect(self.limit_phone_length)

    def reset_current_customer_id(self):
        # 새로운 고객을 등록할 때 기존의 customer_id를 리셋
        self.current_customer_id = None

    def on_new_button_clicked(self):
        # 새로운 고객 등록 시 모든 필드를 비우고 초기화
        self.clear_fields()
        self.reset_current_customer_id()
        self.enable_all_fields()
        self.edit_mode = False  # New 모드로 전환
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.imageButton.setEnabled(True)

    def open_select_customer_window(self):
        # SelectCustomerWindow를 열고 고객 선택을 처리
        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    @QtCore.pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        # 고객이 선택되면 해당 고객의 정보를 등록 폼에 채움
        print(f"Customer selected: {customer_data}")
        self.current_customer_id = customer_data.get('uid', '')  # Customer ID 저장
        self.populate_fields_with_customer_data(customer_data)
        
        # searchName 및 searchDateOfBirth에 고객 데이터 넣기
        self.searchName.setText(customer_data.get("name", ""))
        
        # date_of_birth를 QLabel에 텍스트로 표시
        date_of_birth = customer_data.get("date_of_birth", "")
        self.searchDateOfBirth.setText(date_of_birth)

        # 상담 데이터를 테이블에 로드
        self.load_counseling_data()

        self.disable_all_fields()  # 고객 데이터를 불러온 후 필드를 비활성화
        self.disable_counseling_fields()  # 상담 필드를 비활성화
        self.editButton.setEnabled(True)  # 편집 버튼 활성화

    def populate_fields_with_customer_data(self, customer_data):
        # 고객 데이터를 필드에 채움
        self.name.setText(customer_data.get("name", ""))
        self.nrcNo.setText(customer_data.get("nrc_no", ""))
        self.dateOfBirth.setDate(QtCore.QDate.fromString(customer_data.get("date_of_birth"), QtCore.Qt.ISODate))
        self.gender.setCurrentText(customer_data.get("gender", ""))
        self.married.setCurrentText(customer_data.get("marital_status", ""))
        self.phone1.setCurrentText(customer_data.get("mobile1", ""))
        self.phone2.setText(customer_data.get("mobile2", ""))
        self.phone3.setText(customer_data.get("mobile3", ""))
        self.tel1.setCurrentText(customer_data.get("phone1", ""))
        self.tel2.setText(customer_data.get("phone2", ""))
        self.tel3.setText(customer_data.get("phone3", ""))
        self.email.setText(customer_data.get("email", ""))
        self.loanOfficer.setText(customer_data.get("loan_officer", ""))

        home_address = customer_data.get("home_address", {})
        self.homePostalCode.setText(home_address.get("postal_code", ""))
        self.homeStreet.setText(home_address.get("street", ""))
        self.homeCountry.setText(home_address.get("country", ""))
        self.homeCity.setText(home_address.get("city", ""))
        self.homeTownship.setText(home_address.get("township", ""))

        office_address = customer_data.get("office_address", {})
        self.officePostalCode.setText(office_address.get("postal_code", ""))
        self.officeStreet.setText(office_address.get("street", ""))
        self.officeCountry.setText(office_address.get("country", ""))
        self.officeCity.setText(office_address.get("city", ""))
        self.officeTownship.setText(office_address.get("township", ""))

        additional_info = customer_data.get("additional_info", {})
        self.info1.setText(additional_info.get("info1", ""))
        self.info2.setText(additional_info.get("info2", ""))
        self.info3.setText(additional_info.get("info3", ""))
        self.info4.setText(additional_info.get("info4", ""))
        self.info5.setText(additional_info.get("info5", ""))

    def load_counseling_data(self):
        try:
            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                counseling_data = customer_data.get("counseling", [])

                # QStandardItemModel을 사용하여 테이블 모델 설정
                model = QStandardItemModel(len(counseling_data), 4)
                model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])

                for row_idx, counsel in enumerate(counseling_data):
                    model.setItem(row_idx, 0, QStandardItem(counsel.get("counsel_date", "")))
                    model.setItem(row_idx, 1, QStandardItem(counsel.get("counsel_subject", "")))
                    model.setItem(row_idx, 2, QStandardItem(counsel.get("counsel_details", "")))
                    model.setItem(row_idx, 3, QStandardItem(counsel.get("corrective_measure", "")))

                # 모델을 테이블 뷰에 설정
                self.counselingTable.setModel(model)
                self.counselingTable.resizeColumnsToContents()

            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load counseling data: {e}")

    def on_counseling_new_clicked(self):
        # 새로운 상담 데이터 추가를 위한 필드 초기화 및 활성화
        self.counselingDate.setDate(QtCore.QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()
        
        # 필드 활성화
        self.enable_counseling_fields()
        
        # 상담 데이터 추가 모드
        self.edit_mode = False
        self.selected_counseling_row = None

    def on_counseling_edit_clicked(self):
        # 선택된 상담 데이터를 편집할 수 있도록 필드에 데이터를 로드하고 활성화
        selected_indexes = self.counselingTable.selectionModel().selectedRows()
        
        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a counseling record to edit.")
            return
        
        self.selected_counseling_row = selected_indexes[0].row()

        # 선택된 행의 데이터를 counseling 필드로 로드
        model = self.counselingTable.model()
        counsel_date = model.index(self.selected_counseling_row, 0).data(QtCore.Qt.DisplayRole)
        counsel_subject = model.index(self.selected_counseling_row, 1).data(QtCore.Qt.DisplayRole)
        counsel_details = model.index(self.selected_counseling_row, 2).data(QtCore.Qt.DisplayRole)
        corrective_measure = model.index(self.selected_counseling_row, 3).data(QtCore.Qt.DisplayRole)

        if counsel_date and counsel_subject:
            # 상담 데이터를 입력란에 표시
            self.counselingDate.setDate(QtCore.QDate.fromString(counsel_date, "yyyy-MM-dd"))
            self.counselingSubject.setText(counsel_subject)
            self.counselingDetails.setPlainText(counsel_details)
            self.counselingCorrectiveMeasure.setText(corrective_measure)

            # 필드 활성화
            self.enable_counseling_fields()

            # 수정 모드 활성화
            self.edit_mode = True
        else:
            QMessageBox.warning(self, "Error", "Failed to load counseling data. Please try again.")

    def delete_counsel_data(self):
        # 상담 정보를 삭제하는 함수
        try:
            # 선택된 행의 인덱스 가져오기
            selected_indexes = self.counselingTable.selectionModel().selectedRows()

            if not selected_indexes:
                QMessageBox.warning(self, "No Selection", "Please select a counseling record to delete.")
                return

            # 첫 번째 선택된 인덱스에서 행 번호 가져오기
            selected_row = selected_indexes[0].row()

            # Firestore에서 고객 문서 가져오기
            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                counseling_data = customer_data.get("counseling", [])

                # 선택된 행에 해당하는 상담 데이터 삭제
                if 0 <= selected_row < len(counseling_data):
                    del counseling_data[selected_row]

                    # Firestore에 업데이트
                    customer_ref.update({"counseling": counseling_data})

                    QMessageBox.information(self, "Success", "Counseling data deleted successfully.")
                    
                    # 상담 필드 초기화
                    self.counselingDate.setDate(QtCore.QDate(2000, 1, 1))
                    self.counselingSubject.clear()
                    self.counselingDetails.clear()
                    self.counselingCorrectiveMeasure.clear()
                    
                    # 테이블을 다시 로드
                    self.load_counseling_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete counseling data.")
            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete counseling data: {e}")

    def save_counsel_data(self):
        # 상담 정보 준비
        counsel_info = {
            "counsel_subject": self.counselingSubject.text(),
            "counsel_details": self.counselingDetails.toPlainText(),
            "counsel_date": self.counselingDate.date().toString(QtCore.Qt.ISODate),
            "corrective_measure": self.counselingCorrectiveMeasure.text()
        }

        # 고객이 선택되지 않았으면 경고 메시지
        if not self.current_customer_id:
            QMessageBox.warning(self, "No Customer", "Please select a customer before saving counseling data.")
            return

        try:
            # Firestore에서 고객 문서 가져오기
            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            # 고객 데이터가 존재하면 counseling 배열 처리
            if customer_doc.exists:
                customer_data = customer_doc.to_dict()

                if "counseling" not in customer_data:
                    customer_data["counseling"] = []

                if self.edit_mode and self.selected_counseling_row is not None:
                    # 기존 상담 데이터 수정
                    customer_data["counseling"][self.selected_counseling_row] = counsel_info
                else:
                    # 새로운 상담 데이터 추가
                    customer_data["counseling"].append(counsel_info)

                # Firestore에 업데이트
                customer_ref.update({"counseling": customer_data["counseling"]})

                QMessageBox.information(self, "Success", "Counseling data saved successfully.")
                
                # 필드 초기화 및 테이블 업데이트
                self.counselingDate.setDate(QtCore.QDate(2000, 1, 1))
                self.counselingSubject.clear()
                self.counselingDetails.clear()
                self.counselingCorrectiveMeasure.clear()
                self.load_counseling_data()
                
                # 필드 비활성화
                self.disable_counseling_fields()

                # 모드 초기화
                self.edit_mode = False
                self.selected_counseling_row = None

            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save counseling data: {e}")

    def on_counseling_table_clicked(self, index):
        # 이 메서드를 추가하여 테이블에서 선택된 데이터를 관리
        if index.isValid():
            # 선택된 행의 데이터를 입력란에 표시
            row = index.row()
            model = self.counselingTable.model()

            counsel_date = model.index(row, 0).data()
            counsel_subject = model.index(row, 1).data()
            counsel_details = model.index(row, 2).data()
            corrective_measure = model.index(row, 3).data()

            # 선택된 데이터를 counseling 입력란에 채우기
            self.counselingDate.setDate(QtCore.QDate.fromString(counsel_date, "yyyy-MM-dd"))
            self.counselingSubject.setText(counsel_subject)
            self.counselingDetails.setPlainText(counsel_details)
            self.counselingCorrectiveMeasure.setText(corrective_measure)

            # 필드는 비활성화 상태로 유지
            self.disable_counseling_fields()

    def disable_counseling_fields(self):
        self.counselingDate.setEnabled(False)
        self.counselingSubject.setEnabled(False)
        self.counselingDetails.setEnabled(False)
        self.counselingCorrectiveMeasure.setEnabled(False)

    def enable_counseling_fields(self):
        self.counselingDate.setEnabled(True)
        self.counselingSubject.setEnabled(True)
        self.counselingDetails.setEnabled(True)
        self.counselingCorrectiveMeasure.setEnabled(True)

    def not_input_number(self):
        name_text = self.name.text()
        if re.search(r'\d', name_text):
            QMessageBox.warning(self, "Invalid Input", "Name cannot contain numbers.")
            self.name.clear()

    def limit_phone_length(self):
        for field in [self.phone2, self.phone3, self.tel2, self.tel3]:
            text = field.text()
            if len(text) > 4:
                field.setText(text[:4])

    def clear_fields(self):
        self.searchName.clear()
        self.searchDateOfBirth.clear()
        self.name.clear()
        self.nrcNo.clear()
        self.dateOfBirth.setDate(QtCore.QDate(2000, 1, 1))
        self.gender.setCurrentIndex(0)
        self.married.setCurrentIndex(0)
        self.phone1.setCurrentIndex(0)
        self.phone2.clear()
        self.phone3.clear()
        self.tel1.setCurrentIndex(0)
        self.tel2.clear()
        self.tel3.clear()
        self.email.clear()
        self.loanOfficer.clear()
        self.homePostalCode.clear()
        self.homeStreet.clear()
        self.homeCountry.clear()
        self.homeCity.clear()
        self.homeTownship.clear()
        self.officePostalCode.clear()
        self.officeCountry.clear()
        self.officeCity.clear()
        self.officeTownship.clear()
        self.officeStreet.clear()
        self.info1.clear()
        self.info2.clear()
        self.info3.clear()
        self.info4.clear()
        self.info5.clear()
        self.current_customer_id = None  # 불러온 고객의 ID를 초기화
        self.disable_all_fields()  # 새로운 고객 등록 시 모든 필드 비활성화
        self.editButton.setEnabled(False)  # 편집 버튼 비활성화
        self.saveButton.setEnabled(False)  # 저장 버튼 비활성화
        self.imageLabel.clear()

    def disable_all_fields(self):
        # Disable all input fields
        self.name.setEnabled(False)
        self.nrcNo.setEnabled(False)
        self.dateOfBirth.setEnabled(False)
        self.gender.setEnabled(False)
        self.married.setEnabled(False)
        self.phone1.setEnabled(False)
        self.phone2.setEnabled(False)
        self.phone3.setEnabled(False)
        self.tel1.setEnabled(False)
        self.tel2.setEnabled(False)
        self.tel3.setEnabled(False)
        self.email.setEnabled(False)
        self.loanOfficer.setEnabled(False)
        self.homePostalCode.setEnabled(False)
        self.homeStreet.setEnabled(False)
        self.homeCountry.setEnabled(False)
        self.homeCity.setEnabled(False)
        self.homeTownship.setEnabled(False)
        self.officePostalCode.setEnabled(False)
        self.officeCountry.setEnabled(False)
        self.officeCity.setEnabled(False)
        self.officeTownship.setEnabled(False)
        self.officeStreet.setEnabled(False)
        self.info1.setEnabled(False)
        self.info2.setEnabled(False)
        self.info3.setEnabled(False)
        self.info4.setEnabled(False)
        self.info5.setEnabled(False)
        self.saveButton.setEnabled(False)  # 저장 버튼도 비활성화
        self.imageButton.setEnabled(False)

    def enable_all_fields(self):
        self.saveButton.setEnabled(True)
        self.name.setEnabled(True)
        self.nrcNo.setEnabled(True)
        self.dateOfBirth.setEnabled(True)
        self.gender.setEnabled(True)
        self.married.setEnabled(True)
        self.phone1.setEnabled(True)
        self.phone2.setEnabled(True)
        self.phone3.setEnabled(True)
        self.tel1.setEnabled(True)
        self.tel2.setEnabled(True)
        self.tel3.setEnabled(True)
        self.email.setEnabled(True)
        self.loanOfficer.setEnabled(True)
        self.homePostalCode.setEnabled(True)
        self.homeStreet.setEnabled(True)
        self.homeCountry.setEnabled(True)
        self.homeCity.setEnabled(True)
        self.homeTownship.setEnabled(True)
        self.officePostalCode.setEnabled(True)
        self.officeCountry.setEnabled(True)
        self.officeCity.setEnabled(True)
        self.officeTownship.setEnabled(True)
        self.officeStreet.setEnabled(True)
        self.info1.setEnabled(True)
        self.info2.setEnabled(True)
        self.info3.setEnabled(True)
        self.info4.setEnabled(True)
        self.info5.setEnabled(True)
        self.imageButton.setEnabled(True)
    def prepare_save_customer_data(self):
        customer_data = self.get_customer_data()

        # Check for required fields
        missing_fields = [field for field, value in customer_data.items() if not value]
        if missing_fields:
            QMessageBox.warning(self, "Missing Fields",
                                "The following fields are required and cannot be empty: "
                                f"{', '.join(missing_fields)}")
            return

        # Create a formatted string for the message box
        data_summary = (
            f"Name: {customer_data['name']}\n"
            f"NRC No.: {customer_data['nrc_no']}\n"
            f"Date of Birth: {customer_data['date_of_birth']}\n"
            f"Gender: {customer_data['gender']}\n"
            f"Marital Status: {customer_data['marital_status']}\n"
            f"Mobile1: {customer_data['mobile1']}\n"
            f"Mobile2: {customer_data['mobile2']}\n"
            f"Mobile3: {customer_data['mobile3']}\n"
            f"Phone1: {customer_data['phone1']}\n"
            f"Phone2: {customer_data['phone2']}\n"
            f"Phone3: {customer_data['phone3']}\n"
            f"Email: {customer_data['email']}\n"
            f"Loan Officer: {customer_data['loan_officer']}\n"
            f"Home Address:\n"
            f"  Postal Code: {customer_data['home_address']['postal_code']}\n"
            f"  Street: {customer_data['home_address']['street']}\n"
            f"  Country: {customer_data['home_address']['country']}\n"
            f"  City: {customer_data['home_address']['city']}\n"
            f"  Township: {customer_data['home_address']['township']}\n"
            f"Office Address:\n"
            f"  Postal Code: {customer_data['office_address']['postal_code']}\n"
            f"  Street: {customer_data['office_address']['street']}\n"
            f"  Country: {customer_data['office_address']['country']}\n"
            f"  City: {customer_data['office_address']['city']}\n"
            f"  Township: {customer_data['office_address']['township']}\n"
            f"Additional Info:\n"
            f"  Info1: {customer_data['additional_info']['info1']}\n"
            f"  Info2: {customer_data['additional_info']['info2']}\n"
            f"  Info3: {customer_data['additional_info']['info3']}\n"
            f"  Info4: {customer_data['additional_info']['info4']}\n"
            f"  Info5: {customer_data['additional_info']['info5']}"
        )

        # Show confirmation message box
        reply = QMessageBox.question(self, 'Confirm Data',
                                     f"Would you like to proceed?\n\n{data_summary}",
                                     QMessageBox.Ok | QMessageBox.Cancel,
                                     QMessageBox.Cancel)

        if reply == QMessageBox.Ok:
            self.save_customer_data()

    def get_customer_data(self):
        return {
            "name": self.name.text(),
            "nrc_no": self.nrcNo.text(),
            "date_of_birth": self.dateOfBirth.date().toString(QtCore.Qt.ISODate),
            "gender": self.gender.currentText(),
            "marital_status": self.married.currentText(),
            "mobile1": self.phone1.currentText(),
            "mobile2": self.phone2.text(),
            "mobile3": self.phone3.text(),
            "phone1": self.tel1.currentText(),
            "phone2": self.tel2.text(),
            "phone3": self.tel3.text(),
            "email": self.email.text(),
            "loan_officer": self.loanOfficer.text(),
            "home_address": {
                "postal_code": self.homePostalCode.text(),
                "street": self.homeStreet.text(),
                "country": self.homeCountry.text(),
                "city": self.homeCity.text(),
                "township": self.homeTownship.text()
            },
            "office_address": {
                "postal_code": self.officePostalCode.text(),
                "country": self.officeCountry.text(),
                "city": self.officeCity.text(),
                "township": self.officeTownship.text(),
                "street": self.officeStreet.text()
            },
            "additional_info": {
                "info1": self.info1.text(),
                "info2": self.info2.text(),
                "info3": self.info3.text(),
                "info4": self.info4.text(),
                "info5": self.info5.text()
            }
        }

    def save_customer_data(self):
        customer_data = self.get_customer_data()

        try:
            # edit_mode가 활성화되어 있고, current_customer_id가 있으면 기존 문서를 업데이트
            if self.edit_mode and self.current_customer_id:
                # 기존 문서 업데이트
                customer_ref = DB.collection('Customer').document(self.current_customer_id)
                customer_data["uid"] = self.current_customer_id  # 기존 문서의 uid를 유지
                customer_ref.update(customer_data)  # update로 수정
                QMessageBox.information(self, "Success", "Customer data updated successfully.")
            else:
                # 새로운 문서 추가
                customer_ref = DB.collection('Customer')
                new_customer_ref = customer_ref.add(customer_data)
                new_customer_id = new_customer_ref[1].id  # 생성된 document의 ID 가져오기
                customer_data["uid"] = new_customer_id  # uid를 document ID로 설정
                DB.collection('Customer').document(new_customer_id).update({"uid": new_customer_id})
                QMessageBox.information(self, "Success", "New customer data saved successfully.")

            self.clear_fields()
            # 저장 후 searchButton과 newButton 활성화
            self.searchButton.setEnabled(True)
            self.newButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.edit_mode = False  # 저장 후 edit_mode 해제

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer data: {e}")

    def edit_customer_data(self):
        self.newButton.setEnabled(False)
        self.searchButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        QMessageBox.information(self, "Edit Customer", "You can now edit customer data.")
        self.enable_all_fields()
        self.edit_mode = True  # Edit 모드로 전환

    def select_image(self):
        # 파일 탐색기 열기
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                # QLabel에 이미지 설정
                self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

                # 이미지를 Base64로 인코딩하여 저장
                buffer = BytesIO()
                pixmap.save(buffer, "JPEG")  # JPEG 또는 PNG로 저장 가능
                self.image_base64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image.")
def main():
    app = QApplication(sys.argv)
    window = RegistrationApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
