import sys, os, re, requests
from datetime import timedelta
from io import BytesIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QListWidget, QVBoxLayout, QDialog, QPushButton
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap, QIcon
from PyQt5.QtCore import Qt

from src.components import DB, storageBucket
from src.pages.loan.select_customer import SelectCustomerWindow

class RegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.show()
        self.setup_connections()
        self.disable_all_fields()
        self.current_customer_id = None
        self.edit_mode = False
        self.initialize_buttons()
        self.setup_counseling_table()
        self.edit_mode = False
        self.selected_counseling_row = None

    def setup_counseling_table(self):
        model = QStandardItemModel(0, 4)
        model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])
        self.counselingTable.setModel(model)
        self.counselingTable.setSelectionBehavior(self.counselingTable.SelectRows)

    def initialize_buttons(self):
        self.searchButton.setEnabled(True)
        self.newButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)

    def setup_connections(self):
        self.newButton.clicked.connect(self.on_new_button_clicked)
        self.searchButton.clicked.connect(self.open_select_customer_window)
        self.name.textChanged.connect(self.not_input_number)
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.editButton.clicked.connect(self.edit_customer_data)
        self.imageButton.clicked.connect(self.select_image)
        
        self.selectLoanOfficerButton.clicked.connect(self.open_officer_select_dialog)  # 추가된 부분

        self.counselingNewButton.clicked.connect(self.on_counseling_new_clicked)
        self.counselingEditButton.clicked.connect(self.on_counseling_edit_clicked)
        self.counselingSaveButton.clicked.connect(self.save_counsel_data)
        self.counselingDeleteButton.clicked.connect(self.delete_counsel_data)
        self.counselingTable.clicked.connect(self.on_counseling_table_clicked)

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

    def on_new_button_clicked(self):
        self.clear_fields()
        self.reset_current_customer_id()
        self.enable_all_fields()
        self.edit_mode = False
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.imageButton.setEnabled(True)
        self.clear_counseling_table()  # 테이블 정보 초기화

    def open_select_customer_window(self):
        self.setEnabled(False)

        self.select_customer_window = SelectCustomerWindow()
        self.select_customer_window.customer_selected.connect(self.handle_customer_selected)
        self.select_customer_window.show()

    def clear_counseling_table(self):
        model = QStandardItemModel(0, 4)
        model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])
        self.counselingTable.setModel(model)

    @QtCore.pyqtSlot(dict)
    def handle_customer_selected(self, customer_data):
        try:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.current_customer_id = customer_data.get('uid', '')
            self.populate_fields_with_customer_data(customer_data)

            self.searchName.setText(customer_data.get("name", ""))
            date_of_birth = customer_data.get("date_of_birth", "")
            self.searchDateOfBirth.setText(date_of_birth)

            self.load_counseling_data()

            self.disable_all_fields()
            self.disable_counseling_fields()
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

    def load_counseling_data(self):
        try:
            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                counseling_data = customer_data.get("counseling", [])

                model = QStandardItemModel(len(counseling_data), 4)
                model.setHorizontalHeaderLabels(["Date", "Subject", "Details", "Corrective Measure"])

                for row_idx, counsel in enumerate(counseling_data):
                    model.setItem(row_idx, 0, QStandardItem(counsel.get("counsel_date", "")))
                    model.setItem(row_idx, 1, QStandardItem(counsel.get("counsel_subject", "")))
                    model.setItem(row_idx, 2, QStandardItem(counsel.get("counsel_details", "")))
                    model.setItem(row_idx, 3, QStandardItem(counsel.get("corrective_measure", "")))

                self.counselingTable.setModel(model)
                self.counselingTable.resizeColumnsToContents()

            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load counseling data: {e}")

    def on_counseling_new_clicked(self):
        self.counselingDate.setDate(QtCore.QDate.currentDate())
        self.counselingSubject.clear()
        self.counselingDetails.clear()
        self.counselingCorrectiveMeasure.clear()

        self.enable_counseling_fields()

        self.edit_mode = False
        self.selected_counseling_row = None

    def on_counseling_edit_clicked(self):
        selected_indexes = self.counselingTable.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "No Selection", "Please select a counseling record to edit.")
            return

        self.selected_counseling_row = selected_indexes[0].row()

        model = self.counselingTable.model()
        counsel_date = model.index(self.selected_counseling_row, 0).data(QtCore.Qt.DisplayRole)
        counsel_subject = model.index(self.selected_counseling_row, 1).data(QtCore.Qt.DisplayRole)
        counsel_details = model.index(self.selected_counseling_row, 2).data(QtCore.Qt.DisplayRole)
        corrective_measure = model.index(self.selected_counseling_row, 3).data(QtCore.Qt.DisplayRole)

        if counsel_date and counsel_subject:
            self.counselingDate.setDate(QtCore.QDate.fromString(counsel_date, "yyyy-MM-dd"))
            self.counselingSubject.setText(counsel_subject)
            self.counselingDetails.setPlainText(counsel_details)
            self.counselingCorrectiveMeasure.setText(corrective_measure)

            self.enable_counseling_fields()

            self.edit_mode = True
        else:
            QMessageBox.warning(self, "Error", "Failed to load counseling data. Please try again.")

    def delete_counsel_data(self):
        try:
            selected_indexes = self.counselingTable.selectionModel().selectedRows()

            if not selected_indexes:
                QMessageBox.warning(self, "No Selection", "Please select a counseling record to delete.")
                return

            selected_row = selected_indexes[0].row()

            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()
                counseling_data = customer_data.get("counseling", [])

                if 0 <= selected_row < len(counseling_data):
                    del counseling_data[selected_row]

                    customer_ref.update({"counseling": counseling_data})

                    QMessageBox.information(self, "Success", "Counseling data deleted successfully.")

                    self.counselingDate.setDate(QtCore.QDate(2000, 1, 1))
                    self.counselingSubject.clear()
                    self.counselingDetails.clear()
                    self.counselingCorrectiveMeasure.clear()

                    self.load_counseling_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete counseling data.")
            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete counseling data: {e}")

    def save_counsel_data(self):
        # 상담 정보가 모두 입력되었는지 확인
        if not self.counselingSubject.text() or not self.counselingDetails.toPlainText():
            QMessageBox.warning(self, "Missing Information", "Subject and Details are required.")
            return

        counsel_info = {
            "counsel_subject": self.counselingSubject.text(),
            "counsel_details": self.counselingDetails.toPlainText(),
            "counsel_date": self.counselingDate.date().toString(QtCore.Qt.ISODate),
            "corrective_measure": self.counselingCorrectiveMeasure.text()
        }

        if not self.current_customer_id:
            QMessageBox.warning(self, "No Customer", "Please select a customer before saving counseling data.")
            return

        try:
            customer_ref = DB.collection('Customer').document(self.current_customer_id)
            customer_doc = customer_ref.get()

            if customer_doc.exists:
                customer_data = customer_doc.to_dict()

                if "counseling" not in customer_data:
                    customer_data["counseling"] = []

                if self.edit_mode and self.selected_counseling_row is not None:
                    customer_data["counseling"][self.selected_counseling_row] = counsel_info
                else:
                    customer_data["counseling"].append(counsel_info)

                customer_ref.update({"counseling": customer_data["counseling"]})

                QMessageBox.information(self, "Success", "Counseling data saved successfully.")

                self.counselingDate.setDate(QtCore.QDate(2000, 1, 1))
                self.counselingSubject.clear()
                self.counselingDetails.clear()
                self.counselingCorrectiveMeasure.clear()
                self.load_counseling_data()

                self.disable_counseling_fields()

                self.edit_mode = False
                self.selected_counseling_row = None

            else:
                QMessageBox.warning(self, "No Customer Data", "The selected customer does not exist in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save counseling data: {e}")

    def on_counseling_table_clicked(self, index):
        if index.isValid():
            row = index.row()
            model = self.counselingTable.model()

            counsel_date = model.index(row, 0).data()
            counsel_subject = model.index(row, 1).data()
            counsel_details = model.index(row, 2).data()
            corrective_measure = model.index(row, 3).data()

            self.counselingDate.setDate(QtCore.QDate.fromString(counsel_date, "yyyy-MM-dd"))
            self.counselingSubject.setText(counsel_subject)
            self.counselingDetails.setPlainText(counsel_details)
            self.counselingCorrectiveMeasure.setText(corrective_measure)

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

        data_summary = (
            f"Name: {customer_data['name']}\n"
            f"NRC No.: {customer_data['nrc_no']}\n"
            f"Date of Birth: {customer_data['date_of_birth']}\n"
            f"Gender: {customer_data['gender']}\n"
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

        reply = QMessageBox.question(self, 'Confirm Data',
                                    f"Would you like to proceed?",
                                    #  f"Would you like to proceed?\n\n{data_summary}",
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
            self.newButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.edit_mode = False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer data: {e}")

    def edit_customer_data(self):
        self.newButton.setEnabled(False)
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
    window = RegistrationApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
