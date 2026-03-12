from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QRect as RCT, Qt

from BySide import ClickableLabel, ScrollField, ExitButton, DefaultFont, AdvButtonGroup
from config import CONFIG, translate_to as tsl

ENABLE_BANK = CONFIG['ENABLE_BANK']
ENABLE_ISF = CONFIG['ENABLE_ISF']
LANGUAGE = CONFIG['LANGUAGE']
AUTO_UNLOCK_TEXTER = CONFIG['AUTO_UNLOCK_TEXTER']


# noinspection PyAttributeOutsideInit
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.lang = tsl(LANGUAGE)
        self.MainWindow = MainWindow
        MainWindow.setObjectName("LightND")
        MainWindow.resize(660, 380)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/icon.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)

        self.tabList: list[str] = []
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(RCT(0, 0, 661, 381))
        self.tabWidget.setObjectName("tabWidget")
        self.Downloader = QtWidgets.QWidget()
        self.Downloader.setObjectName("Downloader")

        Dfont = DefaultFont()
        Sfont = DefaultFont(11)
        SSfont = DefaultFont(10)

        self.Exit = ExitButton(parent=MainWindow)
        self.Exit.setGeometry(RCT(52, 312, 90, 28))

        self.DirectoryCh = QtWidgets.QPushButton(parent=self.Downloader)
        self.DirectoryCh.setGeometry(RCT(222, 288, 130, 28))

        self.DirectoryCh.setFont(Dfont)
        self.DirectoryCh.setObjectName("DirectoryCh")
        self.NumnameInput = QtWidgets.QLineEdit(parent=self.Downloader)
        self.NumnameInput.setGeometry(RCT(100, 30, 171, 21))
        self.NumnameInput.setObjectName("NumnameInput")
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(parent=self.Downloader)
        self.verticalLayoutWidget_4.setGeometry(RCT(230, 88, 101, 91))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.TextFormula_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.TextFormula_2.setContentsMargins(0, 0, 0, 0)
        self.TextFormula_2.setObjectName("TextFormula_2")
        self.TF_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_4)
        self.TF_1.setObjectName("TF_4")
        self.TextFormula_2.addWidget(self.TF_1)
        self.TF_2 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_4)
        self.TF_2.setObjectName("TF_5")
        self.TextFormula_2.addWidget(self.TF_2)
        self.TF_3 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_4)
        self.TF_3.setObjectName("TF_6")
        self.TextFormula_2.addWidget(self.TF_3)
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(parent=self.Downloader)
        self.verticalLayoutWidget_3.setGeometry(RCT(120, 88, 73, 61))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.DownloadMode_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.DownloadMode_2.setContentsMargins(0, 0, 0, 0)
        self.DownloadMode_2.setObjectName("DownloadMode_2")
        self.DM_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_3)
        self.DM_1.setObjectName("DM_3")
        self.DownloadMode_2.addWidget(self.DM_1)
        self.DM_2 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_3)
        self.DM_2.setObjectName("DM_4")
        self.DownloadMode_2.addWidget(self.DM_2)
        self.layoutWidget = QtWidgets.QWidget(parent=self.Downloader)
        self.layoutWidget.setGeometry(350, 88, 131, 151)
        self.layoutWidget.setObjectName("layoutWidget")
        self.Output_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.Output_2.setContentsMargins(3, 0, 0, 0)
        self.Output_2.setObjectName("Output_2")
        self.OU_1 = QtWidgets.QRadioButton(parent=self.layoutWidget)
        self.OU_1.setObjectName("OU_6")
        self.Output_2.addWidget(self.OU_1)
        self.OU_2 = QtWidgets.QRadioButton(parent=self.layoutWidget)
        self.OU_2.setObjectName("OU_7")
        self.Output_2.addWidget(self.OU_2)
        self.OU_3 = QtWidgets.QCheckBox(parent=self.layoutWidget)
        self.OU_3.setObjectName("OU_8")
        self.Output_2.addWidget(self.OU_3)
        self.OU_4 = QtWidgets.QCheckBox(parent=self.layoutWidget)
        self.OU_4.setObjectName("OU_9")
        self.Output_2.addWidget(self.OU_4)
        self.OU_5 = QtWidgets.QCheckBox(parent=self.layoutWidget)
        self.OU_5.setObjectName("OU_10")
        self.Output_2.addWidget(self.OU_5)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(parent=self.Downloader)
        self.verticalLayoutWidget_2.setGeometry(30, 88, 71, 91)
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")

        self.DownloadContent_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.DownloadContent_2.setContentsMargins(0, 0, 0, 0)
        self.DownloadContent_2.setObjectName("DownloadContent_2")

        self.DC_1 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_2)
        self.DC_1.setObjectName("DC_4")

        self.DownloadContent_2.addWidget(self.DC_1)
        self.DC_2 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_2)
        self.DC_2.setObjectName("DC_5")

        self.DownloadContent_2.addWidget(self.DC_2)
        self.DC_3 = QtWidgets.QRadioButton(parent=self.verticalLayoutWidget_2)
        self.DC_3.setObjectName("DC_6")

        self.DownloadContent_2.addWidget(self.DC_3)
        self.StartB = QtWidgets.QPushButton(parent=self.Downloader)
        self.StartB.setGeometry(RCT(500, 288, 120, 28))
        self.StartB.setFont(Dfont)
        self.StartB.setObjectName("StartB")

        self.TDList = QtWidgets.QPushButton(parent=self.Downloader)
        self.TDList.setGeometry(RCT(505, 26, 110, 28))
        self.TDList.setFont(Dfont)
        self.TDList.setObjectName("TDList")

        self.label = QtWidgets.QLabel(parent=self.Downloader)
        self.label.setGeometry(RCT(30, 30, 71, 21))
        self.label.setObjectName("label")

        # self.CheckUPD = QtWidgets.QPushButton(parent=self.Downloader)
        # self.CheckUPD.setGeometry(RCT(505, 138, 110, 28))
        # self.CheckUPD.setFont(Dfont)
        # self.CheckUPD.setObjectName("CheckUPD")

        self.TaskUPD = QtWidgets.QPushButton(parent=self.Downloader)
        self.TaskUPD.setGeometry(RCT(505, 178, 110, 28))
        self.TaskUPD.setFont(Dfont)
        self.TaskUPD.setText(self.lang['MIS_button'])

        self.detailBT = QtWidgets.QPushButton(parent=self.Downloader)
        self.detailBT.setGeometry(RCT(505, 78, 110, 28))
        self.detailBT.setFont(Dfont)
        self.detailBT.setText(self.lang['DL_DetailMode'])
        self.detailBT.setObjectName("DetailBT")

        self.GLB_setting = QtWidgets.QPushButton(parent=self.MainWindow)
        self.GLB_setting.setGeometry(636, 23, 23, 23)
        self.GLB_setting.setFont(Sfont)
        self.GLB_setting.setText('△')

        self.tabWidget.addTab(self.Downloader, "")
        self.tabList.append('Downloader')

        self.Texter = QtWidgets.QWidget()
        self.Texter.setObjectName("Texter")

        self.DirectoryChoose = QtWidgets.QPushButton(parent=self.Texter)
        self.DirectoryChoose.setGeometry(RCT(480, 26, 140, 28))
        self.DirectoryChoose.setFont(Dfont)
        self.DirectoryChoose.setObjectName("DirectoryChoose")

        self.AZW2 = QtWidgets.QCheckBox(parent=self.Texter)
        self.AZW2.setGeometry(RCT(330, 170, 105, 19))
        self.AZW2.setObjectName("AZW2")
        self.DOCX1 = QtWidgets.QCheckBox(parent=self.Texter)
        self.DOCX1.setGeometry(RCT(100, 100, 106, 19))
        self.DOCX1.setObjectName("DOCX1")
        self.HFolderInput = QtWidgets.QLineEdit(parent=self.Texter)
        self.HFolderInput.setGeometry(RCT(100, 30, 291, 21))
        self.HFolderInput.setObjectName("HFolderInput")
        self.StartB_2 = QtWidgets.QPushButton(parent=self.Texter)
        self.StartB_2.setGeometry(RCT(500, 288, 120, 28))

        self.StartB_2.setFont(Dfont)
        self.StartB_2.setObjectName("StartB_2")
        self.EPUB2 = QtWidgets.QCheckBox(parent=self.Texter)
        self.EPUB2.setGeometry(RCT(220, 170, 102, 19))
        self.EPUB2.setObjectName("EPUB2")
        self.AZW1 = QtWidgets.QCheckBox(parent=self.Texter)
        self.AZW1.setGeometry(RCT(330, 100, 105, 19))
        self.AZW1.setObjectName("AZW1")
        self.EPUB1 = QtWidgets.QCheckBox(parent=self.Texter)
        self.EPUB1.setGeometry(RCT(220, 100, 102, 19))
        self.EPUB1.setObjectName("EPUB1")
        self.label_2 = QtWidgets.QLabel(parent=self.Texter)
        self.label_2.setGeometry(RCT(30, 30, 51, 21))
        self.label_2.setObjectName("label_2")
        self.DOCX2 = QtWidgets.QCheckBox(parent=self.Texter)
        self.DOCX2.setGeometry(RCT(100, 170, 106, 19))
        self.DOCX2.setObjectName("DOCX2")
        self.tabWidget.addTab(self.Texter, "")
        self.tabList.append('Texter')

        self.DC_3.setChecked(True)
        self.DM_2.setChecked(True)
        self.TF_1.setChecked(True)
        self.OU_2.setChecked(True)
        self.OU_5.setEnabled(False)

        self.NumnameInput.setValidator(QtGui.QIntValidator(1, 9999))
        self.NumnameInput.setPlaceholderText('3057')
        self.HFolderInput.setPlaceholderText('D:/fakepath/HFolder')

        self.detailBT_t = QtWidgets.QPushButton(parent=self.Texter)
        self.detailBT_t.setGeometry(505, 78, 110, 28)
        self.detailBT_t.setFont(Dfont)
        self.detailBT_t.setText(self.lang['TX_DetailMode'])

        self.unlock_button = ClickableLabel(parent=self.Texter)
        self.unlock_button.setText(self.lang['TX_Unlock'])
        self.unlock_button.move(30, 102)
        self.unlock_button.setEnabled(not AUTO_UNLOCK_TEXTER)

        self.Converter = QtWidgets.QWidget()
        self.Converter.setObjectName('converter')

        self.FileChoose_c = QtWidgets.QPushButton(parent=self.Converter)
        self.FileChoose_c.setGeometry(RCT(485, 26, 125, 28))
        self.FileChoose_c.setFont(Dfont)
        self.FileChoose_c.setObjectName("FileChoose")

        self.CInput = QtWidgets.QLineEdit(parent=self.Converter)
        self.CInput.setGeometry(RCT(132, 30, 320, 21))
        self.CInput.setObjectName("CInput")

        self.label_3 = QtWidgets.QLabel(parent=self.Converter)
        self.label_3.setGeometry(RCT(30, 30, 90, 21))
        self.label_3.setObjectName("label_3")

        self.COutput = QtWidgets.QLineEdit(parent=self.Converter)
        self.COutput.setGeometry(RCT(132, 75, 320, 21))
        self.COutput.setObjectName("COutput")

        self.label_4 = QtWidgets.QLabel(parent=self.Converter)
        self.label_4.setGeometry(RCT(30, 75, 90, 21))
        self.label_4.setObjectName("label_4")

        self.CCover = QtWidgets.QLineEdit(parent=self.Converter)
        self.CCover.setGeometry(RCT(132, 120, 320, 21))
        self.CCover.setObjectName("CCover")

        self.label_5 = QtWidgets.QLabel(parent=self.Converter)
        self.label_5.setGeometry(RCT(30, 120, 95, 21))
        self.label_5.setObjectName("label_5")

        self.CoverChoose_c = QtWidgets.QPushButton(parent=self.Converter)
        self.CoverChoose_c.setGeometry(RCT(485, 116, 125, 28))
        self.CoverChoose_c.setFont(Dfont)
        self.CoverChoose_c.setObjectName("CoverChoose")

        self.label_6 = QtWidgets.QLabel(parent=self.Converter)
        self.label_6.setGeometry(RCT(30, 165, 95, 21))
        self.label_6.setObjectName("label_6")

        self.label_7 = QtWidgets.QLabel(parent=self.Converter)
        self.label_7.setGeometry(RCT(30, 210, 96, 21))
        self.label_7.setObjectName("label_7")

        self.CTitle = QtWidgets.QLineEdit(parent=self.Converter)
        self.CTitle.setGeometry(RCT(132, 165, 320, 21))
        self.CTitle.setObjectName("CTitle")

        self.CWriter = QtWidgets.QLineEdit(parent=self.Converter)
        self.CWriter.setGeometry(RCT(132, 210, 320, 21))
        self.CWriter.setObjectName("CWriter")

        self.Start_c = QtWidgets.QPushButton(parent=self.Converter)
        self.Start_c.setGeometry(RCT(485, 288, 125, 28))
        self.Start_c.setFont(Dfont)
        self.Start_c.setObjectName("Start_c")

        self.tabWidget.addTab(self.Converter, '')
        self.tabList.append('Converter')

        self.BookBank = QtWidgets.QWidget()
        self.BBScroll = ScrollField(self.BookBank, None, (0, 30, 1062, 582))

        self.od_bank = ClickableLabel(parent=self.BookBank)
        self.od_bank.setGeometry(RCT(14, 0, 72, 28))
        self.od_bank.setFont(Sfont)
        self.od_bank.setObjectName("od_bank")
        self.od_bank.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.o_menu = QtWidgets.QMenu(self.MainWindow)
        self.o_actions = (self.o_menu.addAction(self.lang['BB_od_name']),
                          self.o_menu.addAction(self.lang['BB_od_numname']),
                          self.o_menu.addAction(self.lang['BB_od_rating']))

        self.order_arrow = ClickableLabel(parent=self.BookBank, pic=(50, 50, 50, 150))
        self.order_arrow.setGeometry(RCT(88, 0, 32, 28))
        self.order_arrow.setPixmap(QtGui.QPixmap("images/uorder.png").scaled(28, 28))
        self.order_arrow.setObjectName("uar")

        self.flt_bunko = ClickableLabel(parent=self.BookBank)
        self.flt_bunko.setGeometry(RCT(138, 3, 80, 24))
        self.flt_bunko.setFont(Sfont)
        self.flt_bunko.setObjectName("flt_bunko")

        self.b_menu = QtWidgets.QMenu(parent=self.MainWindow)

        self.flt_genre = ClickableLabel(parent=self.BookBank)
        self.flt_genre.setGeometry(RCT(228, 3, 80, 24))
        self.flt_genre.setFont(Sfont)
        self.flt_genre.setObjectName("flt_genre")

        self.g_menu = QtWidgets.QMenu(parent=self.MainWindow)

        self.flt_search = QtWidgets.QLineEdit(parent=self.BookBank)
        self.flt_search.setGeometry(RCT(324, 0, 190, 28))
        self.flt_search.setFont(Sfont)
        self.flt_search.setObjectName("flt_search")
        self.flt_search.setPlaceholderText(self.lang['BB_TextPlaceholder'])

        self.none_sr = ClickableLabel(parent=self.BookBank)
        self.none_sr.setText(self.lang['BB_nonesr'])
        self.none_sr.setFont(SSfont)
        self.none_sr.setGeometry(425, 100, 209, 30)
        self.none_sr.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.refresh_bank = ClickableLabel(parent=self.BookBank)
        self.refresh_bank.setGeometry(RCT(1000, 0, 28, 28))
        self.refresh_bank.setPixmap(QtGui.QPixmap("images/refresh.png").scaled(32, 32))
        self.refresh_bank.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;  
            }

            QLabel:hover {
                background-color: #FFECF4; 
            }
        """)

        self.flt_liked = ClickableLabel(parent=self.BookBank)
        self.flt_liked.setGeometry(968, 0, 28, 28)
        self.flt_liked.setPixmap(QtGui.QPixmap("images/heart_h.png").scaled(28, 28))
        self.flt_liked.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;  
            }

            QLabel:hover {
                background-color: #FFECF4; 
            }
        """)

        self.regenerate_bank = ClickableLabel(parent=self.BookBank)
        self.regenerate_bank.setGeometry(1032, 0, 28, 28)
        self.regenerate_bank.setPixmap(QtGui.QPixmap("images/reset.png").scaled(28, 28))
        self.regenerate_bank.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;  
            }

            QLabel:hover {
                background-color: #FFECF4; 
            }
        """)

        self.export_btn = QtWidgets.QCheckBox(parent=self.BookBank)
        self.export_btn.setGeometry(690, 3, 160, 24)
        self.export_btn.setFont(Sfont)
        self.export_btn.setText(self.lang['BB_ExportMode'])

        self.import_btn = ClickableLabel(parent=self.BookBank)
        self.import_btn.setGeometry(580, 3, 80, 24)
        self.import_btn.setFont(Sfont)
        self.import_btn.setText(self.lang['BB_ImportRMZ'])

        self.start_export = ClickableLabel(parent=self.BookBank)
        self.start_export.setGeometry(800, 2, 70, 24)
        self.start_export.setFont(Dfont)
        self.start_export.setText(self.lang['BB_Export'])
        self.start_export.setHidden(True)

        if ENABLE_BANK:
            self.tabWidget.addTab(self.BookBank, '')
            self.tabList.append('BookBank')

        self.ImageSearcher = QtWidgets.QWidget()

        self.sr_input1 = QtWidgets.QLineEdit(parent=self.ImageSearcher)
        self.sr_input1.setGeometry(100, 30, 171, 21)
        self.sr_input1.setPlaceholderText('Html num')

        self.sr_input2 = QtWidgets.QLineEdit(parent=self.ImageSearcher)
        self.sr_input2.setGeometry(100, 80, 171, 21)
        self.sr_input2.setPlaceholderText('Numname')

        self.sr_start = QtWidgets.QPushButton(parent=self.ImageSearcher)
        self.sr_start.setGeometry(100, 130, 40, 21)
        self.sr_start.setText('Search')

        if ENABLE_ISF:
            self.tabWidget.addTab(self.ImageSearcher, 'ISF')
            self.tabList.append('ImageSearcher')

        self.NovelSearcher = QtWidgets.QWidget()

        self.OU_CK = AdvButtonGroup(MainWindow, False, [self.OU_3, self.OU_4, self.OU_5])
        self.OU_R = AdvButtonGroup(MainWindow, True, [self.OU_1, self.OU_2])
        self.TF = AdvButtonGroup(MainWindow, True, [self.TF_1, self.TF_2, self.TF_3])
        self.DM = AdvButtonGroup(MainWindow, True, [self.DM_1, self.DM_2])
        self.DC = AdvButtonGroup(MainWindow, True, [self.DC_1, self.DC_2, self.DC_3])

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", self.lang['VERSION']))
        self.Exit.setText(_translate("MainWindow", self.lang['exit']))
        self.DirectoryCh.setText(_translate("MainWindow", self.lang['DL_Directory']))
        self.TF_1.setText(_translate("MainWindow", self.lang['DL_TF_1']))
        self.TF_2.setText(_translate("MainWindow", self.lang['DL_TF_2']))
        self.TF_3.setText(_translate("MainWindow", self.lang['DL_TF_3']))
        self.DM_1.setText(_translate("MainWindow", self.lang['DL_DM_1']))
        self.DM_2.setText(_translate("MainWindow", self.lang['DL_DM_2']))
        self.OU_1.setText(_translate("MainWindow", self.lang['DL_OU_1']))
        self.OU_2.setText(_translate("MainWindow", self.lang['DL_OU_2']))
        self.OU_3.setText(_translate("MainWindow", self.lang['DL_OU_3']))
        self.OU_4.setText(_translate("MainWindow", self.lang['DL_OU_4']))
        self.OU_5.setText(_translate("MainWindow", self.lang['DL_OU_5']))
        self.DC_1.setText(_translate("MainWindow", self.lang['DL_DC_1']))
        self.DC_2.setText(_translate("MainWindow", self.lang['DL_DC_2']))
        self.DC_3.setText(_translate("MainWindow", self.lang['DL_DC_3']))
        self.StartB.setText(_translate("MainWindow", self.lang['DL_StartB']))
        self.TDList.setText(_translate("MainWindow", self.lang['DL_TDList']))
        self.label.setText(_translate("MainWindow", self.lang['DL_Numname']))
        # self.CheckUPD.setText(_translate("MainWindow", "CheckList"))
        # self.TaskUPD.setText(_translate("MainWindow", "Task-List"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Downloader),
                                  _translate("MainWindow", self.lang['DL_TABNAME']))
        self.DirectoryChoose.setText(_translate("MainWindow", self.lang['TX_DirectoryChoose']))
        self.AZW2.setText(_translate("MainWindow", self.lang['TX_AZW2']))
        self.DOCX1.setText(_translate("MainWindow", self.lang['TX_DOCX1']))
        self.StartB_2.setText(_translate("MainWindow", self.lang['TX_StartB_2']))
        self.EPUB2.setText(_translate("MainWindow", self.lang['TX_EPUB2']))
        self.AZW1.setText(_translate("MainWindow", self.lang['TX_AZW1']))
        self.EPUB1.setText(_translate("MainWindow", self.lang['TX_EPUB1']))
        self.label_2.setText(_translate("MainWindow", self.lang['TX_HFolder']))
        self.DOCX2.setText(_translate("MainWindow", self.lang['TX_DOCX2']))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Texter),
                                  _translate("MainWindow", self.lang['TX_TABNAME']))
        self.FileChoose_c.setText(_translate("MainWindow", self.lang['CV_FileChoose_c']))
        self.CoverChoose_c.setText(_translate("MainWindow", self.lang['CV_CoverChoose_c']))
        self.Start_c.setText(_translate("MainWindow", self.lang['CV_Start_c']))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Converter),
                                  _translate("MainWindow", self.lang['CV_Tab_Converter']))
        self.label_3.setText(_translate("MainWindow", self.lang['CV_DOCX_input']))
        self.label_4.setText(_translate("MainWindow", self.lang['CV_EPUB_output']))
        self.label_5.setText(_translate("MainWindow", self.lang['CV_Cover_optional']))
        self.label_6.setText(_translate("MainWindow", self.lang['CV_Title_optional']))
        self.label_7.setText(_translate("MainWindow", self.lang['CV_Writer_optional']))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.BookBank),
                                  _translate("MainWindow", self.lang['BB_TABNAME']))
        self.od_bank.setText(_translate("MainWindow", self.lang['BB_od_name']))
        self.flt_bunko.setText(_translate("MainWindow", self.lang['BB_flt_bunko']))
        self.flt_genre.setText(_translate("MainWindow", self.lang['BB_flt_genre']))


def activate():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    activate()
