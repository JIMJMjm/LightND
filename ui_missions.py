import json
import os
import time
from functools import partial

import requests as rq
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QVBoxLayout, QWidget, QDialog, QScrollArea, QPushButton, QLineEdit, QHBoxLayout
from bs4 import BeautifulSoup as bs

from BySide import ClickableLabel
from config import confirm_name

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 '
                  'Safari/537.36'}

exist = os.path.exists


def save_json(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        # noinspection PyTypeChecker
        json.dump(content, f, indent=4, ensure_ascii=False)
    return 0


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


class TaskWidget(QWidget):
    def __init__(self, numname, pos: tuple, parent=None):
        super().__init__(parent)

        numname = str(numname)

        self.numname, self.name = get_info(numname)
        self.image_path = get_img(numname)

        x, y = pos
        self.setGeometry(x, y, 481, 61)

        self.Task = QtWidgets.QFrame(self)
        self.Task.setStyleSheet(
            "#Task { border: 2px solid rgb(218, 182, 183); padding: 5px; }"
        )
        self.Task.setObjectName("Task")
        self.Task.setGeometry(0, 0, 481, 61)

        self.Thumbnail = QtWidgets.QLabel(parent=self.Task)
        self.Thumbnail.setGeometry(QtCore.QRect(2, 2, 51, 57))
        if 'byte' not in str(type(self.image_path)):
            self.Thumbnail.setPixmap(QtGui.QPixmap(self.image_path).scaled(51, 57))
        else:
            pm = QtGui.QPixmap()
            pm.loadFromData(self.image_path)
            self.Thumbnail.setPixmap(pm.scaled(51, 57))
        self.Thumbnail.setObjectName("Thumbnail")

        self.Name = QtWidgets.QLabel(parent=self.Task)
        self.Name.setGeometry(QtCore.QRect(60, 10, 321, 21))
        font = QtGui.QFont()
        font.setFamily("宋体")
        self.Name.setFont(font)
        self.Name.setObjectName("Name")
        self.Name.setText(self.name)

        self.AddCheck = ClickableLabel(parent=self.Task)
        self.AddCheck.setGeometry(QtCore.QRect(60, 39, 99, 16))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setUnderline(True)
        self.AddCheck.setFont(font)
        self.AddCheck.setObjectName("AddCheck")
        self.AddCheck.setText("+Checklist")

        self.DL_button = ClickableLabel(parent=self.Task)
        self.DL_button.setGeometry(QtCore.QRect(400, 12, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setUnderline(True)
        self.DL_button.setFont(font)
        self.DL_button.setObjectName("label")
        self.DL_button.setText("Download")

        self.remove_button = QPushButton(parent=self.Task)
        self.remove_button.setGeometry(QtCore.QRect(158, 39, 16, 16))
        self.remove_button.setText('-')

        self.ProgessBar = QtWidgets.QProgressBar(parent=self.Task)
        self.ProgessBar.setGeometry(QtCore.QRect(190, 37, 281, 20))
        self.ProgessBar.setProperty("value", 0)
        self.ProgessBar.setTextVisible(True)
        self.ProgessBar.setObjectName("ProgessBar")

    def delete(self):
        self.setParent(None)
        self.deleteLater()


class UPDWidget(QWidget):
    def __init__(self, numname, pos: tuple, parent=None):
        super().__init__(parent)

        numname = str(numname)

        self.numname, self.name = get_info(numname)
        self.image_path = get_img(numname)

        x, y = pos
        self.setGeometry(x, y, 481, 61)

        self.Task = QtWidgets.QFrame(self)
        self.Task.setStyleSheet(
            "#Task { border: 2px solid rgb(218, 182, 183); padding: 5px; }"
        )
        self.Task.setObjectName("Task")
        self.Task.setGeometry(0, 0, 481, 61)

        self.Thumbnail = QtWidgets.QLabel(parent=self.Task)
        self.Thumbnail.setGeometry(QtCore.QRect(2, 2, 51, 57))
        if 'byte' not in str(type(self.image_path)):
            self.Thumbnail.setPixmap(QtGui.QPixmap(self.image_path).scaled(51, 57))
        else:
            pm = QtGui.QPixmap()
            pm.loadFromData(self.image_path)
            self.Thumbnail.setPixmap(pm.scaled(51, 57))
        self.Thumbnail.setObjectName("Thumbnail")

        self.Name = QtWidgets.QLabel(parent=self.Task)
        self.Name.setGeometry(QtCore.QRect(60, 10, 321, 21))
        font = QtGui.QFont()
        font.setFamily("宋体")
        self.Name.setFont(font)
        self.Name.setObjectName("Name")
        self.Name.setText(self.name)

        self.AddCheck = ClickableLabel(parent=self.Task)
        self.AddCheck.setGeometry(QtCore.QRect(60, 39, 93, 16))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setUnderline(True)
        self.AddCheck.setFont(font)
        self.AddCheck.setObjectName("Check")
        self.AddCheck.setText("Check Update")
        # self.AddCheck.clicked.connect(lambda: print(1))

        self.DL_Button = ClickableLabel(parent=self.Task)
        self.DL_Button.setGeometry(QtCore.QRect(400, 12, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setUnderline(True)
        self.DL_Button.setFont(font)
        self.DL_Button.setObjectName("label")
        self.DL_Button.setText("Download")

        self.remove_button = QPushButton(parent=self.Task)
        self.remove_button.setGeometry(QtCore.QRect(158, 39, 16, 16))
        self.remove_button.setText('-')

        self.ProgessBar = QtWidgets.QProgressBar(parent=self.Task)
        self.ProgessBar.setGeometry(QtCore.QRect(190, 37, 281, 20))
        self.ProgessBar.setProperty("value", 0)
        self.ProgessBar.setTextVisible(True)
        self.ProgessBar.setObjectName("ProgessBar")

    def delete(self):
        self.setParent(None)
        self.deleteLater()


class AskWindow(QDialog):
    confirm = Signal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Number Input Dialog")
        self.setFixedSize(300, 100)

        main_layout = QVBoxLayout(self)

        input_layout = QHBoxLayout()

        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText("Numname 0-9999")
        self.number_input.setValidator(QIntValidator(0, 9999, self))
        self.number_input.setMaximumWidth(150)

        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.setMaximumWidth(100)

        input_layout.addWidget(self.number_input)
        input_layout.addWidget(self.confirm_button)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(input_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def confirm_action(self):
        value = self.number_input.text()
        if value.isdigit():
            print(f"Confirmed value: {value}")
            self.confirm.emit(int(value))
            self.number_input.clear()
        else:
            print("Invalid input!")
        self.close()


def get_img(numname, iis=False):
    if exist(f'images/thumbnails/{numname}.jpg'):
        return f'images/thumbnails/{numname}.jpg'
    url = f'https://img.wenku8.com/image/{int(numname) // 1000}/{numname}/{numname}s.jpg'
    imagee = rq.get(url, headers=header)
    time.sleep(0.03)
    m = imagee.content
    with open(f'images/thumbnails/{numname}.jpg', 'wb') as f:
        f.write(m)
    if iis:
        return f'images/thumbnails/{numname}.jpg'
    return m


def get_info(numname):
    modl = numname[0]
    if len(numname) <= 3:
        modl = '0'
    r0 = rq.get(f'https://www.wenku8.cc/novel/{modl}/{numname}/index.htm', headers=header)
    r0.encoding = 'GBK'
    sp = bs(r0.text, 'html.parser')
    name = sp.find('div', id='title').text
    name = confirm_name(name)
    return numname, name


class CheckWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check List")
        self.setFixedSize(500, 640)
        self.setModal(False)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.askwindow = AskWindow()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(1, 0, 500, 600))
        self.scroll_content = QWidget()

        self.add_button = QPushButton("Add New Novel", self)
        self.add_button.setGeometry(30, 605, 115, 30)

        self.now_y = 540
        self.val_got = 0

        self.tasks = []
        self.checklist = read_json('checklist.json')

        self.valuelist = [int(i[0]) for i in self.checklist]
        self.cover_url = ''

        self.scroll_content.setGeometry(0, 0, 480, self.now_y)
        self.scroll_area.setWidget(self.scroll_content)

        self.askwindow.confirm_button.clicked.connect(self.askwindow.confirm_action)
        self.askwindow.confirm.connect(self.handle_value)

    def add_task_wid(self, numname, pos=(0, 0)):
        self.tasks.append(UPDWidget(numname, pos=pos, parent=self.scroll_content))

    def render_checklist(self):
        self.scroll_content.update()
        for e, i in enumerate(self.checklist):
            self.add_task_wid(numname=i[0], pos=(0, e * 60))

        for i in range(len(self.tasks)):
            currtsk = self.tasks[i]
            '''
            try:
                currtsk.remove_button.clicked.disconnect()
            except RuntimeError or RuntimeWarning:
                pass
            '''
            currtsk.remove_button.clicked.connect(partial(self.refresh_checklist, currtsk))

    def refresh_checklist(self, target: UPDWidget = None):
        if not target:
            self.checklist.append([str(self.val_got), self.tasks[-1].name])
            self.valuelist = [int(i[0]) for i in self.checklist]
            save_json('checklist.json', self.checklist)
            self.tasks[-1].AddCheck.clicked.connect(lambda: print(self.tasks[-1].numname))
            return

        mode = self.tasks.index(target)
        curtsk: UPDWidget = self.tasks.pop(mode)
        curtsk.delete()
        self.checklist.pop(mode)
        self.valuelist = [int(i[0]) for i in self.checklist]
        save_json('checklist.json', self.checklist)
        for e, task in enumerate(self.tasks[mode:]):
            task.move(0, (mode + e) * 60)

    def handle_value(self, value):
        self.val_got = value
        if self.val_got in self.valuelist:
            print('Already Added!')
            return

        poss = (0, len(self.tasks) * 60)
        if len(self.tasks) * 60 >= self.now_y:
            self.now_y += 60
            self.scroll_content.setGeometry(0, 0, 480, self.now_y)

        new_w = UPDWidget(self.val_got, poss, self.scroll_content)
        self.tasks.append(new_w)
        self.refresh_checklist()
        new_w.show()

    def test(self):
        for i in self.tasks:
            print(i.numname)


class TaskWindow(QDialog):
    return_todolist = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task List")
        self.setFixedSize(500, 640)
        self.setModal(False)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.askwindow = AskWindow()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(QtCore.QRect(1, 0, 500, 600))
        self.scroll_content = QWidget()

        self.add_button = QPushButton("Add New Novel", self)
        self.add_button.setGeometry(30, 605, 115, 30)

        self.now_y = 540
        self.val_got = 0

        self.tasks = []
        self.todolist = []
        self.valuelist = [int(i) for i in self.todolist]
        self.cover_url = ''

        self.scroll_content.setGeometry(0, 0, 480, self.now_y)
        self.scroll_area.setWidget(self.scroll_content)

        # noinspection PyUnresolvedReferences
        self.askwindow.confirm_button.clicked.connect(self.askwindow.confirm_action)
        self.askwindow.confirm.connect(self.handle_value)

    def add_task_wid(self, numname, pos=(0, 0)):
        self.tasks.append(TaskWidget(numname, pos=pos, parent=self.scroll_content))

    def render_tasklist(self, todolist):
        self.scroll_content.update()
        for e, i in enumerate(todolist):
            self.add_task_wid(numname=i, pos=(0, e * 60))

        for i in range(len(self.tasks)):
            currtsk = self.tasks[i]
            try:
                currtsk.remove_button.clicked.disconnect()
            except RuntimeError:
                pass
            currtsk.remove_button.clicked.connect(partial(self.refresh_checklist, currtsk))

    def refresh_checklist(self, target: TaskWidget = None):
        if not target:
            self.todolist.append(str(self.val_got))
            self.valuelist = [int(i) for i in self.todolist]
            self.return_todolist.emit()
            self.tasks[-1].AddCheck.clicked.connect(lambda: print(self.tasks[-1].numname))
            return

        mode = self.tasks.index(target)
        curtsk: TaskWidget = self.tasks.pop(mode)
        curtsk.delete()
        self.todolist.pop(mode)
        self.valuelist = [int(i) for i in self.todolist]
        for e, task in enumerate(self.tasks[mode:]):
            task.move(0, (mode + e) * 60)

    def handle_value(self, value):
        self.val_got = value
        if self.val_got in self.valuelist:
            print('Already Added!')
            return

        poss = (0, len(self.tasks) * 60)
        if len(self.tasks) * 60 >= self.now_y:
            self.now_y += 60
            self.scroll_content.setGeometry(0, 0, 480, self.now_y)
        new_w = TaskWidget(self.val_got, poss, self.scroll_content)
        self.tasks.append(new_w)
        self.refresh_checklist()
        new_w.show()

    def test(self):
        for i in self.tasks:
            print(i.numname)
