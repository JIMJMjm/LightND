import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QProgressBar, QDialog

from BySide import DefaultFont, ScrollField
from config import LANG

INDEX = 0


class TaskWidget(QWidget):
    def __init__(self, bankinfo: list, task_type: str, uid: int, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 150)
        self.numname, self.name = bankinfo[:2]

        self.thumb = QLabel(self)
        self.uid = uid
        self.thumb.setPixmap(QPixmap(f'images/thumbnails/{self.numname}.jpg').scaled(100, 150))

        self.task_type = task_type
        type_text = ''

        if self.task_type == 'TEXTER':
            type_text = LANG['TASK_type_TEXTER']
        elif self.task_type == 'DNLDER':
            type_text = LANG['TASK_type_DOWNLOADER']
        elif self.task_type == 'EPUBER':
            type_text = LANG['TASK_type_EPUB']
        type_text += ':'

        self.type_label = QLabel(self)
        self.type_label.setGeometry(108, 74, 115, 34)
        self.type_label.setText(type_text)
        self.type_label.setFont(DefaultFont(size=11))
        # self.type_label.setStyleSheet("QLabel { border: 3px solid rgba(255, 255, 180, 255);}")

        self.name_label = QLabel(self)
        self.name_label.setGeometry(110, 0, 480, 50)
        self.name_label.setWordWrap(True)
        self.name_label.setText(self.name)
        self.name_label.setFont(DefaultFont(size=12, bold=True))

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(220, 98, 370, 22)
        self.progress_bar.setRange(0, 100)
        # self.progress_bar.setValue(50)
        self.progress_bar.setTextVisible(False)
        # self.progress_bar.setStyleSheet("QProgressBar { border: 3px solid rgba(255, 255, 180, 255);}")

        self.state_label = QLabel(self)
        self.state_label.setGeometry(220, 65, 370, 30)
        self.state_label.setFont(DefaultFont(size=13))
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.state_label.setText('12452345235463456')
        # self.state_label.setStyleSheet("QLabel { border: 3px solid rgba(255, 255, 180, 255);}")

    def setTextState(self, text: str):
        self.state_label.setText(text)

    def setProgressValue(self, value: int):
        self.progress_bar.setValue(value)

    def setCurrentState(self, state: tuple[str, int]):
        self.progress_bar.setValue(state[1])
        self.state_label.setText(state[0])


class TestWidget(QLabel):
    def __init__(self, num=0):
        super().__init__(text=str(num))

        self.setGeometry(0, 0, 600, 150)

        self.setFont(DefaultFont(size=16))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet('QLabel { border: 1px solid black; }')


class MissionWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(620, 800)
        self.setWindowTitle(LANG['MIS_Window'])
        self.setWindowIcon(QIcon('images/icon.ico'))

        self.tasklist = []

        self.scroll = ScrollField(parent=self, widgets=[], Geometry=(0, 0, 620, 800))
        self.scroll.widget_size[0] = 600

    def form_task_widget(self, task_list: list[list]):
        for i in task_list:
            self.addTask(i)

    def clearWidgets(self):
        for i in self.scroll.widgets:
            i.setParent(None)

    def refresh_list(self):
        ind = []
        for y, i in self.scroll.widgets:
            if i.progress_bar.value() == 100:
                ind.append(i.uid)
                self.scroll.removeWidget(y)

        for i in self.tasklist:
            if i[-1] in ind:
                self.tasklist.remove(i)

    def addTask(self, task: list):
        global INDEX
        self.tasklist.append(list(task) + [INDEX])
        self.scroll.addWidget(TaskWidget(bankinfo=task[:2], task_type=task[-1], uid=INDEX))
        INDEX += 1


def activate():
    app = QApplication([])
    window = TaskWidget(
        bankinfo=['3057', '关于我在无意间被隔壁的天使变成废柴这件事(关于邻家的天使大人不知不觉把我惯成了废人这档子事)'],
        task_type='TEXTER', uid=1)
    window.show()
    sys.exit(app.exec())


def activate2():
    app = QApplication([])
    window = MissionWindow()
    window.addTask(
        ['3057', '关于我在无意间被隔壁的天使变成废柴这件事(关于邻家的天使大人不知不觉把我惯成了废人这档子事)',
         'TEXTER'])
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    activate2()
