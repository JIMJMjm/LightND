from os.path import exists as ext

from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QDialog, QFrame, QWidget, QLabel, QPushButton, QCheckBox

from BySide import ScrollField, DefaultFont, ClickableLabel
from rating import StarRatingWidget

DFont = DefaultFont(14)
SFont = DefaultFont()
XSFont = DefaultFont(10).setFont('Microsoft YaHei')


class BookTitle(QWidget):
    def __init__(self, numname, bookname, parent=None):
        super().__init__(parent)
        self.setFixedSize(550, 80)
        self.bknm_label = QLabel(parent=self)
        self.bknm_label.setText(bookname)
        self.bknm_label.setGeometry(68, 0, 482, 50)
        self.bknm_label.setFont(DFont)
        self.bknm_label.setWordWrap(True)

        self.thm_label = QLabel(parent=self)
        self.thm_label.setGeometry(0, 0, 52, 80)

        if ext(f'images/thumbnails/{numname}.jpg'):
            self.thm_label.setPixmap(QPixmap(f'images/thumbnails/{numname}.jpg').scaled(52, 80))
        else:
            self.thm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.thm_label.setText('?')


class PrgChapterWidget(QWidget):
    aclick = Signal()

    def __init__(self, name, clickable: bool, parent=None):
        super().__init__(parent)
        self.fr_b = QFrame(self)
        self.fr_b.setGeometry(40, 0, 451, 30)
        self.fr_b.setStyleSheet("QFrame { border: 1px solid rgb(120, 120, 120); }")

        self.setFixedSize(530, 30)
        self.isChecked = not clickable
        self.name = name

        self.label = ClickableLabel(parent=self, pic=(219, 112, 147, 154))
        self.label.setText(name)
        self.label.setFont(XSFont)
        self.label.setGeometry(40, 0, 451, 30)

        self.checkBox = QCheckBox(self)
        self.checkBox.setGeometry(504, 8, 16, 16)
        self.checkBox.setChecked(self.isChecked)
        self.checkBox.setEnabled(clickable)

        if clickable:
            self.label.lclicked.connect(self.handleClicked)
            self.checkBox.clicked.connect(self.handleClicked)

    def setClickState(self, state: bool):
        self.isChecked = state
        self.checkBox.setChecked(state)

    def handleClicked(self):
        self.setClickState(not self.isChecked)
        self.aclick.emit()


class RtgWidget(QWidget):
    def __init__(self, name: str, clickable: bool, rating: float = 0.0, parent=None):
        super().__init__(parent)
        self.fr_b = QFrame(self)
        self.fr_b.resize(530, 40)
        self.fr_b.setStyleSheet("QFrame { border: 1px solid rgb(120, 120, 120); }")

        self.setFixedSize(530, 40)
        self.name = name

        self.label = QLabel(parent=self)
        self.label.setText(name)
        self.label.setFont(SFont)
        self.label.setGeometry(15, 0, 395, 40)

        self.ratings = StarRatingWidget(self, rating_=rating, click=clickable)
        self.ratings.move(410, 10)
        if clickable:
            self.reset_btn = ClickableLabel(self)
            self.reset_btn.setGeometry(358, 0, 45, 40)
            self.reset_btn.setFont(SFont)
            self.reset_btn.setText('Reset')
            self.reset_btn.lclicked.connect(lambda: self.ratings.set_rating(0))

    @property
    def rating(self) -> float:
        return self.ratings.rating


class PrgWidget(QWidget):
    stretch = Signal(tuple)

    def __init__(self, data: list | str, clickable: bool, parent=None):
        super().__init__(parent)
        self.fr_b = QFrame(self)
        self.fr_b.resize(530, 40)
        self.fr_b.setStyleSheet("QFrame { border: 1px solid rgb(120, 120, 120); }")
        self.resize(530, 40)
        self.isChecked = False
        self.isClickable = clickable
        self.data = data

        self._dar = QPixmap('images/d_arrow.png').scaled(16, 16)
        self._rar = QPixmap('images/r_arrow.png').scaled(16, 16)

        if isinstance(data, str):
            self.str_widget(data)
        else:
            self.list_widget(data)

    def str_widget(self, name: str):
        self.label = QLabel(parent=self)
        self.label.setGeometry(58, 0, 440, 40)
        self.label.setFont(SFont)
        self.label.setWordWrap(True)
        self.label.setText(name)

        self.checkBox = QCheckBox(self)
        self.checkBox.setEnabled(False)
        self.checkBox.setChecked(True)
        self.checkBox.setGeometry(504, 13, 16, 16)

    def list_widget(self, names: list):
        self.label = QLabel(parent=self)
        self.label.setGeometry(58, 0, 440, 40)
        self.label.setFont(SFont)
        self.label.setWordWrap(True)
        self.label.setText(names[0])

        self.line1 = QFrame(parent=self)
        self.line1.setGeometry(40, 0, 2, 40)
        self.line1.setFrameShape(QFrame.Shape.VLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)
        self.line1.setObjectName("line")

        self.line2 = QFrame(parent=self)
        self.line2.setGeometry(490, 0, 2, 40)
        self.line2.setFrameShape(QFrame.Shape.VLine)
        self.line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.line2.setObjectName("line")

        self.checkBox = QCheckBox(self)
        self.checkBox.setEnabled(self.isClickable)
        self.checkBox.setChecked(not self.isClickable)
        self.checkBox.setGeometry(504, 13, 16, 16)
        if self.isClickable:
            self.checkBox.setTristate()
            self.checkBox.setCheckState(Qt.CheckState.Unchecked)
            self.checkBox.clicked.connect(self.handleCheckBoxClicked)

        self._arrow = ClickableLabel(parent=self)
        self._arrow.setGeometry(14, 13, 16, 16)
        self._arrow.setPixmap(self._rar)
        self._arrow_clicked = False

        self.chapter_list = []
        for y, i in enumerate(names[1:]):
            pcw = PrgChapterWidget(i, clickable=self.isClickable, parent=self)
            pcw.setHidden(True)
            pcw.move(0, 40 + y * 30)
            self.chapter_list.append(pcw)
        for i in self.chapter_list:
            i.checkBox.setEnabled(self.isClickable)
            i.checkBox.setChecked(not self.isClickable)
            i.aclick.connect(self.update_checkstate)
        self.delta_x = len(self.chapter_list) * 30

        self._arrow.lclicked.connect(lambda: self.stretch_widget(not self._arrow_clicked))

    def stretch_widget(self, t: bool):
        if t:
            self.resize(530, 40 + self.delta_x)
            self.fr_b.resize(530, 40 + self.delta_x)
            for i in self.chapter_list:
                i.setHidden(False)
        else:
            self.resize(530, 40)
            self.fr_b.resize(530, 40)
            for i in self.chapter_list:
                i.setHidden(True)

        self._arrow_clicked = not self._arrow_clicked
        self._arrow.setPixmap(self._dar if self._arrow_clicked else self._rar)
        self.stretch.emit((t, self.delta_x))

    def update_checkstate(self):
        states = [i.isChecked for i in self.chapter_list]
        if all(states):
            self.checkBox.setCheckState(Qt.CheckState.Checked)
        elif any(states):
            self.checkBox.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            self.checkBox.setCheckState(Qt.CheckState.Unchecked)

    def handleCheckBoxClicked(self):
        if not self.checkBox.isChecked():
            self.checkBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
            ck = False
        else:
            self.checkBox.setCheckState(QtCore.Qt.CheckState.Checked)
            ck = True
        for i in self.chapter_list:
            if not i.checkBox.isEnabled():
                continue
            i.setClickState(ck)

    @property
    def reading(self) -> list:
        return (([self.data[0]]
                 if self.checkBox.checkState() != QtCore.Qt.CheckState.Unchecked else [])
                + ([i.name for i in self.chapter_list if i.isChecked]
                   if self.checkBox.checkState() == QtCore.Qt.CheckState.PartiallyChecked else []))


class RmzImportWindow(QDialog):
    prg_save = Signal(list)
    rtg_save = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setupBasicUi()

    def setupBasicUi(self):
        self.setWindowTitle("Import RMZ")
        self.setFixedSize(1100, 820)

        self.prg_scr_old = ScrollField(parent=self)
        self.prg_scr_old.widget_size = [530, 0]
        self.prg_scr_old.setGeometry(0, 80, 550, 355)

        self.rtg_scr_old = ScrollField(parent=self)
        self.rtg_scr_old.widget_size = [530, 0]
        self.rtg_scr_old.setGeometry(0, 465, 550, 355)

        self.prg_scr_new = ScrollField(parent=self)
        self.prg_scr_new.widget_size = [530, 0]
        self.prg_scr_new.setGeometry(550, 80, 550, 355)

        self.rtg_scr_new = ScrollField(parent=self)
        self.rtg_scr_new.widget_size = [530, 0]
        self.rtg_scr_new.setGeometry(550, 465, 550, 355)

        self.line1 = QFrame(parent=self)
        self.line1.setGeometry(549, 0, 2, 840)
        self.line1.setFrameShape(QFrame.Shape.VLine)
        self.line1.setFrameShadow(QFrame.Shadow.Sunken)
        self.line1.setObjectName("line1")

        self.line2 = QFrame(parent=self)
        self.line2.setGeometry(53, 50, 497, 2)
        self.line2.setFrameShape(QFrame.Shape.HLine)
        self.line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.line2.setObjectName("line2")

        self.line3 = QFrame(parent=self)
        self.line3.setGeometry(603, 50, 497, 2)
        self.line3.setFrameShape(QFrame.Shape.HLine)
        self.line3.setFrameShadow(QFrame.Shadow.Sunken)
        self.line3.setObjectName("line3")

        self.label1 = QLabel(self)
        self.label1.setGeometry(55, 50, 440, 30)
        self.label1.setFont(SFont)
        self.label1.setText('Current Reading progress')
        self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label2 = QLabel(self)
        self.label2.setGeometry(550, 50, 550, 30)
        self.label2.setFont(SFont)
        self.label2.setText('Imported Reading progress')
        self.label2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label3 = QLabel(self)
        self.label3.setGeometry(55, 425, 440, 50)
        self.label3.setFont(SFont)
        self.label3.setText('Current Ratings')
        self.label3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label4 = QLabel(self)
        self.label4.setGeometry(550, 425, 550, 50)
        self.label4.setFont(SFont)
        self.label4.setText('Imported Ratings')
        self.label4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_prg = QPushButton(self)
        self.save_prg.setGeometry(498, 50, 52, 31)
        self.save_prg.setFont(SFont)
        self.save_prg.setText('Save')

        self.save_rtg = QPushButton(self)
        self.save_rtg.setGeometry(498, 434, 52, 32)
        self.save_rtg.setFont(SFont)
        self.save_rtg.setText('Save')

    def setupLuxUi(self):
        self.title_old = BookTitle(self.hmzinfo['numname'], self.hmzinfo['name'], parent=self)
        self.title_old.move(0, 0)

        self.title_new = BookTitle(self.rmz[0], self.rmz[1], parent=self)
        self.title_new.move(550, 0)

        prg_old = self.hmzinfo['allname']
        self.generateScrollContent('prg_old', prg_old)

        rtg_old = [i[0] for i in self.hmzinfo['allname']]
        self.generateScrollContent('rtg_old', rtg_old)

        prg_new = self.rmz[-1]['prg']
        self.generateScrollContent('prg_new', prg_new)

        rtg_new = self.rmz[-1]['rtg']
        self.generateScrollContent('rtg_new', rtg_new)

        self.save_rtg.raise_()
        self.save_prg.raise_()

        self.save_rtg.clicked.connect(self.handleRtgSave)
        self.save_prg.clicked.connect(self.handlePrgSave)
        #
        # self.rtg_save.connect(lambda con: print(con))
        # self.prg_save.connect(lambda con: print(con))

    def generateScrollContent(self, _type: str, data: list[str | list] | dict[str: str | int]):
        if _type == 'prg_old':
            for i in data:
                self.prg_scr_old.addWidget(PrgWidget(i, clickable=True))

            for y, i in enumerate(self.prg_scr_old.widgets):
                i.stretch.connect(lambda indicator, list_='old', index=y:
                                  self.prg_widget_connection(index, list_, indicator))
        if _type == 'prg_new':
            for i in data:
                self.prg_scr_new.addWidget(PrgWidget(i, clickable=False))

            for y, i in enumerate(self.prg_scr_new.widgets):
                i.stretch.connect(lambda indicator, list_='new', index=y:
                                  self.prg_widget_connection(index, list_, indicator))
        if _type == 'rtg_old':
            for i in data:
                self.rtg_scr_old.addWidget(RtgWidget(name=i, clickable=True))
        if _type == 'rtg_new':
            for i, j in zip(data.keys(), data.values()):
                self.rtg_scr_new.addWidget(RtgWidget(name=i, clickable=False, rating=j))

    def prg_widget_connection(self, y: int, _t: str, indicator: tuple):
        if _t == 'old':
            x_1, y_1 = self.prg_scr_old.mainwidget.size().toTuple()
            for i in self.prg_scr_old[y + 1:]:
                x_c, y_c = i.pos().toTuple()
                if indicator[0]:
                    i.move(x_c, y_c + indicator[1])
                else:
                    i.move(x_c, y_c - indicator[1])
            if indicator[0]:
                self.prg_scr_old.mainwidget.resize(x_1, y_1 + indicator[1])
            else:
                self.prg_scr_old.mainwidget.resize(x_1, y_1 - indicator[1])

        if _t == 'new':
            x_1, y_1 = self.prg_scr_new.mainwidget.size().toTuple()
            for i in self.prg_scr_new[y + 1:]:
                x_c, y_c = i.pos().toTuple()
                if indicator[0]:
                    i.move(x_c, y_c + indicator[1])
                else:
                    i.move(x_c, y_c - indicator[1])
            if indicator[0]:
                self.prg_scr_new.mainwidget.resize(x_1, y_1 + indicator[1])
            else:
                self.prg_scr_new.mainwidget.resize(x_1, y_1 - indicator[1])

    def initData(self, rmz: list[str | dict], hmzinfo: dict):
        """
        :param rmz: Requires at least empty Luxury data.
        :param hmzinfo:
        :return:
        """
        self.hmzinfo = hmzinfo
        self.rmz = rmz

        self.setupLuxUi()

    def handlePrgSave(self):
        prg = []
        for i in self.prg_scr_old.widgets:
            if p1 := i.reading:
                prg.append(p1)
        self.prg_save.emit(prg)

    def handleRtgSave(self):
        rtg = {}
        for i in self.rtg_scr_old.widgets:
            if r1 := i.rating:
                rtg[i.name] = r1
        self.rtg_save.emit(rtg)


def activate():
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    rmz = RmzImportWindow()
    rmz.initData(rmz=[
        "183",
        "CLANNAD官方外传小说",
        "麻枝准",
        [
            "校园",
            "青春",
            "恋爱"
        ],
        "电击文库",
        {
            "prg": [
                ["～被光守护的坂道上～", '1', '2'],
                "Another Story"
            ],
            "rtg": {
                "～被光守护的坂道上～": 8,
                "Another Story": 8
            },
            "fav": False,
            "lck": "2025/07/24 18:20:04"
        }
    ], hmzinfo={
        "name": "CLANNAD官方外传小说",
        "writer": "麻枝准",
        "allnet": [
            [
                "～被光守护的坂道上～",
                "8123.htm",
                "8124.htm",
                "8125.htm",
                "8126.htm",
                "8127.htm",
                "8128.htm",
                "8129.htm",
                "8130.htm",
                "8131.htm",
                "8132.htm",
                "8133.htm",
                "8134.htm",
                "8136.htm",
                "8138.htm",
                "8139.htm",
                "8150.htm"
            ],
            [
                "Another Story",
                "8135.htm",
                "8143.htm",
                "8142.htm",
                "19510.htm"
            ]
        ],
        "allname": [
            [
                "～被光守护的坂道上～",
                "第一话 拿出勇气吧",
                "第二话 连衣裙",
                "第三话 男性朋友们",
                "第四话 那个时候的我",
                "第五话 公子的日记",
                "第六话 心跳加速的瞬间",
                "第七话 特别的夜晚",
                "第八话 我的哥哥",
                "第九话 各式各样的味道",
                "第十话 咒语的秘密",
                "第十一话 二人的回忆",
                "第十二话 老师的回忆",
                "第十三话 四年前的因缘",
                "特别篇 古河面包师再结成",
                "第十五话 大家在澡堂",
                "第十六话 城镇的思念"
            ],
            [
                "Another Story",
                "1 她的境界线",
                "2 尾巴王国的琴美",
                "3 风子小宇宙",
                "后记"
            ]
        ],
        "directory": "D:/ACGN/Novel",
        "discription": "关于我们的渚的一次细微的，命中注定的某次事件的故事一年后。\n她与“后辈”冈崎朋也相遇，然后相恋这次讲的则是之前的一段小插曲。\n"
                       "内容是，游戏的本篇中没有提及到的渚和朋也各自的过去两人之间发生过了什么。\n在洒满春光的校园中向我们敞开的，是CLANNAD的另一扇门。",
        "genre": [
            "校园",
            "青春",
            "恋爱"
        ],
        "bunko": "电击文库",
        "numname": "183"
    })
    rmz.show()
    app.exec()


if __name__ == '__main__':
    activate()
