import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QIntValidator, QDoubleValidator, QBrush, QColor
from PyQt5.QtCore import QDate, Qt

from src.components import DB

class SettingsFixedAssetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "fixed_asset.ui")
        uic.loadUi(ui_path, self)

        # 창 크기 고정
        self.setFixedSize(self.size())

        icon_path = os.path.join(current_dir, 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))

        self.current_asset_id = None
        self.current_status = None
        self.initialize_ui()
        self.show()

    def initialize_ui(self):
        self.editButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.terminateButton.setEnabled(False)
        self.item.setEnabled(False)
        self.purchaseDate.setEnabled(False)
        self.value.setEnabled(False)
        self.depreciationPeriod.setEnabled(False)
        self.depreciationRatio.setEnabled(False)

        self.value.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        self.depreciationPeriod.setValidator(QIntValidator(0, 100))
        self.depreciationRatio.setValidator(QDoubleValidator(0.0, 100.0, 2))

        self.setup_table()

        self.newButton.clicked.connect(self.on_new_clicked)
        self.editButton.clicked.connect(self.on_edit_clicked)
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.deleteButton.clicked.connect(self.on_delete_clicked)
        self.terminateButton.clicked.connect(self.on_terminate_clicked)
        self.fixedAssetTable.clicked.connect(self.on_table_row_clicked)

        self.load_assets()

    def setup_table(self):
        self.model = QStandardItemModel(0, 7)
        self.model.setHorizontalHeaderLabels(["Status", "Item", "Purchase Date", "Value", "Depreciation Period", "Depreciation Ratio", "asset_id"])
        self.fixedAssetTable.setModel(self.model)
        self.fixedAssetTable.setSelectionBehavior(QTableView.SelectRows)
        self.fixedAssetTable.setColumnHidden(6, True)

    def load_assets(self):
        try:
            assets = DB.collection('Assets').get()

            self.model.setRowCount(0)
            for asset in assets:
                asset_data = asset.to_dict()
                
                status = 'Active' if asset_data.get("active", "") == True else 'Closed'
                status_item = QStandardItem(status)
                item = QStandardItem(asset_data.get("item", ""))
                purchase_date = QStandardItem(asset_data.get("purchase_date", ""))
                value = QStandardItem(asset_data.get("value", ""))
                depreciation_period = QStandardItem(asset_data.get("depreciation_period", ""))
                depreciation_ratio = QStandardItem(str(asset_data.get("depreciation_ratio", "")))
                asset_id = QStandardItem(asset_data.get("asset_id", ""))

                if status == 'Closed':
                    for i in [status_item, item, purchase_date, value, depreciation_period, depreciation_ratio, asset_id]:
                        i.setForeground(QBrush(QColor(255, 0, 0)))

                self.model.appendRow([status_item, item, purchase_date, value, depreciation_period, depreciation_ratio, asset_id])

            self.fixedAssetTable.resizeColumnsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load assets: {e}")

    def on_new_clicked(self):
        self.item.clear()
        self.purchaseDate.setDate(QDate.currentDate())
        self.value.clear()
        self.depreciationPeriod.clear()
        self.depreciationRatio.clear()

        self.item.setEnabled(True)
        self.purchaseDate.setEnabled(True)
        self.value.setEnabled(True)
        self.depreciationPeriod.setEnabled(True)
        self.depreciationRatio.setEnabled(True)
        self.terminateButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.current_asset_id = None

    def on_edit_clicked(self):
        self.item.setEnabled(True)
        self.purchaseDate.setEnabled(True)
        self.value.setEnabled(True)
        self.depreciationPeriod.setEnabled(True)
        self.depreciationRatio.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

    def on_save_clicked(self):
        item = self.item.text()
        purchase_date = self.purchaseDate.date()
        value = self.value.text()
        depreciation_period = self.depreciationPeriod.text()
        depreciation_ratio = self.depreciationRatio.text()

        if not item or not purchase_date or not value or not depreciation_period or not depreciation_ratio:
            QMessageBox.warning(self, "Validation Error", "All fields cannot be empty.")
            return

        try:
            depreciation_period_years = int(depreciation_period)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Depreciation Period must be a valid number.")
            return

        end_date = purchase_date.addYears(depreciation_period_years)

        asset_data = {
            'item': item,
            'purchase_date': purchase_date.toString("yyyy-MM-dd"),
            'value': value,
            'depreciation_period': depreciation_period,
            'depreciation_ratio': depreciation_ratio,
            'end_date': end_date.toString("yyyy-MM-dd"),
            'active': True
        }

        try:
            if self.current_asset_id:
                DB.collection('Assets').document(self.current_asset_id).update(asset_data)
                QMessageBox.information(self, "Success", "Asset information updated successfully.")
            else:
                new_asset_ref = DB.collection('Assets').add(asset_data)
                DB.collection('Assets').document(new_asset_ref[1].id).update({"asset_id": new_asset_ref[1].id})
                QMessageBox.information(self, "Success", "New asset added successfully.")

            self.clear_fields()
            self.load_assets()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save asset data: {e}")

    def on_delete_clicked(self):
        if not self.current_asset_id:
            QMessageBox.warning(self, "Selection Error", "No asset selected.")
            return

        try:
            DB.collection('Assets').document(self.current_asset_id).delete()
            QMessageBox.information(self, "Success", "Asset deleted successfully.")
            self.clear_fields()
            self.load_assets()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete asset: {e}")

    def on_table_row_clicked(self, index):
        row = index.row()
        model = self.fixedAssetTable.model()
        asset_id = model.index(row, 1).data()
        item = model.index(row, 1).data()
        purchase_date = model.index(row, 2).data()
        value = model.index(row, 3).data()
        depreciation_period = model.index(row, 4).data()
        depreciation_ratio = model.index(row, 5).data()
        status = model.index(row, 0).data()

        self.current_status = status

        self.item.setText(item)
        qdate = QDate.fromString(purchase_date, "yyyy-MM-dd")
        self.purchaseDate.setDate(qdate)
        self.value.setText(value)
        self.depreciationPeriod.setText(depreciation_period)
        self.depreciationRatio.setText(depreciation_ratio)

        assets = DB.collection('Assets').where('asset_id', '==', asset_id).get()
        if assets:
            self.current_asset_id = assets[0].id

        self.deleteButton.setEnabled(True)
        self.saveButton.setEnabled(False)

        if status == "Closed":
            self.editButton.setEnabled(False)
        else:
            self.editButton.setEnabled(True)

        self.item.setEnabled(False)
        self.purchaseDate.setEnabled(False)
        self.value.setEnabled(False)
        self.depreciationPeriod.setEnabled(False)
        self.depreciationRatio.setEnabled(False)

    def on_terminate_clicked(self):
        if not self.current_asset_id:
            QMessageBox.warning(self, "Selection Error", "No asset selected.")
            return

        try:
            # Firestore에서 'active' 필드를 False로 업데이트 (상태를 'Closed'로 설정)
            DB.collection('Assets').document(self.current_asset_id).update({'active': False})
            QMessageBox.information(self, "Success", "Asset terminated successfully.")
            self.clear_fields()
            self.load_assets()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to terminate asset: {e}")

    def clear_fields(self):
        self.item.clear()
        self.purchaseDate.setDate(QDate.currentDate())
        self.value.clear()
        self.depreciationPeriod.clear()
        self.depreciationRatio.clear()

        self.item.setEnabled(False)
        self.purchaseDate.setEnabled(False)
        self.value.setEnabled(False)
        self.depreciationPeriod.setEnabled(False)
        self.depreciationRatio.setEnabled(False)
        self.terminateButton.setEnabled(False)

        self.saveButton.setEnabled(False)
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = SettingsFixedAssetApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()