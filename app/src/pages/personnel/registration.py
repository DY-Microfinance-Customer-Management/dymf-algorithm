import sys, os, re, requests
from datetime import timedelta
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import pandas as pd

from src.components import DB, storageBucket
from src.components.select_staff import SelectStaffWindow

class PersonnelRegisterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.setup_connections()
        self.disable_all_fields()
        self.current_staff_id = None
        self.edit_mode = False
        self.initialize_buttons()
        self.show()

    def initialize_buttons(self):
        self.searchButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.markAsResignButton.setEnabled(False)
        self.newButton.setEnabled(True)  # Enable New button

    def setup_connections(self):
        self.searchButton.clicked.connect(self.open_select_staff_window)
        self.newButton.clicked.connect(self.new_staff_data)  # New button connected
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_staff_data)
        self.editButton.clicked.connect(self.edit_staff_data)
        self.imageButton.clicked.connect(self.select_image)

        self.tel2ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel2ByThree.textChanged.connect(self.limit_phone_length)
        self.tel1ByTwo.textChanged.connect(self.limit_phone_length)
        self.tel1ByThree.textChanged.connect(self.limit_phone_length)

    def reset_current_staff_id(self):
        self.current_staff_id = None

    def open_select_staff_window(self):
        self.select_staff_window = SelectStaffWindow()
        self.select_staff_window.staff_selected.connect(self.handle_staff_selected)
        self.select_staff_window.show()

    @QtCore.pyqtSlot(dict)
    def handle_staff_selected(self, staff_data):
        try:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.current_staff_id = staff_data.get('uid', '')
            self.populate_fields_with_staff_data(staff_data)

            self.name.setText(staff_data.get("name", ""))
            self.dateOfBirth.setDate(QtCore.QDate.fromString(staff_data.get("date_of_birth", "2000-01-01"), QtCore.Qt.ISODate))

            self.disable_all_fields()
            self.editButton.setEnabled(True)
            self.markAsResignButton.setEnabled(True)

        finally:
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)

    def populate_fields_with_staff_data(self, staff_data):
        self.name.setText(staff_data.get("name", ""))
        self.nrcNo.setText(staff_data.get("nrc_no", ""))
        self.dateOfBirth.setDate(QtCore.QDate.fromString(staff_data.get("date_of_birth"), QtCore.Qt.ISODate))
        self.gender.setCurrentText(staff_data.get("gender", ""))
        self.tel2ByOne.setText(staff_data.get("tel2ByOne", ""))
        self.tel2ByTwo.setText(staff_data.get("tel2ByTwo", ""))
        self.tel2ByThree.setText(staff_data.get("tel2ByThree", ""))
        self.tel1ByOne.setText(staff_data.get("tel1ByOne", ""))
        self.tel1ByTwo.setText(staff_data.get("tel1ByTwo", ""))
        self.tel1ByThree.setText(staff_data.get("tel1ByThree", ""))
        self.email.setText(staff_data.get("email", ""))
        self.address.setText(staff_data.get("address", ""))
        self.salary.setText(staff_data.get("salary", ""))
        self.ssb.setText(staff_data.get("ssb", ""))
        self.incomeTax.setText(staff_data.get("income_tax", ""))
        self.bonus.setText(staff_data.get("bonus", ""))

        # Load image if available
        image_url = staff_data.get("image_url", "")
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
                print("Error", f"Failed to load image: {e}")
                self.imageLabel.clear()
        else:
            self.imageLabel.clear()

    def new_staff_data(self):
        # Clear all fields and enable them for new data input
        self.clear_fields()
        self.enable_all_fields()
        self.saveButton.setEnabled(True)
        self.edit_mode = False  # New entry, not edit mode
        self.current_staff_id = None

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
        self.tel2ByOne.clear()
        self.tel2ByTwo.clear()
        self.tel2ByThree.clear()
        self.tel1ByOne.clear()
        self.tel1ByTwo.clear()
        self.tel1ByThree.clear()
        self.email.clear()
        self.address.clear()
        self.salary.clear()
        self.ssb.clear()
        self.incomeTax.clear()
        self.bonus.clear()
        self.current_staff_id = None
        self.disable_all_fields()
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.imageLabel.clear()

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
        self.address.setEnabled(False)
        self.salary.setEnabled(False)
        self.ssb.setEnabled(False)
        self.incomeTax.setEnabled(False)
        self.bonus.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.imageButton.setEnabled(False)
        self.markAsResignButton.setEnabled(False)

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
        self.address.setEnabled(True)
        self.salary.setEnabled(True)
        self.ssb.setEnabled(True)
        self.incomeTax.setEnabled(True)
        self.bonus.setEnabled(True)
        self.imageButton.setEnabled(True)

    def prepare_save_staff_data(self):
        staff_data = self.get_staff_data()

        # Required fields
        required_fields = [
            "name", "nrc_no", "date_of_birth", "gender"
        ]

        # Check if any required fields are missing
        missing_fields = []

        # Check tel1 related fields
        if not all([self.tel1ByOne.text(), self.tel1ByTwo.text(), self.tel1ByThree.text()]):
            missing_fields.append("Tel1")

        # Check required fields
        for field in required_fields:
            if not staff_data.get(field):
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
            self.save_staff_data()

    def get_staff_data(self):
        staff_data = {
            "name": self.name.text(),
            "nrc_no": self.nrcNo.text(),
            "date_of_birth": self.dateOfBirth.date().toString(QtCore.Qt.ISODate),
            "gender": self.gender.currentText(),
            "tel1ByOne": self.tel1ByOne.text(),
            "tel1ByTwo": self.tel1ByTwo.text(),
            "tel1ByThree": self.tel1ByThree.text(),
            "tel2ByOne": self.tel2ByOne.text(),
            "tel2ByTwo": self.tel2ByTwo.text(),
            "tel2ByThree": self.tel2ByThree.text(),
            "email": self.email.text(),
            "address": self.address.text(),
            "salary": self.salary.text(),
            "ssb": self.ssb.text(),
            "income_tax": self.incomeTax.text(),
            "bonus": self.bonus.text()
        }
        return staff_data

    def save_staff_data(self):
        staff_data = self.get_staff_data()

        try:
            if self.edit_mode and self.current_staff_id:
                staff_uid = self.current_staff_id
                DB.collection('Staff').document(staff_uid).update(staff_data)
            else:
                new_staff_ref = DB.collection('Staff').add(staff_data)
                staff_uid = new_staff_ref[1].id
                staff_data["uid"] = staff_uid
                DB.collection('Staff').document(staff_uid).update({"uid": staff_uid})

            if hasattr(self, 'selected_image_path') and os.path.exists(self.selected_image_path):
                image_blob = storageBucket.blob(f'staff_images/{staff_uid}.jpg')

                image_blob.upload_from_filename(self.selected_image_path)

                image_url = image_blob.generate_signed_url(expiration=timedelta(days=365))

                staff_data["image_url"] = image_url
                DB.collection('Staff').document(staff_uid).update({"image_url": image_url})

            QMessageBox.information(self, "Success", "Staff data saved successfully.")
            self.clear_fields()

            self.searchButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.edit_mode = False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save staff data: {e}")

    def edit_staff_data(self):
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

def main():
    app = QApplication(sys.argv)
    window = PersonnelRegisterApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
