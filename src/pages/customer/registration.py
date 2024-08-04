import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic, QtCore
from components import DB

class RegistrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "registration.ui")
        uic.loadUi(ui_path, self)
        self.show()
        self.setup_connections()

    def setup_connections(self):
        self.saveButton.clicked.connect(self.prepare_save_customer_data)
        self.editButton.clicked.connect(self.edit_customer_data)
        self.newButton.clicked.connect(self.clear_fields)

    def clear_fields(self):
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
            customer_ref = DB.collection('Customer')
            new_customer_ref = customer_ref.add(customer_data)
            QMessageBox.information(self, "Success", "Customer data saved successfully.")
            self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer data: {e}")

    def edit_customer_data(self):
        QMessageBox.information(self, "Edit Customer", "Feature not implemented yet.")
        # TODO: Implement the edit customer data functionality

def main():
    app = QApplication(sys.argv)
    window = RegistrationApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
