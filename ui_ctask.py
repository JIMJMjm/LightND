from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QDialog, QPushButton, QCheckBox, QLabel, QFrame

from BySide import ScrollField, ClickableLabel, WidgetGrid
from rating import StarRatingWidget as Rtw
from config import LUXINFO_TEMPLATE, LANG

EMPTY = QtCore.Qt.CheckState(0)
HALF = QtCore.Qt.CheckState(1)
FULL = QtCore.Qt.CheckState(2)

font = QtGui.QFont()
font.setFamily("Microsoft YaHei")
font.setPointSize(10)

font1 = QtGui.QFont()
font1.setFamily("宋体")
font1.setPointSize(11)


def get_default_name(selected_volumes: list):
    ind = 0
    i = selected_volumes[0]
    res = ''
    while ind < len(selected_volumes) and i <= selected_volumes[-1]:
        if i != selected_volumes[ind]:
            i += 1
            continue
        if ind + 1 == len(selected_volumes):
            res += str(selected_volumes[-1])
            break
        if i + 1 != selected_volumes[ind + 1]:
            res += str(i)
            res += '+'
        elif i - 1 != selected_volumes[ind - 1]:
            res += str(i)
            res += '~'
        i += 1
        ind += 1
    return res


def restore_from_default_name(path):
    dirs = path.split('/')
    if dirs[-2] != 'Slices':
        return 0
    filename = dirs[-1]
    if filename[0] != '[':
        return 0
    if filename[-6:] != '].docx':
        return 0
    return int(filename[1])


class TitleWidget(QWidget):
    def __init__(self, img, text: str, parent=None):
        super().__init__(parent=parent)

        self.image_path = img
        self.text = text

        self.setGeometry(0, 0, 500, 50)

        self.title_task = QFrame(self)

        self.line = QFrame(parent=self.title_task)
        self.line.setGeometry(QtCore.QRect(40, 0, 3, 51))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        self.titletxt = QLabel(parent=self.title_task)
        self.titletxt.setGeometry(QtCore.QRect(62, 0, 431, 51))

        self.titletxt.setFont(font1)
        self.titletxt.setWordWrap(True)
        self.titletxt.setObjectName("label")
        self.titletxt.setText(self.text)

        self.Thumbnail = QLabel(parent=self.title_task)
        self.Thumbnail.setGeometry(QtCore.QRect(0, 0, 41, 51))
        if 'byte' not in str(type(self.image_path)):
            self.Thumbnail.setPixmap(QtGui.QPixmap(self.image_path).scaled(41, 51))
        else:
            pm = QtGui.QPixmap()
            pm.loadFromData(self.image_path)
            self.Thumbnail.setPixmap(pm.scaled(41, 51))
        self.Thumbnail.setObjectName("Thumbnail")


class ChapterWigdet(QWidget):
    def __init__(self, parent, chap: str):
        super().__init__(parent)
        self.checked = False
        self.setFixedSize(441, 30)
        self.label = ClickableLabel(parent=self, text=chap)
        self.label.setObjectName('MAIN')
        self.setStyleSheet(
            "#MAIN { border: 2px solid rgb(100, 100, 100); padding: 2px; }"
            "#MAIN:hover { border: 2px solid rgba(219, 112, 147, 154); padding: 2px; }"
        )
        self.label.setFont(font)
        self.label.setGeometry(1, 0, 401, 30)

        self.checkBox = QtWidgets.QCheckBox(parent=self)
        self.checkBox.setText("")
        self.checkBox.setIconSize(QtCore.QSize(16, 16))
        self.checkBox.setGeometry(414, 9, 16, 16)
        self.checkBox.clicked.connect(self.upd)
        self.label.clicked.connect(self._label_clicked)

    def upd(self):
        self.checked = self.checkBox.isChecked()

    def _label_clicked(self):
        if not self.checkBox.isEnabled():
            return
        self.checkBox.nextCheckState()
        self.upd()


class VolumeWidget(QWidget):
    delta_ex = QtCore.Signal(int)

    def __init__(self, text: str | list, parent=None, chapters: bool = False, ext_chaps: list | bool = None):
        super().__init__(parent)
        if ext_chaps is None:
            ext_chaps = []

        self.isChecked = False
        self.setGeometry(0, 0, 500, 40)

        self.volume = QFrame(self)
        self.volume.setStyleSheet("#Task { border: 2px solid rgb(100, 100, 100); padding: 1px; }")
        self.volume.setObjectName("Task")
        self.volume.setGeometry(0, 0, 481, 41)

        self.line = QFrame(parent=self.volume)
        self.line.setGeometry(40, 0, 3, 41)
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")

        self.label = QLabel(parent=self.volume)
        self.label.setGeometry(58, 0, 390, 40)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")

        if not chapters:
            self.checkBox = QtWidgets.QCheckBox(parent=self.volume)
            self.checkBox.setText("")
            self.checkBox.setIconSize(QtCore.QSize(20, 20))
            self.checkBox.setChecked(False)
            self.checkBox.setObjectName("checkBox")
            self.checkBox.setGeometry(14, 13, 16, 16)
            self.label.setText(text)
            self.checkBox.clicked.connect(self.update_state)
            return

        self._text = text[1:]
        self.ext_chaps = self._text if ext_chaps is True else ext_chaps
        self._exp_len = len(self._text) * 30

        self.label.setText(text[0])

        self._dar = QtGui.QPixmap('images/d_arrow.png').scaled(16, 16)
        self._rar = QtGui.QPixmap('images/r_arrow.png').scaled(16, 16)
        self._arrow = ClickableLabel(parent=self.volume)
        self._arrow.clicked.connect(self.handle_arrow)
        self._arrow.setGeometry(14, 13, 16, 16)
        self._arrow.setPixmap(self._rar)
        self._arrow_clicked = False

        self.line2 = QFrame(parent=self.volume)
        self.line2.setGeometry(440, 0, 3, 41)
        self.line2.setFrameShape(QFrame.Shape.VLine)
        self.line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.line2.setObjectName("line")

        self.checkBox = QCheckBox(self.volume)
        self.checkBox.setCheckState(EMPTY)
        self.checkBox.setGeometry(454, 13, 16, 16)

        self.chapterWidgets = WidgetGrid(self.volume)
        self.chapterWidgets.setGridSize((1, len(self._text)))
        self.chapterWidgets.setChildSize((441, 30))
        self.chapterWidgets.move(39, 41)
        self.chapterWidgets.setHidden(True)
        if ext_chaps is True:
            self.checkBox.setCheckState(FULL)
            self.checkBox.setEnabled(False)
        self.generate_chaps()
        self.checkBox.clicked.connect(self.handle_volume_checkbox)

    def update_state(self):
        self.isChecked = self.checkBox.isChecked()

    def generate_chaps(self):
        for i in self._text:
            cpi = ChapterWigdet(self.chapterWidgets, i)
            self.chapterWidgets.addWidget(cpi)
            if i in self.ext_chaps:
                cpi.checkBox.setEnabled(False)
                cpi.checkBox.setChecked(True)
                continue
            cpi.checkBox.clicked.connect(self.upd_volume_checkbox)
            cpi.label.clicked.connect(self.upd_volume_checkbox)

    def expand_chaps(self):
        self.chapterWidgets.setHidden(False)
        self.volume.resize(self.volume.width(), self.volume.height() + self._exp_len)
        self.resize(self.width(), self.height() + self._exp_len)
        self._arrow.setPixmap(self._dar)
        self.delta_ex.emit(self._exp_len)

    def extract_chaps(self):
        self.chapterWidgets.setHidden(True)
        self.volume.resize(self.volume.width(), self.volume.height() - self._exp_len)
        self.resize(self.width(), self.height() - self._exp_len)
        self._arrow.setPixmap(self._rar)
        self.delta_ex.emit(-self._exp_len)

    def handle_arrow(self):
        if self._arrow_clicked:
            self.extract_chaps()
        else:
            self.expand_chaps()
        self._arrow_clicked = not self._arrow_clicked

    def upd_volume_checkbox(self):
        chaps_cb = [i.checkBox.isChecked() for i in self.chapterWidgets if i.checkBox.isEnabled()]
        if all(chaps_cb):
            self.checkBox.setCheckState(FULL)
        elif any(chaps_cb):
            self.checkBox.setCheckState(HALF)
        else:
            self.checkBox.setCheckState(EMPTY)

    def setAllChapterCB(self, state: bool):
        for i in self.chapterWidgets:
            if not i.checkBox.isEnabled():
                continue
            i.checkBox.setChecked(state)

    def handle_volume_checkbox(self):
        if not self.checkBox.isChecked():
            self.checkBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.setAllChapterCB(False)
        else:
            self.checkBox.setCheckState(QtCore.Qt.CheckState.Checked)
            self.setAllChapterCB(True)

    def handle_save_bt(self):
        if self.checkBox.checkState() == FULL:
            return self.label.text()
        if self.checkBox.checkState() == EMPTY and not self.ext_chaps:
            return None
        return [self.label.text()] + [i.label.text() for i in self.chapterWidgets if i.checkBox.isChecked()]


class VolumeWidget_R(QWidget):
    def __init__(self, text: str, parent=None, ratings: int = 0):
        super().__init__(parent)

        self.setGeometry(0, 0, 500, 40)
        self.rating = ratings

        self.volume = QFrame(self)
        self.volume.setStyleSheet(
            "#Task { border: 2px solid rgb(100, 100, 100); padding: 1px; }"
        )
        self.volume.setObjectName("Task")
        self.volume.setGeometry(0, 0, 481, 41)

        self.label = QLabel(parent=self.volume)
        self.label.setGeometry(8, 0, 320, 40)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setText(text)

        self.rt = Rtw(parent=self.volume, rating_=ratings)
        self.rt.move(365, 10)
        self.rt.rating_changed.connect(self.handle_rating_change)

        self.save_bt_vl = ClickableLabel(parent=self.volume, text=LANG['CTASK_save'])
        self.save_bt_vl.setGeometry(333, 0, 35, 40)
        self.save_bt_vl.setHidden(True)
        self.save_bt_vl.lclicked.connect(self.handle_save_bt)

        self.reset_bt_vl = ClickableLabel(parent=self.volume, text=LANG['CTASK_reset'])
        self.reset_bt_vl.setGeometry(295, 0, 35, 40)
        self.reset_bt_vl.lclicked.connect(self.handle_reset_bt)

    def handle_rating_change(self):
        self.save_bt_vl.setHidden(False)

    def handle_save_bt(self):
        self.save_bt_vl.setHidden(True)
        self.rating = self.rt.rating

    def handle_reset_bt(self):
        self.rt.set_rating(0)


class DetailedWindow(QDialog):
    Close_as_dia = Signal()

    def __init__(self, volume_details, chapters: bool = False, ratings: bool = False, bankinfo=None):
        """

        :param volume_details: [title, img_path, *volinfo]
        :param chapters: Bool. If the Chap-Win is rendered.
        :param ratings: Bool. If the Rating-Win is rendered.
        """
        if not volume_details:
            return
        super().__init__()

        self.setWindowTitle(LANG['CTASK_window'])
        self.setWindowIcon(QIcon("images/icon.ico"))
        self.setFixedSize(500, 700)
        self.setModal(True)
        self.renderChapters = chapters
        self.renderRatings = ratings
        self.emission: dict | list = []

        self.title_tx = volume_details[0]
        self.img_path = volume_details[1]
        self.volumes = volume_details[2:]

        self.scroll_area = ScrollField(self, None, (0, 50, 500, 600))

        self.DTtitle = TitleWidget(self.img_path, self.title_tx, parent=self)

        self.startFBT = QPushButton(parent=self)
        self.startFBT.setGeometry(410, 660, 80, 30)

        if not chapters and not ratings:
            self.SelectAll = QCheckBox(parent=self)
            self.SelectAll.setGeometry(14, 667, 100, 16)
            self.SelectAll.setText(LANG['CTASK_select_all'])
            self.SelectAll.clicked.connect(lambda: self.setAllState(self.SelectAll.isChecked()))

            self.text1 = QLabel(parent=self)
            self.text1.setGeometry(105, 660, 80, 30)
            self.text1.setText(LANG['CTASK_filename'])

            self.nameIP = QtWidgets.QLineEdit(parent=self)
            self.nameIP.setGeometry(170, 662, 210, 25)

            self.startFBT.setText(LANG['CTASK_form'])
            self.startFBT.clicked.connect(self.get_novel_state)

            self.generate_widget()
            return

        self.startFBT.setText(LANG['CFG_save'])
        self.startFBT.clicked.connect(self.save_quit_bt)
        if len(bankinfo) < 6:
            bankinfo.append(LUXINFO_TEMPLATE())
        self.bankinfo = bankinfo

        if chapters:
            self.generate_Cwidget()
            # Expansion Control.
            for i in range(len(self.scroll_area.widgets)):
                self.scroll_area[i].delta_ex.connect(lambda _el, idx=i: self.handle_expansion(idx, _el))
            return

        if ratings:
            self.generate_Rwidget()
            return

    def save_quit_bt(self):
        if self.renderRatings:
            rtg = dict()
            for i in self.scroll_area:
                i.handle_save_bt()
                if i.rating != 0:
                    rtg[i.label.text()] = i.rating
            self.emission = rtg
        if self.renderChapters:
            self.emission = [i.handle_save_bt() for i in self.scroll_area if i.handle_save_bt() is not None]
        self.Close_as_dia.emit()

    def generate_Rwidget(self):
        rts = self.bankinfo[5]['rtg']
        for i in self.volumes:
            rti = 0 if rts == 0 else rts.get(i, 0)
            self.scroll_area.addWidget(VolumeWidget_R(i, parent=None, ratings=rti))

    def generate_widget(self):
        for i in self.volumes:
            self.scroll_area.addWidget(VolumeWidget(i, None, self.renderChapters))

    @staticmethod
    def _get_prgi(vol, prg):
        if prg == 0:
            return None
        if vol[0] in prg:
            return True
        for j in prg:
            if j[0] == vol[0]:
                return j[1:]
        return None

    def generate_Cwidget(self):
        prg = self.bankinfo[5]['prg']
        for i in self.volumes:
            prgi = self._get_prgi(i, prg)
            self.scroll_area.addWidget(VolumeWidget(i, None, self.renderChapters, ext_chaps=prgi))

    def get_novel_state(self):
        return [i.isChecked for i in self.scroll_area]

    def setAllState(self, state: bool):
        for i in self.scroll_area:
            i.checkBox.setChecked(state)
            i.update_state()
        self.get_novel_state()

    def get_goal_filename(self):
        filename = self.nameIP.text()
        if not filename:
            print('Using Default Name!')
            return '112'
        return filename

    def handle_expansion(self, idx, _exp_len):
        for i in self.scroll_area[idx + 1:]:
            x, y = i.x(), i.y()
            i.move(x, y + _exp_len)
        self.scroll_area.expandMainWidget((0, _exp_len))


def activate1():
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    wd = DetailedWindow(['114514', 'images/thumbnails/1614.jpg', '1', '1', '3', '4', '5', '1', '1', '3', '4', '5', '1',
                         '1', '3', '4', '5', '1', '1', '3', '4', '5', '7'])
    wd.show()
    app.exec()


def activate2():
    print(get_default_name([1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 15, 16, 17, 19, 20, 21]))


def activate3():
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    wd = DetailedWindow(['114514', 'images/thumbnails/1614.jpg',
                         ['w', '1', '3', '4', '5', '1', '1', '3', '4'], ['f', '2', '3', '4', '5'],
                         ['q', '1', 'w', '4', '5'], ['e', 'b', '3', '4', '5']], chapters=True,
                        bankinfo=[
                            "1861",
                            "Re:从零开始的异世界生活",
                            "长月达平",
                            [
                                "穿越",
                                "战斗",
                                "冒险",
                                "后宫",
                                "人外"
                            ],
                            "MF文库J",
                            [['w', ['f', '3', '4'], 'q'], {}, 0]
                        ])
    wd.show()
    app.exec()


def activate4():
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    wd = DetailedWindow(['114514', 'images/thumbnails/1614.jpg', '1', '5', '3', '4', '6', '7'], ratings=True,
                        bankinfo=[
                            "1861",
                            "Re:从零开始的异世界生活",
                            "长月达平",
                            [
                                "穿越",
                                "战斗",
                                "冒险",
                                "后宫",
                                "人外"
                            ],
                            "MF文库J",
                            {'prg': [], 'rtg': {'1': 4}, 'fav': 0, 'lck': ''}
                        ])
    wd.show()
    app.exec()


if __name__ == "__main__":
    activate3()
