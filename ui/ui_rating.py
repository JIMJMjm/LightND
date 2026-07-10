import sys
from typing import overload, Literal

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QDoubleValidator
from PySide6.QtWidgets import QWidget, QLabel, QDialog, QSlider, QApplication, QLineEdit, QPushButton


class StarRatingWidget(QWidget):
    rating_changed = Signal()
    hoverMovement = Signal(tuple)

    @overload
    def __init__(self, parent=None, click=Literal[False]):
        ...

    @overload
    def __init__(self, parent=None, rating_: float = 0.0, weight: float = 1.0, click=Literal[True]):
        ...

    def __init__(self, parent=None, rating_: float = 0.0, weight: float = 1.0, click=True):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.r_rating = rating_
        self.rating = int(round(rating_, 0))
        self.star_zize = 20
        self.clickable = click
        self.weight = weight
        self.setFixedSize(5*self.star_zize+10, self.star_zize)

        self._sstate = (QPixmap("images/star_e_t.png").scaled(self.star_zize, self.star_zize),
                        QPixmap("images/star_h.png").scaled(self.star_zize, self.star_zize),
                        QPixmap("images/star_f.png").scaled(self.star_zize, self.star_zize))

        self._stars = []
        for i in range(5):
            star = QLabel(self)
            star.setGeometry(i*(self.star_zize+2), 0, self.star_zize, self.star_zize)
            self._stars.append(star)

        self.hover_widget = None

        self._update_display()

        if not click:
            self.hoverMovement.connect(lambda pos: self.hover_widget.move(pos[0] + 200, pos[1] + 60))
            return

        self.weight_count = QDialog(self)
        self.weight_count.setFixedSize(320, 120)

        self.h_slider = QSlider(Qt.Orientation.Horizontal, parent=self.weight_count,
                                tickPosition=QSlider.TickPosition.TicksBelow, tickInterval=10)
        self.h_slider.move(0, 60)
        self.h_slider.setFixedSize(320, 60)
        self.h_slider.setRange(0, 100)
        self.h_slider.setValue(int((self.weight - 1) * 100 + 50))

        self.h_lineedit = QLineEdit(parent=self.weight_count, text=str(self.weight))
        self.h_lineedit.setGeometry(20, 15, 90, 35)
        self.h_lineedit.setFont(QFont('Times New Roman', 14))
        self.h_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dv = QDoubleValidator(decimals=2)
        dv.setRange(0.50, 1.50)
        self.h_lineedit.setValidator(dv)

        self.h_button = QPushButton('Comfirm', parent=self.weight_count)
        self.h_button.setGeometry(210, 15, 90, 35)

        self.h_slider.valueChanged.connect(lambda val: self.setHText(val))
        self.h_lineedit.textChanged.connect(lambda val: self.setHValue(val))
        self.h_button.clicked.connect(self.closeWeight)

    def closeWeight(self):
        val = self.h_slider.value()
        self.weight = round(1 + (val - 50) / 100, 2)
        self.weight_count.close()

    def setHText(self, value: int):
        self.h_lineedit.blockSignals(True)
        self.h_lineedit.setText(str(round(1 + (value - 50) / 100, 2)))
        self.h_lineedit.blockSignals(False)

    def setHValue(self, value):
        if not value:
            return
        value = float(value)
        self.h_slider.blockSignals(True)
        self.h_slider.setValue(int((value - 1) * 100 + 50))
        self.h_slider.blockSignals(False)

    def setWeight(self, weight: float):
        self.weight = weight
        self.setHValue(weight)
        self.setHText(self.h_slider.value())

    def setHoverWidget(self, hover_widget):
        self.hover_widget = hover_widget

    def _update_display(self):
        rating = self.rating
        r_rating = self.r_rating
        if self.hover_widget is not None:
            self.hover_widget.setText(f'{r_rating:.2f}')
        for i in range(5):
            star_value = int(min(max(rating - i * 2, 0), 2))
            self._stars[i].setPixmap(self._sstate[star_value])

    def set_rating(self, Rrating: float):
        if self.r_rating == Rrating:
            return
        self.rating = int(Rrating + 0.5)
        self.r_rating = Rrating
        self._update_display()
        self.rating_changed.emit()

    def get_rating(self):
        return self.rating

    def mousePressEvent(self, event):
        if not self.clickable:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            self._handle_click(pos)
        if event.button() == Qt.MouseButton.RightButton:
            self.weight_count.show()

    def enterEvent(self, event, /):
        if self.hover_widget is None:
            return
        self.hover_widget.setHidden(False)

    def leaveEvent(self, event, /):
        if self.hover_widget is None:
            return
        self.hover_widget.setHidden(True)

    def mouseMoveEvent(self, event, /):
        self.hoverMovement.emit((event.x(), event.y()))

    def _handle_click(self, pos):
        for i in range(5):
            star_rect = self._stars[i].geometry()
            if not star_rect.contains(pos):
                continue
            relative_x = pos.x() - star_rect.x()
            half_width = self.star_zize / 2
            new_rating = i * 2 + 1 + (relative_x >= half_width)
            self.set_rating(new_rating)
            break


class FavouriteWidget(QWidget):
    clicked = Signal(bool)

    def __init__(self, parent=None, fav=False):
        super().__init__(parent)
        self._fav = fav
        self._full = QPixmap("images/heart_f.png")
        self._empty = QPixmap("images/heart_e.png")
        self.setFixedSize(20, 20)
        self.mainwidget = QLabel(parent=self)

        self.update_display()

    def setFaved(self, fav):
        self._fav = fav
        self.update_display()

    def update_display(self):
        if self._fav:
            self.mainwidget.setPixmap(self._full)
        else:
            self.mainwidget.setPixmap(self._empty)

    def mousePressEvent(self, event, /):
        if event.button() == Qt.MouseButton.LeftButton:
            self._fav = not self._fav
            self.clicked.emit(self._fav)
            self.update_display()

    def get_fav(self):
        return self._fav


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QDialog()
    window.setFixedSize(320, 120)

    h_slider = QSlider(Qt.Orientation.Horizontal, parent=window, tickPosition=QSlider.TickPosition.TicksBelow, tickInterval=10)
    h_slider.move(0, 60)
    h_slider.setFixedSize(320, 60)
    h_slider.setRange(0, 100)
    h_slider.setValue(50)

    h_lineedit = QLineEdit(parent=window, text='50')
    h_lineedit.setGeometry(20, 15, 90, 35)
    h_lineedit.setFont(QFont('Times New Roman', 14))
    h_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)

    h_button = QPushButton('Comfirm', parent=window)
    h_button.setGeometry(210, 15, 90, 35)

    h_slider.valueChanged.connect(lambda val: h_lineedit.setText(str(val)))

    window.show()
    app.exec()
