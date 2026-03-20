from os.path import exists as ext
from os import startfile, getcwd
from datetime import datetime
from typing import Any

from PySide6.QtWidgets import QWidget, QProgressBar, QApplication, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont

from BySide import ClickableLabel, DefaultFont
from rating import StarRatingWidget as Rtw, FavouriteWidget as Fvw
from ui_ctask import DetailedWindow
from bookbank import get_bookinfo_from, save_as_bank
from config import read_json, confirm_name, LUXINFO_TEMPLATE as get_template, CONFIG, translate_to as tsl
# from netwk import GetRq

DF_11 = DefaultFont(11)
DF_12 = DefaultFont(12)
DF_10_B = DefaultFont(10, True)
DF_11_B = DefaultFont(11, True)
BANK_PATH = CONFIG['BANK_PATH']
LANGUAGE = CONFIG['LANGUAGE']
LANG = tsl(LANGUAGE)


# noinspection PyAttributeOutsideInit
class BookWidget(QWidget):
    upd_oth = Signal()
    download_thumb = Signal(int)

    def __init__(self, parent=None, bankinfo=None):
        """
        :param parent: Parent.
        :param bankinfo: bookinfo
        """
        LUXINFO_TEMPLATE = get_template()
        super().__init__(parent)
        if bankinfo is None:
            return
        if len(bankinfo) == 2:
            bankinfo[0], bankinfo[1] = bankinfo[1], bankinfo[0]
        self.bankinfo = bankinfo

        self.setFixedSize(347, 170)
        self.numname = bankinfo[0]
        self.lux_info: dict[str, Any] = LUXINFO_TEMPLATE if len(bankinfo) < 6 else bankinfo[5]
        self.bankpos = get_bookinfo_from(self.numname)
        try:
            self.hmzinfo = read_json(f'{BANK_PATH}/{confirm_name(bankinfo[1])}/{self.numname}.hmz')
        except Exception as e:
            print(e)
            self.hmzinfo = None

        self.thumb = f'images/thumbnails/{self.numname}.jpg'
        if not ext(f'images/thumbnails/{self.numname}.jpg'):
            self.thumb = int(self.numname)

        self.bkname = bankinfo[1]

        self.set_to_exported = False

        self.setMouseTracking(True)

    def __repr__(self):
        return str(self.bankinfo[:2])

    def upd_bank(self, lck: bool = False):
        self.bankpos[1][self.bankpos[0]] = self.send_luxed_info()
        save_as_bank(self.bankpos[1])
        if not lck:
            self.update_lux_widgets()
        self.upd_oth.emit()

    def handle_fav_clicked(self):
        self.lux_info['fav'] = self.favrt.get_fav()
        self.upd_bank()

    def handle_open_ratings(self):
        hmzinfo = self.hmzinfo
        if hmzinfo is None:
            print("No hmzinfo, ratings invalid!")
            return
        volinfo = [hmzinfo['name'], f'images/thumbnails/{self.numname}.jpg'] + [i[0] for i in hmzinfo['allname']]
        self.rating_ctask = DetailedWindow(volinfo, ratings=True, bankinfo=self.bankinfo)
        self.rating_ctask.setWindowTitle(LANG['RT_window'])
        self.rating_ctask.Close_as_dia.connect(self.handle_close_ratings)
        self.rating_ctask.show()

    def handle_open_progress(self):
        hmzinfo = self.hmzinfo
        if hmzinfo is None:
            print("No hmzinfo, reading progress invalid!")
            return
        volinfo = [hmzinfo['name'], f'images/thumbnails/{self.numname}.jpg'] + hmzinfo['allname']
        self.prg_ctask = DetailedWindow(volinfo, chapters=True, bankinfo=self.bankinfo)
        self.prg_ctask.setWindowTitle(LANG['PG_window'])
        self.prg_ctask.Close_as_dia.connect(self.handle_close_prg)
        self.prg_ctask.show()

    def handle_close_ratings(self):
        self.lux_info['rtg'] = self.rating_ctask.emission
        self.upd_bank()
        self.rating_ctask.close()

    def handle_close_prg(self):
        self.lux_info['prg'] = self.prg_ctask.emission
        self.upd_bank()
        self.prg_ctask.close()

    def send_luxed_info(self):
        if not any(self.lux_info.values()):
            return self.bankinfo[:5]
        if len(self.bankinfo) < 6:
            self.bankinfo.append(0)
        self.bankinfo[5] = self.lux_info
        return self.bankinfo

    def update_bankinfo_from_bank(self):
        self.bankpos = get_bookinfo_from(self.numname)
        # self.bankinfo = self.bankpos[1][self.bankpos[0]]

    def get_percentage_prg(self):
        if self.hmzinfo is None:
            print("No hmzinfo, progress bar invalid!")
            return None
        allname = self.hmzinfo['allname']
        all_c = sum([len(i) for i in allname]) - len(allname)
        cur_c = 0
        for i in self.lux_info['prg']:
            for j in allname:
                if i == j[0]:
                    cur_c += len(j)-1
                    break
                if isinstance(i, list) and i[0] == j[0]:
                    cur_c += len(i)-1
                    break
        return int(round((cur_c/all_c * 100), 0))

    def update_lux_widgets(self):
        self.favrt.setFaved(self.lux_info['fav'])
        self.rating.set_rating(int(round(sum(self.lux_info['rtg'].values())/max(len(self.lux_info['rtg']), 1), 0)))
        self.progs.setValue(self.get_percentage_prg())

    def setupUI(self):
        if len(self.bkname) > 32:
            delta_y = 48
        elif len(self.bkname) <= 13:
            delta_y = 20
        else:
            delta_y = 35

        self.bookname = ClickableLabel(parent=self)
        self.bookname.setGeometry(118, 8, 225, delta_y)
        self.bookname.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bookname.setText(self.bkname)
        if len(self.bkname) > 20:
            self.bookname.setFont(DF_10_B)
        else:
            self.bookname.setFont(DF_11_B)
        self.bookname.setWordWrap(True)

        self.thumbr = ClickableLabel(parent=self, pic=(219, 112, 147, 154))
        self.thumbr.setGeometry(0, 0, 113, 170)
        if not isinstance(self.thumb, int):
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

        rrtg = self.lux_info['rtg']
        self.rating = Rtw(parent=self, click=False, rating_=0 if not rrtg else sum(rrtg.values())/len(rrtg))
        self.rating.move(200, 60)

        self.favrt = Fvw(parent=self, fav=self.lux_info['fav'])
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
        self.progs.setValue(0 if not self.lux_info['prg'] else self.get_percentage_prg())
        self.progs.setGeometry(200, 89, 133, 18)

        self.update_info = QLabel(parent=self)
        self.update_info.setText(f'{LANG['BW_lck']} : ' + (LANG['BW_never'] if not self.lux_info['lck'] else self.lux_info['lck']))
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
        if ext(pth := f'{BANK_PATH}/{confirm_name(self.bkname)}'):
            self.bookname.lclicked.connect(lambda: startfile(pth))
        if not isinstance(self.thumb, int):
            self.thumbr.lclicked.connect(lambda: startfile(f'{getcwd()}/{self.thumb}'))
        else:
            print(f'Thumbnail for {self.thumb} is not found!')
            self.thumbr.lclicked.connect(lambda: self.download_thumb.emit(self.thumb))
        self.open_rts.lclicked.connect(self.handle_open_ratings)
        self.open_prg.lclicked.connect(self.handle_open_progress)
        self.favrt.clicked.connect(self.handle_fav_clicked)
        self.export_layer.lclicked.connect(self.handleExportLayer)

    def Initialize(self):
        self.setupUI()
        self.setConnection()

    def getAddress(self):
        if ext(addr := f'{BANK_PATH}/{confirm_name(self.bkname)}'):
            return addr
        print('Address not found, please check manually after re-downloading hmzfile.')
        return ''

    def getNum_name(self):
        return self.numname, confirm_name(self.bkname)

    def setLastCheck(self):
        current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.update_info.setText(f'{LANG['BW_lck']} : {current_time}')
        self.lux_info['lck'] = current_time
        self.upd_bank(lck=True)

    def handleExportLayer(self):
        self.set_to_exported = not self.set_to_exported
        if self.set_to_exported:
            self.export_layer.setPixmap(QPixmap('images/selected.png').scaled(45, 45))
        else:
            self.export_layer.setPixmap(QPixmap())

    def setExport(self, is_export_mode: bool):
        self.export_layer.setHidden(not is_export_mode)

    def checkPRG(self, prg) -> int | dict:
        if self.hmzinfo is None:
            print('No hmzinfo, progress undetectable.')
            return 0
        c = 0
        for i in prg:
            for j in self.hmzinfo['allname']:
                if set(i).issubset(set(j)):
                    c += 1
                    break
            else:
                break
        if c == len(prg):
            self.lux_info['prg'] = prg
            self.upd_bank()
            return 1
        return self.hmzinfo

    def checkRTG(self, rtg: dict) -> int | dict:
        if self.hmzinfo is None:
            print('No hmzinfo, ratings undetectable.')
            return 0
        allvols = [i[0] for i in self.hmzinfo['allname']]
        for i in rtg.keys():
            if i not in allvols:
                return self.hmzinfo
        else:
            self.lux_info['rtg'] = rtg
            self.upd_bank()
            return 1


def activate2():
    import sys
    app = QApplication(sys.argv)
    c = BookWidget(None, ['那个，其实，我还是第一次～距离和很好上床却很纯情的女友进行初体验，还有87天', "3493"])
    c.Initialize()
    c.show()
    sys.exit(app.exec())


def activate3():
    import sys
    app = QApplication(sys.argv)
    c = BookWidget(None,
                   ['一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十', "3493"])
    c.Initialize()
    c.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    activate2()
