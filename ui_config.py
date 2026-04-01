from math import isclose
from typing import Literal
from os.path import exists as ext

from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator, QIcon
from PySide6.QtWidgets import QDialog, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QFrame

from BySide import ScrollField, DefaultFont, ClickableLabel, WidgetGrid
from config import (CONFIG, CONFIG_NOTATION, DEFAULT_SETTING,
                    modify_global_settings as mgs, get_global_settings as ggs, translate_to as tsl)

df15 = DefaultFont(15, underline=True)
df13 = DefaultFont(13)
df12 = DefaultFont(12)
df16 = DefaultFont(16)
df14 = DefaultFont(14)

LANG = tsl(CONFIG['LANGUAGE'])


class Ui_Config(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(1000, 550)
        self.setWindowTitle(LANG['CFG_window'])
        self.setWindowIcon(QIcon('images/icon.ico'))

        self.scrollfield = ScrollField(self)
        self.scrollfield.setGeometry(0, 0, 1000, 500)

        self.save_button = ClickableLabel(parent=self)
        self.save_button.setText(LANG['CFG_save'])
        self.save_button.setFont(df15)
        self.save_button.setGeometry(780, 509, 50, 32)
        self.save_button.lclicked.connect(lambda: self.handleSaveAll(q=True))

        self.apply_button = ClickableLabel(parent=self)
        self.apply_button.setText(LANG['CFG_apply'])
        self.apply_button.setFont(df15)
        self.apply_button.setGeometry(930, 509, 50, 32)
        self.apply_button.lclicked.connect(lambda: self.handleSaveAll(q=False))

        self.Cancel_button = ClickableLabel(parent=self)
        self.Cancel_button.setText(LANG['CFG_cancel'])
        self.Cancel_button.setFont(df15)
        self.Cancel_button.setGeometry(848, 509, 55, 32)
        self.Cancel_button.lclicked.connect(self.accept)

        self.reset_button = ClickableLabel(parent=self)
        self.reset_button.setText(LANG['CFG_reset'])
        self.reset_button.setFont(df15)
        self.reset_button.setGeometry(15, 509, 50, 32)
        self.reset_button.lclicked.connect(lambda: self.handleResetAll(q=False))

        entry_number = len(CONFIG)
        self.entry_content_grid = WidgetGrid(self)
        self.entry_content_grid.move(0, 0)
        self.entry_content_grid.setGridSize((1, entry_number))
        self.entry_content_grid.setChildSize((980, 65))
        self.entry_content_grid.resize(980, 65 * entry_number)

        for i, j in zip(CONFIG.keys(), CONFIG.values()):
            _type = ''
            if isinstance(j, bool):
                _type = 'bool'
            elif isinstance(j, int):
                _type = 'int'
            elif isinstance(j, float):
                _type = 'float'
            elif isinstance(j, str):
                _type = 'str'
                if 'PATH' in i:
                    _type = 'directory'
            # noinspection PyTypeChecker
            self.entry_content_grid.addWidget(ConfigEntry(_type=_type, entry_name=i, entry_content=j,
                                                          parent=self.entry_content_grid))
        self.scrollfield.setWidget(self.entry_content_grid)

    def handleSaveAll(self, q: bool = False):
        new_config = {}
        for i in self.entry_content_grid:
            i.handleSave()
            new_config[i.entry_name] = i.entry_content
        mgs(new_config)
        if q:
            self.accept()

    def handleResetAll(self, q: bool = False):
        for i in self.entry_content_grid:
            i.entry_content = DEFAULT_SETTING[i.entry_name]
            i.e_content.setText(str(DEFAULT_SETTING[i.entry_name]))
            i.handleSave()
        ggs(reset=True)
        if q:
            self.accept()


class ConfigEntry(QWidget):
    save_data = Signal(tuple)

    def __init__(self,
                 _type: Literal['bool', 'str', 'directory', 'float', 'int'],
                 entry_name: str,
                 entry_content: bool | str | float,
                 parent=None):
        super().__init__(parent)

        self.border = QFrame(self)
        self.border.setGeometry(0, 0, 400, 65)
        self.border.setStyleSheet("border: 1px solid rgba(0, 0, 0, 120)")

        self.border_2 = QFrame(self)
        self.border_2.setStyleSheet("border: 1px solid rgba(0, 0, 0, 120)")
        self.border_2.setGeometry(400, 0, 580, 65)

        self.label = QLabel(self)
        self.label.setText(CONFIG_NOTATION.get(entry_name))
        self.label.setFont(df12)
        self.label.setGeometry(405, 5, 575, 55)
        self.label.setWordWrap(True)

        self.type = _type
        self.entry_name = entry_name
        self.entry_content = entry_content
        self.init_content = entry_content

        self.setFixedSize(980, 65)
        self.setWindowTitle('Config')

        self.e_label = QLabel(parent=self, text=entry_name + ':')
        self.e_label.setFont(df13)
        self.e_label.setGeometry(8, 0, 312, 30)

        self.save_button = ClickableLabel(parent=self, text='Save')
        self.save_button.setFont(df12)
        self.save_button.setGeometry(362, 4, 35, 22)
        self.save_button.setHidden(True)
        self.save_button.lclicked.connect(self.handleSave)

        self.reset_button = ClickableLabel(parent=self, text='Reset')
        self.reset_button.setFont(df12)
        self.reset_button.setGeometry(320, 4, 37, 22)
        self.reset_button.setHidden(True)
        self.reset_button.lclicked.connect(lambda isBool=_type == 'bool': self.handleReset(isBool))

        if _type == 'bool':
            self.e_content = ClickableLabel(parent=self)
            self.e_content.setGeometry(15, 30, 50, 30)
            if self.entry_content:
                self.e_content.setText('True')
            if not self.entry_content:
                self.e_content.setText('False')
            self.e_content.lclicked.connect(self.handleBoolSwitch)
            self.e_content.setFont(df14)

        if _type == 'directory':
            self.e_content = QLineEdit(parent=self)
            self.e_content.setText(entry_content)
            self.e_content.textChanged.connect(self.handleStringChange)
            self.e_content.setGeometry(8, 32, 365, 30)
            self.e_content.setFont(df14)

            self.getdir = QPushButton(parent=self)
            self.getdir.setText('...')
            self.getdir.setGeometry(374, 35, 25, 24)
            self.getdir.clicked.connect(self.askDirectory)

        if _type == 'float':
            self.e_content = QLineEdit(parent=self)
            self.e_content.setText(str(entry_content))
            self.e_content.setGeometry(8, 32, 200, 30)
            self.e_content.setValidator(QDoubleValidator(decimals=3))
            self.e_content.textChanged.connect(self.handleFloatChange)
            self.e_content.setFont(df16)

        if _type == 'str':
            self.e_content = QLineEdit(parent=self)
            self.e_content.setText(entry_content)
            self.e_content.textChanged.connect(self.handleStringChange)
            self.e_content.setGeometry(8, 30, 350, 30)
            self.e_content.setFont(df14)

        if _type == 'int':
            entry_content = max(-65536, min(65536, int(entry_content)))
            self.entry_content = entry_content
            self.init_content = entry_content

            self.e_content = QLineEdit(parent=self)
            self.e_content.setText(str(entry_content))
            self.e_content.setGeometry(8, 32, 100, 30)
            self.e_content.setValidator(QIntValidator())
            self.e_content.textChanged.connect(self.handleIntChange)
            self.e_content.setFont(df16)

        # self.save_data.connect(lambda data: print(data))

    def handleBoolSwitch(self):
        self.entry_content = not self.entry_content
        if self.entry_content:
            self.e_content.setText('True')
        else:
            self.e_content.setText('False')
        self.testifyChange()

    def handleStringChange(self):
        self.entry_content = self.e_content.text()
        self.testifyChange()

    def handleFloatChange(self):
        self.entry_content = float(self.e_content.text())
        self.testifyChange(isfloat=False)

    def handleIntChange(self):
        if self.e_content.text() == '-' or self.e_content.text() == '':
            self.entry_content = 0
        else:
            self.entry_content = max(-65536, min(65536, int(self.e_content.text())))
        self.testifyChange()

    def testifyChange(self, isfloat: bool = False):
        if isfloat:
            if isclose(self.entry_content, self.init_content):
                self.save_button.setHidden(True)
                self.reset_button.setHidden(True)
                return
        if self.entry_content == self.init_content:
            self.save_button.setHidden(True)
            self.reset_button.setHidden(True)
            return
        self.save_button.setHidden(False)
        self.reset_button.setHidden(False)

    def askDirectory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select a Directory",
        )
        if directory:
            self.entry_content = directory
            self.e_content.setText(directory)

    def handleReset(self, isBool: bool = False):
        self.entry_content = self.init_content
        self.e_content.setText(str(self.entry_content))
        if isBool:
            self.testifyChange()

    def handleSave(self):
        if self.type == 'directory' and not ext(self.entry_content):
            print('Directory invalid. Please enter a valid directory.')
            return
        if self.type == 'float' and not isinstance(self.entry_content, float):
            print('Float invalid. Please enter a valid float.')
            return
        if self.type == 'int' and not isinstance(self.entry_content, int):
            print('Int invalid. Please enter a valid int.')
            return
        self.save_data.emit((self.entry_name, self.entry_content))
        self.init_content = self.entry_content
        self.testifyChange()


def activate1():
    app = QApplication([])
    ui = Ui_Config()
    ui.show()
    app.exec()


if __name__ == "__main__":
    activate1()
