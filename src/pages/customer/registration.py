import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic, QtCore
from components import DB
from pages.loan.select_customer import SelectCustomerWindow  # SelectCustomerWindow를 임포트

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

        # Connect counselingSaveButton and counselingDeleteButton
        self.counselingSaveButton.clicked.connect(self.upload_counsel_data)  # 상담 정보 저장 버튼 연결
        self.counselingDeleteButton.clicked.connect(self.delete_counsel_data)  # 상담 정보 삭제 버튼 연결

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

        self.disable_all_fields()  # 고객 데이터를 불러온 후 필드를 비활성화
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

    def upload_counsel_data(self):
        # 상담 정보 업로드
        customer_name = self.name.text()
        customer_dob = self.dateOfBirth.date().toString(QtCore.Qt.ISODate)
        counsel_info = self.counsel.toPlainText()  # 상담 정보 (텍스트 입력)
        counsel_date = self.counselDate.date().toString(QtCore.Qt.ISODate)  # 상담 날짜
        counsel_type = self.counselType.currentText()  # 상담 유형 (콤보박스)

        # 고객의 이름이 비어 있으면 경고 메시지 표시
        if not customer_name:
            QMessageBox.warning(self, "Missing Information", "Customer's name is required to upload counsel data.")
            return

        counsel_data = {
            "customer_name": customer_name,
            "customer_dob": customer_dob,
            "counsel_info": counsel_info,
            "counsel_date": counsel_date,
            "counsel_type": counsel_type
        }

        try:
            counsel_ref = DB.collection('Counsel_Info')
            counsel_ref.add(counsel_data)
            QMessageBox.information(self, "Success", "Counsel data uploaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload counsel data: {e}")

    def delete_counsel_data(self):
        # 상담 정보를 삭제하는 함수
        try:
            # 삭제할 상담 정보를 선택했는지 확인
            selected_row = self.counselingTable.currentIndex().row()
            if selected_row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a counseling record to delete.")
                return

            # Firestore에서 선택한 상담 정보 가져오기
            counseling_data = self.get_selected_counseling_data(selected_row)

            if counseling_data:
                # 삭제 확인 메시지 박스
                reply = QMessageBox.question(self, 'Confirm Delete', 
                                            "Are you sure you want to delete this counseling record?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # Firestore에서 상담 정보 삭제
                    DB.collection('Counsel_Info').document(counseling_data['uid']).delete()
                    QMessageBox.information(self, "Success", "Counseling data deleted successfully.")
                    # 테이블 갱신 또는 삭제된 행을 테이블에서 제거
                    self.load_counseling_data()
                else:
                    return
            else:
                QMessageBox.warning(self, "No Data", "Counseling data not found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete counseling data: {e}")

    def get_selected_counseling_data(self, row):
        # 상담 테이블에서 선택한 행의 데이터를 가져오는 함수
        try:
            counseling_data = self.counselingTable.model().index(row, 0).data()  # uid가 첫 번째 열에 있다고 가정
            doc = DB.collection('Counsel_Info').document(counseling_data).get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load counseling data: {e}")
            return None

def main():
    app = QApplication(sys.argv)
    window = RegistrationApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
