import sys
from PyQt5.QtWidgets import QApplication, QTableView, QHeaderView
from PyQt5.QtCore import QAbstractTableModel, Qt

class TableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super(TableModel, self).__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
        return None

app = QApplication(sys.argv)

data = [
    [4, 9, 2],
    [1, 0, 0],
    [3, 5, 1],
]

headers = ["Column 1", "Column 2", "Column 3"]

model = TableModel(data, headers)
table_view = QTableView()
table_view.setModel(model)

# 열 이름 설정
table_view.horizontalHeader().setStretchLastSection(True)
table_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 특정 열 (여기서는 두 번째 열)의 너비를 조정

table_view.show()
sys.exit(app.exec_())
