import sys, os, re, requests
from datetime import timedelta
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from src.components import DB, storageBucket

class RegistrationCustomerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "customer.ui")
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())
        

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.show()
        self.setup_connections()
        self.disable_all_fields()
        self.current_customer_id = None
        self.edit_mode = False
        self.initialize_buttons()

    def initialize_buttons(self):
        self.newButton.setEnabled(True)
        self.saveButton.setEnabled(False)
        self.cpNumber.setEnabled(False)

    def setup_connections(self):
        self.newButton.clicked.connect(self.on_new_button_clicked)
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.imageButton.clicked.connect(self.select_image)

        self.tel2ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel2ByThree.textChanged.connect(self.limit_phone_length)
        self.tel1ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel1ByThree.textChanged.connect(self.limit_phone_length)

        self.loanType.currentTextChanged.connect(self.toggle_cp_number)

    def toggle_cp_number(self):
        # "Group Loan"이 선택되면 cpNumber를 활성화
        if self.loanType.currentText() == "Group Loan":
            self.cpNumber.setEnabled(True)
        else:
            self.cpNumber.setEnabled(False)
            self.cpNumber.clear()  # 비활성화할 때 필드를 초기화

    def reset_current_customer_id(self):
        self.current_customer_id = None

    def on_new_button_clicked(self):
        self.clear_fields()
        self.reset_current_customer_id()
        self.enable_all_fields()
        self.edit_mode = False
        self.saveButton.setEnabled(True)
        self.imageButton.setEnabled(True)

    def not_input_number(self):
        name_text = self.name.text()
        if re.search(r'\d', name_text):
            QMessageBox.warning(self, "Invalid Input", "Name cannot contain numbers.")
            self.name.clear()

    def limit_phone_length(self):
        for field in [self.tel2ByTwo, self.tel2ByThree, self.tel1ByTwo, self.tel1ByThree]:
            text = field.text()
            if len(text) > 4:
                field.setText(text[:4])

    def clear_fields(self):
        self.name.clear()
        self.nrcNo.clear()
        self.dateOfBirth.setDate(QtCore.QDate(2000, 1, 1))
        self.gender.setCurrentIndex(0)
        self.tel2ByOne.setCurrentIndex(0)
        self.tel2ByTwo.clear()
        self.tel2ByThree.clear()
        self.tel1ByOne.setCurrentIndex(0)
        self.tel1ByTwo.clear()
        self.tel1ByThree.clear()
        self.email.clear()
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
        self.current_customer_id = None
        self.disable_all_fields()
        self.saveButton.setEnabled(False)
        self.imageLabel.clear()
        self.cpNumber.clear()

    def disable_all_fields(self):
        self.name.setEnabled(False)
        self.nrcNo.setEnabled(False)
        self.dateOfBirth.setEnabled(False)
        self.gender.setEnabled(False)
        self.tel2ByOne.setEnabled(False)
        self.tel2ByTwo.setEnabled(False)
        self.tel2ByThree.setEnabled(False)
        self.tel1ByOne.setEnabled(False)
        self.tel1ByTwo.setEnabled(False)
        self.tel1ByThree.setEnabled(False)
        self.email.setEnabled(False)
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
        self.saveButton.setEnabled(False)
        self.imageButton.setEnabled(False)
        self.loanType.setEnabled(False)
        self.cpNumber.setEnabled(False)

    def enable_all_fields(self):
        self.saveButton.setEnabled(True)
        self.name.setEnabled(True)
        self.nrcNo.setEnabled(True)
        self.dateOfBirth.setEnabled(True)
        self.gender.setEnabled(True)
        self.tel2ByOne.setEnabled(True)
        self.tel2ByTwo.setEnabled(True)
        self.tel2ByThree.setEnabled(True)
        self.tel1ByOne.setEnabled(True)
        self.tel1ByTwo.setEnabled(True)
        self.tel1ByThree.setEnabled(True)
        self.email.setEnabled(True)
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
        # self.cpNumber.setEnabled(True)
        self.loanType.setEnabled(True)

    def prepare_save_customer_data(self):
        customer_data = self.get_customer_data()

        # 필수 필드 목록
        required_fields = [
            "name", "nrc_no", "date_of_birth", "gender"
        ]

        # Loan Type이 "Group Loan"일 때 cp_number를 필수 항목에 추가
        if self.loanType.currentText() == "Group Loan":
            required_fields.append("cp_number")

        # 필수 필드 중 하나라도 비어있는지 확인
        missing_fields = []

        # tel1 관련 필드 검사
        if not all([self.tel1ByOne.currentText(), self.tel1ByTwo.text(), self.tel1ByThree.text()]):
            missing_fields.append("Tel1")

        # 필수 필드 검사 (QComboBox와 QLineEdit을 구분)
        if not self.name.text():
            missing_fields.append("이름")
        if not self.nrcNo.text():
            missing_fields.append("NRC No.")
        if not self.dateOfBirth.date().isValid():
            missing_fields.append("생년월일")
        if not self.gender.currentText():
            missing_fields.append("성별")

        # 만약 필수 필드가 비어있다면 경고 메시지 출력
        if missing_fields:
            QMessageBox.warning(self, "Missing Fields",
                                f"{', '.join(missing_fields)}is not fill.")
            return

        reply = QMessageBox.question(self, 'Confirm Data',
                                     "Would you like to proceed?",
                                     QMessageBox.Ok | QMessageBox.Cancel,
                                     QMessageBox.Ok)

        if reply == QMessageBox.Ok:
            self.save_customer_data()

    def get_customer_data(self):
        customer_data = {
            "name": self.name.text(),
            "nrc_no": self.nrcNo.text(),
            "date_of_birth": self.dateOfBirth.date().toString(QtCore.Qt.ISODate),
            "gender": self.gender.currentText(),
            "tel1ByOne": self.tel1ByOne.currentText(),
            "tel1ByTwo": self.tel1ByTwo.text(),
            "tel1ByThree": self.tel1ByThree.text(),
            "tel2ByOne": self.tel2ByOne.currentText(),
            "tel2ByTwo": self.tel2ByTwo.text(),
            "tel2ByThree": self.tel2ByThree.text(),
            "email": self.email.text(),
            "loan_type": self.loanType.currentText(),
            "cp_number": self.cpNumber.text(),
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

        # Only add cpNumber if loanType is "Group Loan"
        if self.loanType.currentText() == "Group Loan":
            customer_data["cp_number"] = self.cpNumber.text()

        return customer_data

    def save_customer_data(self):
        customer_data = self.get_customer_data()

        try:
            if self.edit_mode and self.current_customer_id:
                customer_uid = self.current_customer_id
            else:
                new_customer_ref = DB.collection('Customer').add(customer_data)
                customer_uid = new_customer_ref[1].id
                customer_data["uid"] = customer_uid
                DB.collection('Customer').document(customer_uid).update({"uid": customer_uid})

            if hasattr(self, 'selected_image_path') and os.path.exists(self.selected_image_path):
                image_blob = storageBucket.blob(f'customer_images/{customer_uid}.jpg')

                image_blob.upload_from_filename(self.selected_image_path)

                image_url = image_blob.generate_signed_url(expiration=timedelta(days=365))

                customer_data["image_url"] = image_url
                DB.collection('Customer').document(customer_uid).update({"image_url": image_url})

            DB.collection('Customer').document(customer_uid).update(customer_data)

            QMessageBox.information(self, "Success", "Customer data saved successfully.")
            self.clear_fields()

            self.newButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.edit_mode = False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer data: {e}")

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_name:
            pixmap = QPixmap(file_name)

            if not pixmap.isNull():
                self.imageLabel.setPixmap(
                    pixmap.scaled(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                )

                self.selected_image_path = file_name
            else:
                QMessageBox.warning(self, "Error", "Failed to load image.")

def main():
    app = QApplication(sys.argv)
    window = RegistrationCustomerApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()