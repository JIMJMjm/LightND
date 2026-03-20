from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QDialog, QWidget, QLabel, QFrame, QCheckBox, QPushButton

from BySide import DefaultFont, ScrollField, ClickableLabel
from config import LANG

font1 = QFont()
font1.setFamily("宋体")
font1.setPointSize(11)

font2 = DefaultFont(11)

font3 = DefaultFont(13)


class TitleWidget(QWidget):
    def __init__(self, num_name, width: int = 1000, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, 80)
        self.numname, self.name = num_name

        path = f'images/thumbnails/{self.numname}.jpg'

        self.thumbnail = QLabel(parent=self)
        self.thumbnail.setGeometry(0, 0, 60, 80)
        self.thumbnail.setPixmap(QPixmap(path).scaled(60, 80))

        self.bookname = QLabel(parent=self)
        self.bookname.setGeometry(65, 0, width - 60, 80)
        self.bookname.setFont(font1)
        self.bookname.setText(self.name)

        self.brd = QFrame(parent=self)
        self.brd.setFixedSize(width, 80)
        self.brd.move(0, 0)
        self.brd.setStyleSheet("border: 2px solid rgb(100, 100, 100); padding: 1px;")


class VolumeWidget(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.isChecked = False
        self.setGeometry(0, 0, 498, 40)

        self.volume = QFrame(self)
        self.volume.setStyleSheet(
            "#Task { border: 2px solid rgb(100, 100, 100); padding: 1px; }"
        )
        self.volume.setObjectName("Task")
        self.volume.setGeometry(0, 0, 481, 41)

        self.line = QFrame(parent=self.volume)
        self.line.setGeometry(40, 0, 3, 41)
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        self.label = QLabel(parent=self.volume)
        self.label.setGeometry(58, 0, 390, 40)
        self.label.setText(name)
        self.label.setFont(font1)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")

        self.checkBox = QCheckBox(parent=self.volume)
        self.checkBox.setText("")
        self.checkBox.setChecked(False)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setGeometry(14, 13, 16, 16)

        self.checkBox.clicked.connect(self.switchCheckState)

    def switchCheckState(self):
        self.isChecked = not self.isChecked

    def setCheckState(self, isChecked):
        self.isChecked = isChecked
        self.checkBox.setChecked(isChecked)


class MenuWidget(QWidget):
    def __init__(self, parent=None, vols: list = None, main=False):
        super().__init__(parent)
        if vols is None:
            vols = []
        self.vols = vols
        self.setFixedSize(500, 540)
        self.main = main

        self.widgets = [VolumeWidget(i, parent=self) for i in vols]
        self.scroll_field = ScrollField(parent=self, widgets=self.widgets, Geometry=(0, 0, 500, 500))

        self.select_all = QCheckBox(parent=self)
        self.select_all.setChecked(False)
        self.select_all.setGeometry(11, 513, 16, 16)

        self.select_all_text = ClickableLabel(parent=self)
        self.select_all_text.setText("Select All")
        self.select_all_text.setFont(font2)
        self.select_all_text.setGeometry(31, 513, 100, 16)

        self.download_button = QPushButton(parent=self)
        self.download_button.setText("Download")
        self.download_button.setFont(font3)
        self.download_button.setGeometry(385, 504, 105, 34)

        if not self.main:
            self.download_button.setHidden(True)

        self.select_all.clicked.connect(self.selectAll)
        self.select_all_text.clicked.connect(self.selectAll)
        for i in self.widgets:
            i.checkBox.clicked.connect(self.checkSelectAll)

    def selectAll(self):
        opposite = not self.select_all.isChecked()
        self.select_all.setChecked(opposite)
        for i in self.widgets:
            i.setCheckState(opposite)

    def checkSelectAll(self):
        if not all((i.isChecked for i in self.widgets)):
            self.select_all.setChecked(False)
            return
        self.select_all.setChecked(True)

    def setMain(self):
        self.main = True
        self.download_button.setHidden(False)

    def __getitem__(self, item):
        return self.vols[item]


class UpdateWindow(QDialog):
    def __init__(self, num_name, parent=None, additions: list = None, modifications: list = None):
        super().__init__(parent)
        self.setWindowTitle(LANG['UPD_window'])
        # self.setModal(True)
        width = 1000
        mode = 'all'

        self.additions = additions
        self.modifications = modifications
        if not additions:
            self.additions = []
            width -= 500
            mode = 'modifications'
        if not modifications:
            self.modifications = []
            width -= 500
            mode = 'additions'
        self.setFixedSize(width, 640)

        self.titleWidget = TitleWidget(num_name, parent=self, width=width)
        self.titleWidget.move(0, 0)

        self.i_a = None
        self.i_m = None
        self.menu_1 = []
        self.menu_2 = []

        if mode != 'modifications':
            self.menu_1 = MenuWidget(parent=self, main=False, vols=self.additions)
            self.i_a = QLabel(parent=self, text='Additions:')
            self.i_a.setFixedSize(80, 20)
            self.i_a.setFont(font2)

        if mode != 'additions':
            self.menu_2 = MenuWidget(parent=self, main=False, vols=self.modifications)
            self.i_m = QLabel(parent=self, text='Modifications:')
            self.i_m.setFixedSize(82, 20)
            self.i_m.setFont(font2)

        if mode == 'all':
            self.i_a.move(220, 81)
            self.i_m.move(718, 81)
            self.menu_1.move(0, 100)
            self.menu_2.move(501, 100)
            self.menu_2.setMain()
            self.bt = self.menu_2.download_button

            self.line = QFrame(parent=self)
            self.line.setGeometry(500, 80, 2, 1000)
            self.line.setFrameShape(QFrame.Shape.VLine)
            self.line.setFrameShadow(QFrame.Shadow.Sunken)

        if mode == 'additions':
            self.i_a.move(220, 81)
            self.menu_1.move(0, 100)
            self.menu_1.setMain()
            self.bt = self.menu_1.download_button

        if mode == 'modifications':
            self.i_m.move(218, 81)
            self.menu_2.move(0, 100)
            self.menu_2.setMain()
            self.bt = self.menu_2.download_button

    def getAllDownloads(self):
        self.close()
        return self.menu_1[:] + self.menu_2[:]


def activate1():
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    wd = UpdateWindow(('3057', '1919'), parent=None, additions=['1', '2', '3', '4'], modifications=['1', '2', '3', '5'])
    wd.show()
    app.exec()


if __name__ == '__main__':
    activate1()
