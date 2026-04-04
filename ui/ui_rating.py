from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel


class StarRatingWidget(QWidget):
    rating_changed = Signal()
    hoverMovement = Signal(tuple)

    def __init__(self, parent=None, rating_: float = 0.0, click=True):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.r_rating = rating_
        self.rating = int(round(rating_, 0))
        self.star_zize = 20
        self.clickable = click
        self.setFixedSize(5*self.star_zize+10, self.star_zize)

        self._sstate = (QPixmap("images/star_e_t.png").scaled(self.star_zize, self.star_zize),
                        QPixmap("images/star_h.png").scaled(self.star_zize, self.star_zize),
                        QPixmap("images/star_f.png").scaled(self.star_zize, self.star_zize))

        self._stars = []
        for i in range(5):
            star = QLabel(self)
            star.setGeometry(i*(self.star_zize+2), 0, self.star_zize, self.star_zize)
            self._stars.append(star)

        self.hover_widget = QLabel(self)

        self._update_display()

        if not click:
            self.hoverMovement.connect(lambda pos: self.hover_widget.move(pos[0] + 200, pos[1] + 60))

    def setHoverWidget(self, hover_widget):
        self.hover_widget = hover_widget

    def _update_display(self):
        rating = self.rating
        for i in range(5):
            star_value = int(min(max(rating - i * 2, 0), 2))
            self._stars[i].setPixmap(self._sstate[star_value])

    def set_rating(self, rating: int):
        if self.rating == rating:
            return
        self.rating = rating
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

    def enterEvent(self, event, /):
        self.hover_widget.setHidden(False)

    def leaveEvent(self, event, /):
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
    pass
