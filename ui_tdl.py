from os.path import exists as ext

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QHBoxLayout, QFileDialog)

from config import LANG


def getTodolist(file_path):
    if not ext(file_path):
        print('Not a valid file.')
    with open(file_path, 'r') as f:
        todolist = [i.strip() for i in f.readlines()]
    return todolist


class EditableTableWindow(QMainWindow):
    dataConfirmed = Signal(list)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_table()

    def init_ui(self):
        self.setWindowTitle(LANG['TODOLIST_window'])
        self.setWindowIcon(QIcon('images/icon.ico'))
        self.setFixedSize(500, 700)

        self.validator = QIntValidator(1, 9999)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        hlayout = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["序号", "数字编号"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
               QTableWidget {
                   background-color: #f8f9fa;
                   alternate-background-color: #e9ecef;
                   gridline-color: #dee2e6;
                   selection-background-color: #e8fcff;
                   selection-color: #000000;
                   font-size: 12px;
               }

               QTableWidget::horizontalHeader {
                   background-color: #495057;
                   color: white;
                   font-weight: bold;
               }
               QTableWidget::horizontalHeader::section {
                   background-color: #495057;
                   padding: 8px;
                   border: none;
                   border-right: 1px solid #6c757d;
                   font-size: 13px;
               }
               QTableWidget::horizontalHeader::section:last {
                   border-right: none;
               }

               QTableWidget::verticalHeader {
                   background-color: #f1f3f5;
               }

               QTableWidget::item:hover {
                   background-color: #d3d9df;
                   border: 1px solid #828D8F;
               }

               QTableWidget::item:selected {
                   background-color: #e8fcff;
                   color: white;
                   border: none;
               }

               QTableWidget::item:editable {
                   background-color: white;
               }

               QTableWidget::item:focus {
                   border: 2px solid #228be6;
                   outline: none;
               }
           """)

        self.confirm_button = QPushButton("确认")
        self.confirm_button.setFixedSize(80, 30)
        self.confirm_button.clicked.connect(self.on_confirm_clicked)

        self.cancel_button = QPushButton('取消')
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.close)

        self._import = QPushButton("导入")
        self._import.setFixedSize(80, 30)
        self._import.clicked.connect(self.select_todolist)

        hlayout.addWidget(self._import)
        hlayout.addStretch()
        hlayout.addWidget(self.cancel_button)
        hlayout.addWidget(self.confirm_button)
        layout.addWidget(self.table)
        layout.addLayout(hlayout)

    def init_table(self):
        self.add_new_row(row_number=1)
        self.table.itemChanged.connect(self.on_item_changed)

    def add_new_row(self, row_number: int):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        index_item = QTableWidgetItem(str(row_number))
        index_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_position, 0, index_item)

        data_item = QTableWidgetItem("")
        data_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row_position, 1, data_item)

    def setModifiable(self, state: bool) -> None:
        for row in range(self.table.rowCount()):
            if state:
                self.table.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEditable)
                continue
            self.table.item(row, 0).setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.item(row, 1).setFlags(Qt.ItemFlag.ItemIsEnabled)

    def on_item_changed(self, item: QTableWidgetItem):
        if item.column() != 1:
            return
        if item.row() != self.table.rowCount() - 1:
            self.table.setCurrentCell(self.table.rowCount(), 0)
            return

        data = item.text().strip()
        if not data:
            self.table.setCurrentCell(self.table.rowCount()+1, 0)
            return

        self.table.itemChanged.disconnect(self.on_item_changed)

        if self.validator.validate(data, 0)[0] != self.validator.State.Acceptable:
            item.setText("")
            self.table.setCurrentCell(self.table.rowCount(), 0)
            self.table.itemChanged.connect(self.on_item_changed)
            return

        next_row_number = self.table.rowCount() + 1
        self.add_new_row(next_row_number)
        self.table.setCurrentCell(next_row_number-1, 1)

        self.table.itemChanged.connect(self.on_item_changed)

    def get_table_data(self) -> list[str]:
        return [self.table.item(row, 1).text().strip() for row in range(self.table.rowCount()-1)]

    def on_confirm_clicked(self):
        data = self.get_table_data()
        self.dataConfirmed.emit(data)
        self.close()

    def select_todolist(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            LANG['SELECT_FILE'],
            "./",
            "Text Files (*.txt)"
        )

        if not file_path:
            print('Not a valid file.')
            return
        todolist = getTodolist(file_path)
        table_data = self.get_table_data()
        todolist = set(todolist) - set(table_data)
        for i in todolist:
            self.table.item(self.table.rowCount()-1, 1).setText(i)


def main():
    pass


if __name__ == "__main__":
    main()
