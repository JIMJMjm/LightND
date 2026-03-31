from datetime import datetime
from os import startfile, getcwd
from os.path import exists as ext

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel

from BySide import ClickableLabel, DefaultFont
from book_struct import BankedBook, BookLuxury, HmzedBook
from bookbank import add_to_bank, getTimeStringFromStamp, read_hmz_par
from config import confirm_name, CONFIG, translate_to as tsl
from rating import StarRatingWidget as Rtw, FavouriteWidget as Fvw
from ui_ctask import DetailedWindow

DF_11 = DefaultFont(11)
DF_12 = DefaultFont(12)
DF_10_B = DefaultFont(10, True)
DF_11_B = DefaultFont(11, True)
BANK_PATH = CONFIG['BANK_PATH']
LANGUAGE = CONFIG['LANGUAGE']
LANG = tsl(LANGUAGE)


# noinspection PyAttributeOutsideInit
class BookWidget(QWidget):
    def __init__(self, bankinfo: BankedBook, parent=None):
        """
        :param parent: Parent.
        :param bankinfo: bookinfo
        """
        super().__init__(parent)
        self.bankinfo = bankinfo

        self.setFixedSize(347, 170)
        self.numname = bankinfo.numname
        self.lux_info: BookLuxury = bankinfo.lux

        self.hmzinfo: HmzedBook
        if ext(f'{bankinfo.directory}/{bankinfo.name}/{self.numname}.hmz'):
            self.hmzpath = f'{bankinfo.directory}/{bankinfo.name}/{self.numname}.hmz'
            self.hmzinfo = read_hmz_par(self.hmzpath)
        else:
            print('Hmz File not found!')
            self.hmzinfo = None

        self.thumb = f'images/thumbnails/{self.numname}.jpg'
        if not ext(f'images/thumbnails/{self.numname}.jpg'):
            self.thumb = None
        self.name = bankinfo[1]

        self.set_to_exported = False
        self.setMouseTracking(True)

    def __repr__(self):
        return self.bankinfo.__repr__() + '_BOOKWIDGET'

    def upd_bank(self, lck: bool = False):
        add_to_bank(self.bankinfo, force_cover=True)
        if not lck:
            self.update_lux_widgets()

    def handle_fav_clicked(self):
        self.lux_info.fav = self.favrt.get_fav()
        self.upd_bank()

    def handle_open_ratings(self):
        if self.hmzinfo is None:
            print("No hmzinfo, ratings invalid!")
            return

        volinfo = [self.hmzinfo.name, f'images/thumbnails/{self.numname}.jpg'] + [i[0] for i in self.hmzinfo.allname]
        self.rating_ctask = DetailedWindow(volinfo, ratings=True, bankinfo=self.bankinfo)
        self.rating_ctask.setWindowTitle(LANG['RT_window'])
        self.rating_ctask.Close_as_dia.connect(self.handle_close_ratings)
        self.rating_ctask.show()

    def handle_open_progress(self):
        if self.hmzinfo is None:
            print("No hmzinfo, reading progress invalid!")
            return

        volinfo = [self.hmzinfo.name, f'images/thumbnails/{self.numname}.jpg'] + self.hmzinfo.allname
        self.prg_ctask = DetailedWindow(volinfo, chapters=True, bankinfo=self.bankinfo)
        self.prg_ctask.setWindowTitle(LANG['PG_window'])
        self.prg_ctask.Close_as_dia.connect(self.handle_close_prg)
        self.prg_ctask.show()

    def handle_close_ratings(self):
        self.lux_info.rtg = self.rating_ctask.emission
        self.upd_bank()
        self.rating_ctask.close()

    def handle_close_prg(self):
        self.lux_info.prg = self.prg_ctask.emission
        self.upd_bank()
        self.prg_ctask.close()

    def get_percentage_prg(self):
        if self.hmzinfo is None:
            print("No hmzinfo, progress bar invalid!")
            return None
        allname = self.hmzinfo.allname
        all_c = sum([len(i) for i in allname]) - len(allname)
        cur_c = 0
        for i in self.lux_info.prg:
            for j in allname:
                if i == j[0]:
                    cur_c += len(j)-1
                    break
                if isinstance(i, list) and i[0] == j[0]:
                    cur_c += len(i)-1
                    break
        return int(round((cur_c/all_c * 100), 0))

    def update_lux_widgets(self):
        self.favrt.setFaved(self.lux_info.fav)
        self.rating.set_rating(int(round(sum(self.lux_info.rtg.values())/max(len(self.lux_info.rtg), 1), 0)))
        self.progs.setValue(self.get_percentage_prg())

    def setupUI(self):
        if len(self.name) > 32:
            delta_y = 48
        elif len(self.name) <= 13:
            delta_y = 20
        else:
            delta_y = 35

        self.bookname = ClickableLabel(parent=self)
        self.bookname.setGeometry(118, 8, 225, delta_y)
        self.bookname.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bookname.setText(self.name)
        if len(self.name) > 20:
            self.bookname.setFont(DF_10_B)
        else:
            self.bookname.setFont(DF_11_B)
        self.bookname.setWordWrap(True)

        self.thumbr = ClickableLabel(parent=self, pic=(219, 112, 147, 154))
        self.thumbr.setGeometry(0, 0, 113, 170)
        if self.thumb is not None:
            self.thumbr.setPixmap(QPixmap(self.thumb).scaled(113, 170))
        else:
            self.thumbr.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.thumbr.setText('?')

        self.updatebt = ClickableLabel(parent=self, text=LANG['BW_update'])
        self.updatebt.setGeometry(195, 117, 50, 17)
        self.updatebt.setFont(DF_11)

        self.detailmd = ClickableLabel(parent=self, text=LANG['BW_texter'])
        self.detailmd.setGeometry(130, 117, 47, 17)
        self.detailmd.setFont(DF_11)

        rrtg = self.lux_info.rtg
        self.rating = Rtw(parent=self, click=False, rating_=0 if not rrtg else sum(rrtg.values())/len(rrtg))
        self.rating.move(200, 60)

        self.favrt = Fvw(parent=self, fav=self.lux_info.fav)
        self.favrt.move(312, 61)

        self.open_prg = ClickableLabel(text=LANG['BW_progress'], parent=self)
        self.open_prg.setFont(DF_12)
        self.open_prg.setGeometry(120, 88, 80, 18)
        self.open_prg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.open_rts = ClickableLabel(text=LANG['BW_rating'], parent=self)
        self.open_rts.setFont(DF_12)
        self.open_rts.setGeometry(120, 61, 80, 18)
        self.open_rts.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progs = QProgressBar(parent=self)
        self.progs.setTextVisible(False)
        self.progs.setRange(0, 100)
        self.progs.setValue(0 if not self.lux_info.prg else self.get_percentage_prg())
        self.progs.setGeometry(200, 89, 133, 18)

        self.update_info = QLabel(parent=self)
        self.update_info.setText(f'{LANG['BW_lck']} : ' + (LANG['BW_never'] if not self.lux_info.lck else
                                                           getTimeStringFromStamp(self.lux_info.lck)))
        self.update_info.setFont(DF_11)
        self.update_info.setGeometry(120, 142, 205, 18)
        self.update_info.setStyleSheet("""
        QLabel {
            color: grey;
        }
        """)

        self.update_result = QLabel(parent=self)
        self.update_result.setGeometry(252, 117, 100, 17)
        self.update_result.setFont(DF_11)

        self.show_update_window = ClickableLabel(parent=self)
        self.show_update_window.setGeometry(125, 142, 90, 18)
        self.show_update_window.setFont(DF_11)
        self.show_update_window.setText(LANG['BW_detailupd'])
        self.show_update_window.setHidden(True)

        self.simple_update = ClickableLabel(parent=self)
        self.simple_update.setGeometry(235, 142, 90, 18)
        self.simple_update.setFont(DF_11)
        self.simple_update.setText(LANG['BW_simpleupd'])
        self.simple_update.setHidden(True)

        self.export_layer = ClickableLabel(parent=self, pic=(249, 255, 86, 255))
        self.export_layer.setGeometry(0, 0, 113, 170)
        self.export_layer.setHidden(True)

        self.hover_widget = QLabel(self)
        self.hover_widget.setStyleSheet("QLabel { background-color: rgb(219, 234, 255); }")
        self.hover_widget.setText(f'{self.rating.r_rating:.2f}')
        self.hover_widget.setGeometry(200, 60, 38, 18)
        self.hover_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hover_widget.setFont(QFont('Times New Roman', 12))
        self.hover_widget.setHidden(True)
        self.rating.setHoverWidget(self.hover_widget)

    def setConnection(self):
        if ext(pth := f'{BANK_PATH}/{confirm_name(self.name)}'):
            self.bookname.lclicked.connect(lambda: startfile(f'{getcwd()}/{pth}' if ':' not in pth else pth))
        if self.thumb is not None:
            self.thumbr.lclicked.connect(lambda: startfile(f'{getcwd()}/{self.thumb}'))
        self.open_rts.lclicked.connect(self.handle_open_ratings)
        self.open_prg.lclicked.connect(self.handle_open_progress)
        self.favrt.clicked.connect(self.handle_fav_clicked)
        self.export_layer.lclicked.connect(self.handleExportLayer)

    def Initialize(self):
        self.setupUI()
        self.setConnection()

    def getAddress(self):
        if ext(addr := f'{self.bankinfo.directory}/{self.bankinfo.name}'):
            return addr
        print('Address not found, please check manually after re-downloading hmzfile.')
        return ''

    def getNum_name(self):
        return self.numname, confirm_name(self.name)

    def setLastCheck(self):
        current_time = datetime.now()
        self.update_info.setText(f'{LANG['BW_lck']} : {current_time.strftime("%Y/%m/%d %H:%M:%S")}')
        self.lux_info.lck = int(current_time.timestamp())
        self.upd_bank(lck=True)

    def handleExportLayer(self):
        self.set_to_exported = not self.set_to_exported
        if self.set_to_exported:
            self.export_layer.setPixmap(QPixmap('images/selected.png').scaled(45, 45))
        else:
            self.export_layer.setPixmap(QPixmap())

    def setExport(self, is_export_mode: bool):
        self.export_layer.setHidden(not is_export_mode)

    def checkPRG(self, prg) -> int | HmzedBook:
        if self.hmzinfo is None:
            print('No hmzinfo, progress undetectable.')
            return 0
        c = 0
        for i in prg:
            for j in self.hmzinfo.allname:
                if set(i).issubset(set(j)):
                    c += 1
                    break
            else:
                break
        if c == len(prg):
            self.lux_info.prg = prg
            self.upd_bank()
            return 1
        return self.hmzinfo

    def checkRTG(self, rtg: dict) -> int | HmzedBook:
        if self.hmzinfo is None:
            print('No hmzinfo, ratings undetectable.')
            return 0
        allvols = [i[0] for i in self.hmzinfo.allname]
        for i in rtg.keys():
            if i not in allvols:
                return self.hmzinfo
        else:
            self.lux_info.rtg = rtg
            self.upd_bank()
            return 1


if __name__ == '__main__':
    pass
