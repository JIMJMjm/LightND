from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent, QFont
from PySide6.QtWidgets import QLabel, QButtonGroup, QScrollArea, QWidget, QPushButton, QCheckBox


def extand_list_to(lis, a, b):
    if not lis:
        return [[0] * a for _ in range(b)]
    la = len(lis[0]) if lis else 0
    lb = len(lis)
    if a > la:
        for row in lis:
            row += [0] * (a - la)
    if b > lb:
        for _ in range(b - lb):
            lis.append([0] * a)
    return lis


class ClickableLabel(QLabel):
    lclicked = Signal()
    rclicked = Signal()
    clicked = lclicked

    def __init__(self, parent=None, text="", pic: tuple | bool = False):
        super().__init__(text, parent)
        self.setText(text)
        effect = """
        QLabel {
            color: black;
        }
        QLabel:hover {
            color: blue;  
        }
        """
        eff_pic = '''QLabel { border: 3px solid transparent; }
            QLabel:hover { border: 3px solid rgba''' + str(pic) + '''; }'''

        if pic:
            self.setStyleSheet(eff_pic)
        else:
            self.setStyleSheet(effect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lclicked.emit()
        if event.button() == Qt.MouseButton.RightButton:
            self.rclicked.emit()
        super().mousePressEvent(event)


class DPushButton(QPushButton):
    rclicked = Signal(int)
    lclicked = Signal(int)

    def __init__(self, parent=None, text=""):
        super().__init__(text, parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.rclicked.emit(1)
        if event.button() == Qt.MouseButton.LeftButton:
            self.lclicked.emit(0)
        super().mousePressEvent(event)


class AdvButtonGroup(QButtonGroup):
    def __init__(self, parent=None, exclusive: bool = True, buttons=None):
        super().__init__(parent)

        if buttons is None:
            buttons = []

        self.isExclusive = exclusive
        self.buttons = buttons

        self.setExclusive(self.isExclusive)

        for i in self.buttons:
            self.addButton(i)

    def __getitem__(self, item):
        return self.buttons[item]

    def AddButtons(self, buttons: list):
        for i in buttons:
            self.addButton(i)


class ScrollField(QScrollArea):
    def __init__(self, parent=None, widgets=None, Geometry=None):
        super().__init__(parent)

        if widgets is None:
            widgets = []
        if Geometry is None:
            Geometry = [0, 0, 0, 0]

        self.widgets = widgets
        self.mainwidget = QWidget()
        self.setGeometry(*Geometry)  # NOQA
        self.Geometry = Geometry
        self.setWidget(self.mainwidget)

        self.widget_size = [0, 0]
        for y, i in enumerate(self.widgets):
            i.setParent(self)
            size = i.size().toTuple()
            i.move(0, self.widget_size[1])
            self.widget_size[0] = size[0]
            self.widget_size[1] += size[1]

        self.mainwidget.setGeometry(*self.Geometry[:2], *self.widget_size)  # NOQA

    def addWidget(self, widget: QWidget):
        size = widget.size().toTuple()
        widget.setParent(self.mainwidget)
        widget.move(0, self.widget_size[1])
        if not self.widget_size[0]:
            self.widget_size[0] = size[0] - 20  # NOQA
        self.widget_size[1] += size[1]  # NOQA
        self.mainwidget.setGeometry(*self.Geometry[:2], *self.widget_size)  # NOQA

        self.widgets.append(widget)

    def __getitem__(self, item):
        return self.widgets[item]

    def clearself(self):
        """
        Should only be used at bookgrid.
        :return: None
        """
        if not self.widgets:
            return

    def setMainWidget(self, widget):
        self.mainwidget = widget
        self.setWidget(self.mainwidget)

    def resetMainWidget(self):
        self.mainwidget = QWidget()
        self.setWidget(self.mainwidget)

    def expandMainWidget(self, dlt: tuple[int, int]):
        w, h = self.mainwidget.width(), self.mainwidget.height()
        dw, dh = dlt
        self.mainwidget.resize(w + dw, h + dh)

    def __repr__(self):
        return f"<{self.__class__.__name__} widgets={self.widgets}>"


class ExitButton(QPushButton):
    def __init__(self, parent=None, Geometry=None):
        super().__init__(parent)
        self.setText('Exit')
        self.setFont(DefaultFont())
        self.clicked.connect(exit)
        if Geometry:
            self.setGeometry(Geometry)


class DefaultFont(QFont):
    def __init__(self, size=13, bold=False, underline=False):
        super().__init__()
        self.setFamily("Times New Roman")
        self.setPointSize(size)
        if bold:
            self.setBold(True)
        if underline:
            self.setUnderline(True)

    def setFont(self, font):
        self.setFamily(font)
        return self


class GroupedWidgets(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.group_width = 0
        self.group_height = 0
        self.unit_size = None
        self.widgets = []

    def addWidget(self, widget: QWidget, grid_pos: (int, int)):
        widget.setParent(self)
        if not self.unit_size:
            self.unit_size = widget.size().toTuple()
        cur_width = self.unit_size[0] * (grid_pos[0] + 1)
        cur_height = self.unit_size[1] * (grid_pos[1] + 1)
        if cur_width > self.group_width:
            self.group_width = cur_width
        if cur_height > self.group_height:
            self.group_height = cur_height

        widget.move(cur_width - self.unit_size[0], cur_height - self.unit_size[1])
        self.widgets.append(widget)

    def __getitem__(self, item):
        return self.widgets[item]

    def __str__(self):
        return self.widgets


class WidgetGrid(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.childsize = [0, 0]
        self.gridsize = [1, 1]
        self.rendersize = [0, 0]
        self.grid = [[None]]

    def __getitem__(self, item):
        a = []
        for i in self.grid:
            a += i
        return a[item]

    def setWidgetAt(self, widget, pos=(0, 0)):
        grid = self.grid
        grid = extand_list_to(grid, *pos)
        grid[pos[0]][pos[1]] = widget
        self.grid = grid
        self.gridsize = [len(grid[0]), len(grid)]
        widget.setParent(self)

    def setChildSize(self, csize=None):
        if csize is None:
            csize = [1, 1]
        self.childsize = csize
        self.rendersize = [self.gridsize[0] * csize[0], self.gridsize[1] * csize[1]]

    def addWidget(self, widget):
        for i in range(self.gridsize[0] * self.gridsize[1]):
            x = i // self.gridsize[0]
            y = i % self.gridsize[0]
            if not self.grid[x][y]:
                self.grid[x][y] = widget
                widget.setParent(self)
                widget.move(y * self.childsize[0], x * self.childsize[1])
                return

    def setGridSize(self, gsize: tuple):
        if not gsize:
            gsize = (1, 1)
        self.gridsize = gsize
        self.grid = extand_list_to(self.grid, *gsize)

    def clearself(self):
        a = []
        for i in self.grid:
            a += i
        if not a[0]:
            return
        for i in a:
            i.setParent(None)
        self.gridsize = [1, 1]
        self.rendersize = [0, 0]
        self.grid = [[0]]

    def __repr__(self):
        return f"<{self.__class__.__name__} grid={self.grid}>"


class BinaryCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTristate(True)

    def nextCheckState(self):
        if self.checkState() == Qt.CheckState.Checked:
            self.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.setCheckState(Qt.CheckState.Checked)
