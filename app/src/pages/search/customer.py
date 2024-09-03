import sys, os, re, requests
from datetime import timedelta
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidget, QVBoxLayout, QDialog, QPushButton
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from src.components import DB, storageBucket
from app.src.components.select_customer import SelectCustomerWindow

class SearchCustomerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "customer.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.show()
        self.setup_connections()
        self.disable_all_fields()
        self.current_customer_id = None
        self.edit_mode = False
        self.initialize_buttons()

    def initialize_buttons(self):
        self.searchButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def setup_connections(self):
        self.searchButton.clicked.connect(self.open_select_customer_window)
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.editButton.clicked.connect(self.edit_customer_data)
        self.imageButton.clicked.connect(self.select_image)
        self.selectLoanOfficerButton.clicked.connect(self.open_officer_select_dialog)

        self.phone2.textChanged.connect(self.limit_phone_length)
        self.phone3.textChanged.connect(self.limit_phone_length)
        self.tel2.textChanged.connect(self.limit_phone_length)
        self.tel3.textChanged.connect(self.limit_phone_length)

    def reset_current_customer_id(self):
        self.current_customer_id = None

    def open_officer_select_dialog(self):
        dialog = OfficerSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_officer = dialog.get_selected_officer()
            if selected_officer:
                self.loanOfficer.setText(f"{selected_officer['name']} - {selected_officer['service_area']}")

    def open_select_customer_window(self):
        self.setEnabled(False)

        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    @QtCore.pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        try:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.current_customer_id = customer_data.get('uid', '')
            self.populate_fields_with_customer_data(customer_data)

            self.searchName.setText(customer_data.get("name", ""))
            date_of_birth = customer_data.get("date_of_birth", "")
            self.searchDateOfBirth.setText(date_of_birth)

            self.disable_all_fields()
            self.editButton.setEnabled(True)

        finally:
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)

    def populate_fields_with_customer_data(self, customer_data):
        self.name.setText(customer_data.get("name", ""))
        self.nrcNo.setText(customer_data.get("nrc_no", ""))
        self.dateOfBirth.setDate(QtCore.QDate.fromString(customer_data.get("date_of_birth"), QtCore.Qt.ISODate))
        self.gender.setCurrentText(customer_data.get("gender", ""))
        self.phone1.setCurrentText(customer_data.get("mobile1", ""))
        self.phone2.setText(customer_data.get("mobile2", ""))
        self.phone3.setText(customer_data.get("mobile3", ""))
        self.tel1.setCurrentText(customer_data.get("phone1", ""))
        self.tel2.setText(customer_data.get("phone2", ""))
        self.tel3.setText(customer_data.get("phone3", ""))
        self.email.setText(customer_data.get("email", ""))
        loan_officer = customer_data.get("loan_officer", {})
        if isinstance(loan_officer, dict):
            loan_officer_display = f"{loan_officer.get('name', '')} - {loan_officer.get('service_area', '')}"
        else:
            loan_officer_display = loan_officer

        self.loanOfficer.setText(loan_officer_display)

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

        image_url = customer_data.get("image_url", "")
        if image_url:
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data.read())

                    self.imageLabel.setPixmap(
                        pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.imageLabel.clear()
            except Exception as e:
                print(self, "Error", f"Failed to load image: {e}")
                self.imageLabel.clear()
        else:
            self.imageLabel.clear()

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
        self.current_customer_id = None
        self.disable_all_fields()
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.imageLabel.clear()

    def disable_all_fields(self):
        self.name.setEnabled(False)
        self.nrcNo.setEnabled(False)
        self.dateOfBirth.setEnabled(False)
        self.gender.setEnabled(False)
        self.phone1.setEnabled(False)
        self.phone2.setEnabled(False)
        self.phone3.setEnabled(False)
        self.tel1.setEnabled(False)
        self.tel2.setEnabled(False)
        self.tel3.setEnabled(False)
        self.email.setEnabled(False)
        self.loanOfficer.setEnabled(False)
        self.selectLoanOfficerButton.setEnabled(False)
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

    def enable_all_fields(self):
        self.saveButton.setEnabled(True)
        self.name.setEnabled(True)
        self.nrcNo.setEnabled(True)
        self.dateOfBirth.setEnabled(True)
        self.gender.setEnabled(True)
        self.phone1.setEnabled(True)
        self.phone2.setEnabled(True)
        self.phone3.setEnabled(True)
        self.tel1.setEnabled(True)
        self.tel2.setEnabled(True)
        self.tel3.setEnabled(True)
        self.email.setEnabled(True)
        self.selectLoanOfficerButton.setEnabled(True)
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

        required_fields = [
            "name", "nrc_no", "date_of_birth", "gender", "mobile1", "mobile2", "mobile3",
            "phone1", "phone2", "phone3", "email", "home_address.postal_code",
            "home_address.street", "home_address.country", "home_address.city",
            "home_address.township"
        ]

        missing_fields = []
        for field in required_fields:
            # 딕셔너리 경로에 따라 값 가져오기
            field_parts = field.split('.')
            value = customer_data
            for part in field_parts:
                value = value.get(part)
                if value is None:
                    break

            if not value:
                missing_fields.append(field)

        if missing_fields:
            QMessageBox.warning(self, "Missing Fields",
                                "The following fields are required and cannot be empty: "
                                f"{', '.join(missing_fields)}")
            return

        reply = QMessageBox.question(self, 'Confirm Data',
                                     f"Would you like to proceed?",
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

            self.searchButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.edit_mode = False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer data: {e}")

    def edit_customer_data(self):
        self.searchButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.enable_all_fields()
        self.edit_mode = True

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


# 추가: Officer 선택 창 정의
class OfficerSelectDialog(QDialog):
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


def main():
    app = QApplication(sys.argv)
    window = SearchCustomerApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()