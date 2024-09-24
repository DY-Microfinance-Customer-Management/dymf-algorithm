import sys, os, re, requests
from datetime import timedelta
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidget, QVBoxLayout, QDialog, QPushButton
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from src.components import DB, storageBucket
from src.components.select_customer import SelectCustomerWindow

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
        self.cpNumber.setEnabled(False)  # Disable CP Number by default

    def setup_connections(self):
        self.searchButton.clicked.connect(self.open_select_customer_window)
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.editButton.clicked.connect(self.edit_customer_data)
        self.imageButton.clicked.connect(self.select_image)
        self.selectLoanOfficerButton.clicked.connect(self.open_officer_select_dialog)

        self.tel2ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel2ByThree.textChanged.connect(self.limit_phone_length)
        self.tel1ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel1ByThree.textChanged.connect(self.limit_phone_length)
        self.loanType.currentIndexChanged.connect(self.toggle_cp_number)  # Toggle CP Number based on loan type

    def toggle_cp_number(self):
        # Enable CP Number field only if "Group Loan" is selected
        if self.loanType.currentText() == "Group Loan":
            self.cpNumber.setEnabled(True)
        else:
            self.cpNumber.setEnabled(False)
            self.cpNumber.clear()  # Clear the field if it's disabled

    def reset_current_customer_id(self):
        self.current_customer_id = None

    def open_officer_select_dialog(self):
        dialog = OfficerSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_officer = dialog.get_selected_officer()
            if selected_officer:
                self.loanOfficer.setText(f"{selected_officer['name']} - {selected_officer['service_area']}")

    def open_select_customer_window(self):
        #self.setEnabled(False)
        #이거 하면 search 중간에 끊으면 먹통됨 ㅋ
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
        self.tel2ByOne.setCurrentText(customer_data.get("tel2ByOne", ""))
        self.tel2ByTwo.setText(customer_data.get("tel2ByTwo", ""))
        self.tel2ByThree.setText(customer_data.get("tel2ByThree", ""))
        self.tel1ByOne.setCurrentText(customer_data.get("tel1ByOne", ""))
        self.tel1ByTwo.setText(customer_data.get("tel1ByTwo", ""))
        self.tel1ByThree.setText(customer_data.get("tel1ByThree", ""))
        self.email.setText(customer_data.get("email", ""))

        # Set loan type and CP Number
        self.loanType.setCurrentText(customer_data.get("loan_type", ""))
        self.cpNumber.setText(customer_data.get("cp_number", ""))

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

        # Toggle CP Number field based on loan type
        self.toggle_cp_number()

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
        self.searchName.clear()
        self.searchDateOfBirth.clear()
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
        self.cpNumber.clear()
        self.loanType.setCurrentIndex(0)  # Reset loan type to default

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
        self.loanType.setEnabled(True)
        self.cpNumber.setEnabled(self.loanType.currentText() == "Group Loan")  # Enable CP Number if necessary

    def prepare_save_customer_data(self):
        customer_data = self.get_customer_data()

        # Required fields
        required_fields = [
            "name", "nrc_no", "date_of_birth", "gender"
        ]

        # Check if loan type is "Group Loan" and add cp_number to required fields
        if self.loanType.currentText() == "Group Loan":
            required_fields.append("cp_number")

        # Check if any required fields are missing
        missing_fields = []

        # Check tel1 related fields
        if not all([self.tel1ByOne.currentText(), self.tel1ByTwo.text(), self.tel1ByThree.text()]):
            missing_fields.append("Tel1")

        # Check required fields
        for field in required_fields:
            if not customer_data.get(field):
                missing_fields.append(field)

        if missing_fields:
            QMessageBox.warning(self, "Missing Fields",
                                f"The following fields are required and cannot be empty: {', '.join(missing_fields)}")
            return

        reply = QMessageBox.question(self, 'Confirm Data',
                                     f"Would you like to proceed?",
                                     QMessageBox.Ok | QMessageBox.Cancel,
                                     QMessageBox.Cancel)

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
            "loan_officer": self.loanOfficer.text(),
            "loan_type": self.loanType.currentText(),  # Add loan type
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

# Officer selection dialog definition
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