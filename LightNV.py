from os import listdir as ldr
from os.path import exists as ext
import sys
from time import perf_counter as pfc
from concurrent.futures import ThreadPoolExecutor

from PySide6 import QtGui
from PySide6.QtGui import QPixmap
from typing_extensions import Literal
from PySide6.QtCore import QRunnable, QThreadPool, QPoint, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QMessageBox

from downloadprocess import DownloadTask, confirm_name, get_thumb
from netwk import get_alllist
from prg_export import save_as_rmz, read_from_rmz
from prg_import import RmzImportWindow
from txtprocess import HFolder as HFd, convert_to_epub, find_hmz, NotAHFolderError, read_hmz, get_cover_from, \
    convert_to_epub_pandoc
from BySide import WidgetGrid
from bookbank import (read_bank_file, get_all_info, order_bw as odb, filter_bw as ftb, search_bw as srb,
                      filter_liked_bw as flb, order_bank_ranked as odr, generate_book_bank)
from ui_LightNV import Ui_MainWindow
from ui_bookwidget import BookWidget as BkWt
from ui_config import Ui_Config
from ui_ctask import DetailedWindow, get_default_name, restore_from_default_name
from ui_missions import CheckWindow, get_img
from config import CONFIG, succeeded
from ui_update import UpdateWindow

ALLDOCX, SEPDOCX, ALLEPUB, SEPEPUB, ALLAZW3, SEPAZW3 = 0, 1, 2, 3, 4, 5
ORDER_BB, FILTER_BB = 0, 1

ENABLE_PANDOC = CONFIG['ENABLE_PANDOC']
ENABLE_BANK = CONFIG['ENABLE_BANK']
ENABLE_ISF = CONFIG['ENABLE_ISF']
AFCI = CONFIG['AUTO_FILL_CONVERTER_INFO']
AWW = CONFIG['ALLOW_WARNING_WINDOWS']
BANK_PATH = CONFIG['BANK_PATH']
RMZ_EXPORT_PATH = CONFIG['RMZ_EXPORT_PATH']
RMZ_FILENAME_FORMAT = CONFIG['RMZ_FILENAME_FORMAT']
LANGUAGE = CONFIG['LANGUAGE']


if ENABLE_ISF:
    from image_search import search_for as searchimg


class WorkerRunnable(QRunnable):
    def __init__(self, task, callback, *args, **kwargs):
        super().__init__()
        self.callback = callback
        self.task = task
        self.args = args
        self.kw = kwargs

    def run(self):
        self.task(*self.args, **self.kw)
        self.callback()


class Downloader:
    def __init__(self):
        self.numname = ''
        self.content = 0
        self.mode = 0
        self.merging = 0
        self.global_directory = BANK_PATH
        self.docx_control = 1

    def export_param(self):
        return self.numname, self.content, self.mode, self.merging, self.global_directory, self.docx_control

    def set_param(self, data, _type: Literal[0, 1, 2, 3, 4, 5]):
        """

        :param data:
        :param _type: NUMNAME, CONTENT, MODE, MERGING, GLOBAL_DIRECTORY, DOCX_CONTROL = 0, 1, 2, 3, 4, 5
        :return: returns the data inputed.
        """
        if _type == 0:
            self.numname = data
        elif _type == 1:
            self.content = data
        elif _type == 2:
            self.mode = data
        elif _type == 3:
            self.merging = data
        elif _type == 4:
            self.global_directory = data
        elif _type == 5:
            self.docx_control = data
        return data


class Texter:
    def __init__(self):
        self.target: HFd | None = None
        self.indicator = [0, 0, 0, 0, 0, 0]

    def set_target(self, target: HFd):
        self.target = target

    def textformer(self):
        if self.indicator[0]:
            self.target.formfd()
        if self.indicator[1]:
            self.target.formfd(0)
        if self.indicator[2]:
            self.target.formepub()
        if self.indicator[3]:
            self.target.formepub(0)
        if self.indicator[4]:
            self.target.formazw3()
        if self.indicator[5]:
            self.target.formazw3(0)
        succeeded()


class Converter:
    pass


class MainWindow(QMainWindow):
    showWarning = Signal(str)
    resetBank = Signal()

    def __init__(self, test=0):
        super().__init__()

        if test:
            return
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.lang = self.ui.lang

        self.thread_pool = QThreadPool()

        self.format = 0
        self.formats = [0, 0, 0]
        self.todolist_PATH = ''
        self.todolist = []
        self.name = ''

        self.child_check = CheckWindow()
        # self.child_check.render_checklist()
        # self.child_task = TaskWindow()
        self.child_detail = None
        self.child_detail_t = None

        self.downloader = Downloader()
        self.texter = Texter()

        self.formats_t = [0, 0, 0, 0, 0, 0]
        self.buttonGroup = (self.ui.DOCX1, self.ui.DOCX2, self.ui.EPUB1, self.ui.EPUB2, self.ui.AZW1, self.ui.AZW2)

        self.converter_goal = ''

        self.hidden_veil = QWidget(parent=self.ui.BBScroll)
        self.hidden_veil.setHidden(True)

        bank = read_bank_file()
        bll = []
        self.g_opt = [self.ui.g_menu.addAction(self.lang['BB_MenuAll'])]
        self.b_opt = [self.ui.b_menu.addAction(self.lang['BB_MenuAll'])]

        if ENABLE_BANK:
            self.UAR = QPixmap("images/dorder.png").scaled(28, 28)
            self.DAR = QPixmap("images/uorder.png").scaled(28, 28)

            bll = [BkWt(bankinfo=i) for i in bank]
            bb_info = get_all_info()

            self.g_opt += [self.ui.g_menu.addAction(i) for i in bb_info[0]]
            self.b_opt += [self.ui.b_menu.addAction(i) for i in bb_info[1]]

            self.export_mode = False

        self.bw_list: list[BkWt] = odb((1, '+'), bll)

        self.bb_param = ['', '', [1, '+'], '']
        self.bb_liked: int = 0  # 0 for Nono, 1 for liked, 2 for not liked

        self.warningWindow = QMessageBox()
        self.uiConfig = Ui_Config()

        self.import_window = RmzImportWindow()

    def start_task(self, task, *args, **kwargs):
        self.thread_pool.start(WorkerRunnable(task, self.end_task, *args, **kwargs))

    def end_task(self):
        pass

    def DownloadContentControl(self):
        self.downloader.set_param(4 + self.ui.DC.id(self.ui.DC.checkedButton()), 1)

    def DownloadModeControl(self):
        self.downloader.set_param(3 + self.ui.DM.id(self.ui.DM.checkedButton()), 2)

    def TextFormulaControl(self):
        self.downloader.set_param(-2 - self.ui.TF.id(self.ui.TF.checkedButton()), 3)

    def OutputRDControl(self):
        self.downloader.set_param(-2 - self.ui.OU_R.id(self.ui.OU_R.checkedButton()), 5)
        self.Enabling()

    def OutputCKControl(self):
        checked_buttons = '0b'
        for button in self.ui.OU_CK:
            if button.isChecked():
                checked_buttons += '1'
            else:
                checked_buttons += '0'
        self.format = int(checked_buttons, 2)
        self.formats = [self.format // 4, (self.format % 4) // 2, self.format % 2]
        self.Enabling()

    def AllButtonControl(self):
        self.DownloadContentControl()
        self.DownloadModeControl()
        self.TextFormulaControl()
        self.OutputRDControl()
        self.OutputCKControl()

    def init_bookgrid(self):
        for i in self.bw_list:
            i.setParent(self.hidden_veil)

    def GoptionControl(self, idx: str | int):
        if idx == 0:
            self.ui.flt_genre.setText(self.lang["BB_selectgenre"])
        else:
            self.ui.flt_genre.setText(idx)
        self.bb_param[0] = idx
        self.render_book_bank(self.process_bw_list())

    def BoptionControl(self, idx):
        if idx == 0:
            self.ui.flt_bunko.setText(self.lang["BB_selectbunko"])
        else:
            self.ui.flt_bunko.setText(idx)
        self.bb_param[1] = idx
        self.render_book_bank(self.process_bw_list())

    def select_global_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.lang['SELECT_DIRECTORY'],
            BANK_PATH,
        )

        if directory:
            self.downloader.global_directory = directory

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.lang['SELECT_FILE'],
            "./",
            "Text Files (*.txt)"
        )

        if file_path:
            self.todolist_PATH = file_path
            self.getTodolist()
            print(self.todolist)

    def getTodolist(self):
        if not self.todolist_PATH:
            return 0
        todolist = open(self.todolist_PATH, 'r').readlines()
        self.todolist = [ii.strip() for ii in todolist]
        return 0
        # self.child_task.todolist = self.todolist
        # self.child_task.render_tasklist(self.todolist)

    def convert_start(self):
        UI = self.ui
        converter_paras = [UI.COutput.text(), UI.CTitle.text(), UI.CWriter.text(), UI.CCover.text()]
        if ENABLE_PANDOC:
            convert_to_epub_pandoc(self.converter_goal,
                                   UI.COutput.text(),
                                   UI.CTitle.text(),
                                   UI.CWriter.text(),
                                   numname=-1,
                                   cover=UI.CCover.text())
            succeeded()
            return 
        convert_to_epub(self.converter_goal, *converter_paras)
        succeeded()

    def textformer(self):
        target = HFd(self.downloader.global_directory + '/' + self.name)
        if not self.downloader.docx_control:
            return 0

        if self.formats[1]:
            target.formfd(0)
            target.formepub(0)
        else:
            target.formfd()

        if self.formats[0]:
            target.formepub()

        if self.formats[2]:
            target.formazw3()

        return 0

    def getInput_t(self):
        hfd = self.ui.HFolderInput.text()
        return hfd

    def select_directory_t(self, ask=True, directory=''):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.lang['SELECT_DIRECTORY'],
            BANK_PATH,
        ) if ask else directory
        if directory:
            self.formats_t = [0, 0, 0, 0, 0, 0]
            self.texter.set_target(HFd(directory))
            self.ui.HFolderInput.setText(directory)
            self.check_format(directory)

    def select_file_c(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.lang['SELECT_FILE'],
            "",
            "Docx Files (*.docx)"
        )

        if not file_path:
            return
        else:
            self.converter_goal = file_path
            self.ui.CInput.setText(file_path)
        if not AFCI:
            return
        auto_info = MainWindow.auto_fill(file_path)
        self.ui.COutput.setText(auto_info[0])
        self.ui.CTitle.setText(auto_info[1])
        self.ui.CWriter.setText(auto_info[2])
        self.ui.CCover.setText(auto_info[3])

    @staticmethod
    def auto_fill(path):
        paras = ['', '', '', '']
        outp = path.split('.')
        outp[-1] = 'epub'
        paras[0] = '.'.join(outp)

        dirs = path.split('/')
        filename = dirs[-1][:-5]
        paras[1] = filename
        if dirs[-2] == 'Slices' and (hmzfile := find_hmz('/'.join(dirs[:-2]))):
            vol = restore_from_default_name(path)
            _, writer, _, allname = read_hmz('/'.join(dirs[:-2]) + '/' + hmzfile)
            paras[2] = writer
            if vol == 0:
                return paras
            else:
                vol = vol - 1
            paras[3] = get_cover_from('/'.join(dirs[:-2]) + '/' + allname[vol][0])
            if paras[3] == '':
                numname = hmzfile.split('.')[0]
                paras[3] = f'images/thumbnails/{numname}.jpg'
            return paras
        if filename != dirs[-2]:
            return paras
        if hmzfile := find_hmz('/'.join(dirs[:-1])):
            _, writer, _, allname = read_hmz('/'.join(dirs[:-1]) + '/' + hmzfile)
            paras[2] = writer
            paras[3] = get_cover_from('/'.join(dirs[:-1]) + '/' + allname[0][0])
            if paras[3] == '':
                numname = hmzfile.split('.')[0]
                paras[3] = f'images/thumbnails/{numname}.jpg'
            return paras

        return paras

    def select_cover_c(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.lang['SELECT_FILE'],
            "",
            "Image Files (*.jpg; *.png; *jpeg)"
        )

        if file_path:
            self.ui.CCover.setText(file_path)

    def check_format(self, directory):
        hmz = find_hmz(directory)
        if not hmz:
            raise NotAHFolderError
        name_t, writer_t, allnet, _ = read_hmz(f'{directory}/{hmz}')

        if ext(f'{directory}/{name_t}.docx'):
            self.formats_t[ALLDOCX] = 1
        if ext(f'{directory}/{name_t}.epub'):
            self.formats_t[ALLEPUB] = 1
        if ext(f'{directory}/{name_t}.azw3'):
            self.formats_t[ALLAZW3] = 1
        if ext((vd := f'{directory}/Volume_docx')) and len(ldr(vd)) >= len(allnet):
            self.formats_t[SEPDOCX] = 1
        if ext((ve := f'{directory}/Volume_epub')) and len(ldr(ve)) >= len(allnet):
            self.formats_t[SEPEPUB] = 1
        if ext((va := f'{directory}/Volume_azw3')) and len(ldr(va)) >= len(allnet):
            self.formats_t[SEPAZW3] = 1

        self.upd_button()

    def upd_button(self):
        for y, i in enumerate(self.buttonGroup):
            if self.formats_t[y]:
                i.setEnabled(False)
                i.setChecked(True)
                continue
            i.setEnabled(True)
            i.setChecked(False)

    def ref_button(self):
        indicator = [i.isEnabled() and i.isChecked() for i in self.buttonGroup]
        if indicator[5]:
            self.buttonGroup[3].setChecked(True)
        if indicator[3]:
            self.buttonGroup[1].setChecked(True)
        if indicator[4]:
            self.buttonGroup[2].setChecked(True)
        if indicator[2]:
            self.buttonGroup[0].setChecked(True)
        indicator = [i.isEnabled() and i.isChecked() for i in self.buttonGroup]
        self.texter.indicator = indicator
        print(indicator)

    def tab_change_event(self, index):
        if self.ui.tabList[index] == 'BookBank' or self.ui.tabList[index] == 'NovelSearcher':
            self.ui.Exit.setHidden(True)
            self.ui.GLB_setting.setHidden(True)
            self.ui.MainWindow.resize(1068, 640)
            self.ui.tabWidget.resize(1068, 640)
        else:
            self.ui.MainWindow.resize(660, 380)
            self.ui.tabWidget.resize(660, 380)
            self.ui.Exit.setHidden(False)
            self.ui.GLB_setting.setHidden(False)

    # def od_button_update(self, mouse: int):
    #     bt = self.ui.od_bank
    #     bord = self.bb_param[2]
    #     if mouse == 0:
    #         bord += 1
    #     if mouse == 1:
    #         bord -= 1
    #     if bord < 0:
    #         bord = 2
    #     if bord > 2:
    #         bord = 0
    #     self.bb_param[2] = bord
    #     tplt = self.lang['BB_od_template']
    #     ct = ''
    #     if bord == 0:
    #         ct =  self.lang['BB_od_numname']
    #     elif bord == 1:
    #         ct =  self.lang['BB_od_name']
    #     elif bord == 2:
    #         ct =  self.lang['BB_od_rating']
    #     bt.setText(tplt.replace('%%', ct))
    #     self.render_book_bank(self.process_bw_list())

    def sr_edit_update(self):
        self.bb_param[3] = self.ui.flt_search.text()
        self.render_book_bank(self.process_bw_list())

    def downloadSingle(self, num=None):
        if not (num or self.todolist):
            print('请输入数字编码或选择任务清单')
            return 0
        task = DownloadTask(num, *self.downloader.export_param()[1:-1])
        self.name = task.name
        task.download()
        self.handleWarning(task.getWarning())
        self.textformer()
        succeeded()
        return 0

    def downloadMuti(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            futures = []
            for numnam in self.todolist:
                futures.append(executor.submit(self.downloadSingle, numnam))
            for i in futures:
                i.result()
        print(self.lang['ALL_SUCCEED'])

    def downloadStart(self):
        numname = self.downloader.set_param(self.ui.NumnameInput.text(), 0)
        self.AllButtonControl()
        if numname:
            self.start_task(self.downloadSingle, numname)
        elif self.todolist:
            self.downloadMuti()

    def Enabling(self):
        if self.downloader.docx_control:
            self.ui.OU_3.setEnabled(True)
            self.ui.OU_4.setEnabled(True)
        else:
            self.ui.OU_3.setEnabled(False)
            self.ui.OU_3.setChecked(False)
            self.ui.OU_4.setEnabled(False)
            self.ui.OU_4.setChecked(False)
            self.format = 0
            self.formats = [0, 0, 0]

        if self.ui.OU_3.isChecked():
            self.ui.OU_5.setEnabled(True)
        else:
            self.ui.OU_5.setEnabled(False)
            self.ui.OU_5.setChecked(False)
            self.formats[2] = 0

    def set_connection(self):
        ui = self.ui
        ui.DC.buttonClicked.connect(self.DownloadContentControl)
        ui.DM.buttonClicked.connect(self.DownloadModeControl)
        ui.TF.buttonClicked.connect(self.TextFormulaControl)
        ui.OU_R.buttonClicked.connect(self.OutputRDControl)
        ui.OU_CK.buttonClicked.connect(self.OutputCKControl)
        ui.DirectoryCh.clicked.connect(self.select_global_directory)
        ui.TDList.clicked.connect(self.select_file)
        ui.StartB.clicked.connect(self.downloadStart)
        # ui.CheckUPD.clicked.connect(self.child_check.show)
        # self.ui.TaskUPD.clicked.connect(self.child_task.show)

        ui.Exit.clicked.connect(exit)

        ui.StartB_2.clicked.connect(lambda: self.start_task(self.texter.textformer))
        for i in self.buttonGroup:
            i.clicked.connect(self.ref_button)
        ui.DirectoryChoose.clicked.connect(lambda: self.select_directory_t())

        for i in self.child_check.tasks:
            i.AddCheck.clicked.connect(lambda idx=i: print(idx.numname))
        self.child_check.add_button.clicked.connect(self.child_check.askwindow.show)

        ui.detailBT.clicked.connect(self.generate_detail_window)
        ui.detailBT_t.clicked.connect(self.generate_detail_window_t)

        ui.CoverChoose_c.clicked.connect(self.select_cover_c)
        ui.FileChoose_c.clicked.connect(self.select_file_c)
        ui.Start_c.clicked.connect(lambda: self.start_task(self.convert_start))

        ui.tabWidget.currentChanged.connect(self.tab_change_event)
        if ENABLE_BANK:
            self.set_bw_connection()

            ui.od_bank.lclicked.connect(
                lambda: ui.o_menu.exec(ui.od_bank.mapToGlobal(QPoint(0, ui.od_bank.height()))))
            ui.flt_bunko.lclicked.connect(
                lambda: ui.b_menu.exec(ui.flt_bunko.mapToGlobal(QPoint(0, ui.flt_bunko.height()))))
            ui.flt_genre.lclicked.connect(
                lambda: ui.g_menu.exec(ui.flt_genre.mapToGlobal(QPoint(0, ui.flt_genre.height()))))
            ui.flt_search.textChanged.connect(self.sr_edit_update)
            ui.refresh_bank.lclicked.connect(self.refresh_bw_list)

            ui.flt_liked.lclicked.connect(lambda: self.handleFltLiked(0))
            ui.flt_liked.rclicked.connect(lambda: self.handleFltLiked(1))

        if ENABLE_ISF:
            ui.sr_start.clicked.connect(
                lambda: self.start_task(searchimg(int(ui.sr_input1.text()), ui.sr_input2.text())))

        if AWW:
            self.showWarning.connect(lambda warning: self.showWarningWindow(warning))

        ui.none_sr.lclicked.connect(self.init_bbgrid)
        ui.GLB_setting.clicked.connect(self.uiConfig.show)

        ui.export_btn.clicked.connect(self.setExportMode)
        ui.start_export.lclicked.connect(self.handleExport)

        ui.regenerate_bank.lclicked.connect(lambda: self.handleWarning('RESETBANK'))
        self.resetBank.connect(generate_book_bank)
        ui.import_btn.clicked.connect(self.handleImport)

    def set_bw_connection(self):
        for i in self.g_opt[1:]:
            i.triggered.connect(lambda checked, action=i: self.GoptionControl(action.text()))
        for i in self.b_opt[1:]:
            i.triggered.connect(lambda checked, action=i: self.BoptionControl(action.text()))
        for i in self.ui.o_actions:
            i.triggered.connect(lambda checked, action=i: self.OoptionControl(action.text()))

        self.ui.order_arrow.clicked.connect(self.handleODArrow)
        self.g_opt[0].triggered.connect(lambda: self.GoptionControl(0))
        self.b_opt[0].triggered.connect(lambda: self.BoptionControl(0))
        for i in self.bw_list:
            i.upd_oth.connect(self.upd_bank_in_bw)
            i.detailmd.lclicked.connect(lambda bookwidget=i: self.jump_to_texter(bookwidget))
            i.updatebt.lclicked.connect(lambda bk=i: self.check_update_as(bk))

            i.download_thumb.connect(lambda numbername: get_thumb(numbername))

    @staticmethod
    def check_update(num_name: tuple[str, str]):
        """
        :param num_name: (numname: str, name: str)
        :return:
        """
        current_hmz = read_hmz(f'{BANK_PATH}/{confirm_name(num_name[1])}/{num_name[0]}.hmz', complicated=True)
        current_allnet = current_hmz[2]
        updated_alllist = get_alllist(num_name[0], 'all')
        updated_allnet = updated_alllist[0]
        current_dict = {i[0]: i[1:] for i in current_allnet}
        updated_dict = {i[0]: i[1:] for i in updated_allnet}
        additions = []
        modifications = []
        for i in updated_dict.keys():
            if current_dict.get(i) is None:
                additions.append(i)
                continue
            if current_dict.get(i) != updated_dict.get(i):
                modifications.append(i)
                continue
        if not additions and not modifications:
            return False
        return additions, modifications, updated_alllist

    def generate_detail_window(self):
        numname = self.downloader.set_param(self.ui.NumnameInput.text(), 0)
        if not numname:
            return

        task = DownloadTask(numname=numname)
        cpnames = [i[0] for i in task.allname]

        chapter = [task.name, get_img(numname, iis=True)] + cpnames
        self.child_detail = DetailedWindow(chapter)
        self.child_detail.startFBT.setText(self.lang['DL_deatiled_download'])
        self.child_detail.nameIP.setHidden(True)
        self.child_detail.text1.setHidden(True)
        self.child_detail.startFBT.clicked.connect(lambda: self.start_task(self.dlslice_d, numname))
        self.child_detail.show()

    def generate_detail_window_t(self):
        path = self.getInput_t()
        if not path:
            print('Empty Path! Please Enter a Path.')
            return 112
        hmz = find_hmz(path)

        if hmz == 0:
            print('Not A HFolder! Please Enter a Available Path.')
            return 113

        numname = hmz.split('.')[0] if hmz else ''
        name, writer, allnet = read_hmz(path + '/' + hmz)[:3]
        cpnames = [i[0] for i in allnet]

        chapter = [name, get_img(numname)] + cpnames
        self.child_detail_t = DetailedWindow(chapter)
        self.child_detail_t.startFBT.clicked.connect(lambda: self.start_task(self.formslice_t))
        self.child_detail_t.show()
        return 0

    def formslice_t(self):
        slice_ind = self.child_detail_t.get_novel_state()
        goalname = confirm_name(self.child_detail_t.get_goal_filename())
        if goalname == '112':
            goalname = f'[{get_default_name([index + 1 for index, value in enumerate(slice_ind) if value == 1])}]'

        goalname = confirm_name(goalname)
        self.texter.target.formslice(slice_ind, goalname)
        succeeded()

    def dlslice_d(self, num):
        slice_ind = self.child_detail.get_novel_state()
        self.AllButtonControl()
        task = DownloadTask(num, *self.downloader.export_param()[1:-1])
        task.downloadslice(slice_ind)
        self.handleWarning(task.getWarning())
        succeeded()

    def render_book_bank(self, bw_list=None):
        if not ENABLE_BANK:
            return
        self.init_bookgrid()
        self.ui.none_sr.setHidden(True)
        if bw_list is None:
            bw_list = self.bw_list
        elif not bw_list:
            self.ui.none_sr.setHidden(False)
        bookgrid = WidgetGrid(self.ui.BBScroll)
        bookgrid.setChildSize((347, 170))
        ht = (len(bw_list) + 2) // 3
        bookgrid.setGridSize((3, ht))
        for i in bw_list:
            bookgrid.addWidget(i)
        self.ui.BBScroll.setMainWidget(bookgrid)
        self.ui.BBScroll.mainwidget.setGeometry(0, 0, 1042, 170 * ht)

    def process_bw_list(self) -> list:
        bw_list = self.bw_list
        genre, bunko, cons, srkey = self.bb_param
        liked = self.bb_liked

        if liked > 0:
            bw_list = flb(liked, bw_list)
        if cons[0] == -1:
            bw_list = odr(True if cons[1] == '-' else False, bw_list)
            cons = None
        else:
            cons = tuple(cons)
        bw_list = srb(srkey, bw_list)
        if not genre and not bunko:
            return odb(cons, bw_list)
        if not genre:
            return odb(cons, ftb((4, bunko), bw_list))
        if not bunko:
            return odb(cons, ftb((3, genre), bw_list))
        return odb(cons, ftb((3, genre), ftb((4, bunko), bw_list)))

    def init_bbgrid(self):
        self.bb_param = ['', '', [1, '+'], '']
        self.bb_liked = 0
        self.ui.flt_liked.setPixmap(QtGui.QPixmap("images/heart_h.png").scaled(28, 28))
        self.ui.order_arrow.setPixmap(self.UAR)
        self.ui.flt_search.setText('')
        self.ui.od_bank.setFocus()
        self.ui.od_bank.setText(self.lang['BB_od_bank_init'])
        self.ui.flt_genre.setText(self.lang["BB_selectgenre"])
        self.ui.flt_bunko.setText(self.lang["BB_selectbunko"])
        self.render_book_bank()

    def upd_bank_in_bw(self):
        for i in self.bw_list:
            i.update_bankinfo_from_bank()

    def init_bwlist(self):
        for i in self.bw_list:
            i.Initialize()

    def refresh_bw_list(self):
        del self.g_opt
        del self.b_opt
        self.ui.g_menu.clear()
        self.ui.b_menu.clear()
        del self.hidden_veil
        self.ui.BBScroll.resetMainWidget()

        self.bw_list = []
        self.hidden_veil = QWidget()
        bank = read_bank_file()
        self.g_opt = [self.ui.g_menu.addAction('全部')]
        self.b_opt = [self.ui.b_menu.addAction('全部')]
        bll = [BkWt(bankinfo=i) for i in bank]
        bb_info = get_all_info()

        self.g_opt += [self.ui.g_menu.addAction(i) for i in bb_info[0]]
        self.b_opt += [self.ui.b_menu.addAction(i) for i in bb_info[1]]

        self.bw_list = odb((1, '+'), bll)
        for i in bll:
            i.Initialize()

        self.render_book_bank(self.process_bw_list())
        self.set_bw_connection()

    def jump_to_texter(self, bookWidget: BkWt):
        self.select_directory_t(ask=False, directory=bookWidget.getAddress())
        self.ui.tabWidget.setCurrentIndex(1)

    def check_update_as(self, bookWidget: BkWt):
        num_name = bookWidget.bankinfo[:2]
        result = self.check_update(num_name)
        output = bookWidget.update_result
        if not result:
            output.setText(self.lang['BW_no'])
            output.setStyleSheet('color: red')
            bookWidget.setLastCheck()
            return
        output.setText(self.lang['BW_yes'])
        output.setStyleSheet('color: green')
        bookWidget.update_info.setHidden(True)
        simup = bookWidget.simple_update
        showup = bookWidget.show_update_window
        simup.setHidden(False)
        showup.setHidden(False)
        update_window = UpdateWindow(num_name=num_name, parent=None, additions=result[0], modifications=result[1])
        showup.clicked.connect(update_window.show)
        update_window.bt.clicked.connect(
            lambda: self.start_task(
                DownloadTask(numname='-1', update=num_name).download_volumes_from_allnet,
                *MainWindow.getAllLists(update_window.getAllDownloads(), result[2])
            )
        )
        simup.clicked.connect(
            lambda: self.start_task(
                DownloadTask(numname='-1', update=num_name).download_volumes_from_allnet,
                *MainWindow.getAllLists(result[0] + result[1], result[2])
            )
        )
        bookWidget.setLastCheck()

    @staticmethod
    def getAllLists(vols, alllists):
        return [i for i in alllists[0] if i[0] in vols], [i for i in alllists[1] if i[0] in vols]

    def handleWarning(self, warning):
        if not AWW:
            return None
        if not warning:
            return 0
        self.showWarning.emit(warning)
        return None

    def showWarningWindow(self, warning):
        if warning == 'ADDBANK':
            self.warningWindow = QMessageBox()
            self.warningWindow.setModal(True)
            self.warningWindow.setWindowTitle("Warning while adding new book to Bank")
            self.warningWindow.setIcon(QMessageBox.Icon.Warning)
            self.warningWindow.setText("<b>The book name has possibly changed.</b>")
            self.warningWindow.setInformativeText("Reading progress and rankings are automatically exported.")
            btn_clean = self.warningWindow.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

            self.warningWindow.show()
            clicked_button = self.warningWindow.clickedButton()
            return 0 if clicked_button == btn_clean else 1

        if warning == 'COPYRIGHT':
            self.warningWindow = QMessageBox()
            self.warningWindow.setParent(self)
            self.warningWindow.setModal(False)
            self.warningWindow.setWindowTitle("Warning while downloading")
            self.warningWindow.setIcon(QMessageBox.Icon.Warning)
            self.warningWindow.setText("This book was taken down for <b>No copyright</b>.")
            self.warningWindow.setInformativeText("Downloading from the server directly.<br>Detail mode and "
                                                  "illustration download is now invalid.")
            btn_clean = self.warningWindow.addButton("OK", QMessageBox.ButtonRole.AcceptRole)

            self.warningWindow.show()
            clicked_button = self.warningWindow.clickedButton()
            return 0 if clicked_button == btn_clean else 1

        if warning == 'RESETBANK':
            self.warningWindow = QMessageBox()
            # self.warningWindow.setParent(self)
            self.warningWindow.setModal(True)
            self.warningWindow.setWindowTitle("Warning")
            self.warningWindow.setIcon(QMessageBox.Icon.Warning)
            self.warningWindow.setText("<b>You are trying to RESET your bank.</b>")
            self.warningWindow.setInformativeText("This process is PERMANENT.<br>All reading process, ratings and other"
                                                  " data will be lost.<br>Continue anyway?")
            btn_clean = self.warningWindow.addButton("Yes", QMessageBox.ButtonRole.AcceptRole)
            self.warningWindow.addButton("No", QMessageBox.ButtonRole.RejectRole)

            self.warningWindow.exec()
            clicked_button = self.warningWindow.clickedButton()
            if clicked_button == btn_clean:
                print(1)
                self.resetBank.emit()
                return 1
            else:
                return 0

        return 0

    def handleFltLiked(self, neg: bool | int):
        flt_l = self.ui.flt_liked
        if neg:
            self.bb_liked -= 1
        else:
            self.bb_liked += 1
        if self.bb_liked > 2:
            self.bb_liked = 0
        if self.bb_liked < 0:
            self.bb_liked = 2

        if self.bb_liked == 0:
            flt_l.setPixmap(QtGui.QPixmap("images/heart_h.png").scaled(28, 28))
        if self.bb_liked == 1:
            flt_l.setPixmap(QtGui.QPixmap("images/heart_f.png").scaled(28, 28))
        if self.bb_liked == 2:
            flt_l.setPixmap(QtGui.QPixmap("images/heart_e.png").scaled(28, 28))

        self.render_book_bank(self.process_bw_list())

    def setExportMode(self):
        self.ui.start_export.setHidden(not self.ui.export_btn.isChecked())
        for i in self.bw_list:
            i.setExport(self.ui.export_btn.isChecked())

    def handleExport(self):
        for i in self.bw_list:
            if i.set_to_exported:
                save_as_rmz(1, i.bankinfo, RMZ_EXPORT_PATH, RMZ_FILENAME_FORMAT)
        succeeded('All RMZ exported!')

    def handleSingleImport(self, filename):
        rmzfile, _type = read_from_rmz(filename)
        if _type == 1:
            if len(rmzfile) < 6:
                return
            rmz_lux = rmzfile[5]
            rmz_prg = rmz_lux['prg']
            rmz_rtg = rmz_lux['rtg']
            for i in self.bw_list:
                if i.bankinfo[0] == rmzfile[0]:
                    thisbw = i
                    break
            else:
                print(f'Book(number: {rmzfile[0]}; name: {rmzfile[1]}) not found. Please download first.')
                return
            resultp = thisbw.checkPRG(rmz_prg)
            resultr = thisbw.checkRTG(rmz_rtg)
            if (resultp != 1 and resultp != 0) or (resultr != 1 and resultr != 0):
                self.import_window.initData(rmz=rmzfile,
                                            hmzinfo=read_hmz(f'{BANK_PATH}/{thisbw.bankinfo[1]}/{rmzfile[0]}.hmz',
                                                             source=True))
                self.import_window.exec()
                self.import_window.rtg_save.connect(thisbw.checkRTG)
                self.import_window.prg_save.connect(thisbw.checkPRG)

    def handleImport(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.lang['choose_RMZ'],
            f"{RMZ_EXPORT_PATH}",
            "Rmz (*.rmz)"
        )

        if files:
            l_p_a = len(files)
            for y, filename in enumerate(files, 1):
                progress = y / l_p_a * 100
                filled_length = int(30 * y // l_p_a)
                bar = '=' * filled_length + ' ' * (30 - filled_length)
                print(f"FM: [{bar}] {progress:.2f}% ({y}/{l_p_a})", end='\r')

                self.import_window = RmzImportWindow()
                self.handleSingleImport(filename)

    def handleODArrow(self):
        arrow = self.ui.order_arrow
        if self.bb_param[2][1] == '+':
            self.bb_param[2][1] = '-'
        else:
            self.bb_param[2][1] = '+'
        arrow.setPixmap(self.UAR if self.bb_param[2][1] == '-' else self.DAR)

        self.render_book_bank(self.process_bw_list())

    def OoptionControl(self, text):
        cons = self.bb_param[2]
        self.ui.od_bank.setText(text)
        if text == self.lang['BB_od_name']:
            cons[0] = 1
        if text == self.lang['BB_od_numname']:
            cons[0] = 0
        if text == self.lang['BB_od_rating']:
            cons[0] = -1

        self.bb_param[2] = cons

        self.render_book_bank(self.process_bw_list())


def activate():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.set_connection()
    window.render_book_bank()
    window.show()
    window.init_bwlist()
    sys.exit(app.exec())


def activate_t():
    a = pfc()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.render_book_bank()
    window.show()
    window.init_bwlist()
    window.set_connection()
    b = pfc()
    print(f'{b - a:2f} seconds used to activate the window.')
    sys.exit(app.exec())


if __name__ == "__main__":
    activate_t()
