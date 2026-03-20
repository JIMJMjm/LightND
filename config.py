import json
from os.path import exists as ext

from winsound import PlaySound

DEFAULT_SETTING = {
    "ENABLE_PANDOC": True,
    "ENABLE_ISF": False,
    "COMPLICATE_SLICE_NAME": False,
    "MAX_THREAD_WORKER": 6,
    "ALWAYS_USE_DEFAULT_DOWNLOAD": False,
    "ILLUSTRATION_REQUEST_SLEEP_TIME": 0.1,
    "TEXT_REQUEST_SLEEP_TIME": 0.2,
    "MAX_VOLUME_THREAD_WORKER": 2,
    "ENABLE_BANK": True,
    "AUTO_FILL_CONVERTER_INFO": True,
    "ALLOW_WARNING_WINDOWS": True,
    "BANK_PATH": "novel",
    "RMZ_EXPORT_PATH": "rmz",
    "RMZ_FILENAME_FORMAT": "%NUMNAME%_%TIMESTAMP%",
    "DEFAULT_COVER": "images/uncovered.jpg",
    "LANGUAGE": "en-US"
}


def LUXINFO_TEMPLATE():
    return {'prg': [],
            'rtg': {},
            'fav': 0,
            'lck': ''}


# noinspection PyTypeChecker
def save_json(path, content, format_=1):
    with open(path, 'w', encoding='utf-8') as f:
        if format_ == 1:
            json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            json.dump(content, f, separators=(',', ':'), ensure_ascii=False)
    return 0


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_global_settings(reset: bool = False) -> dict:
    if (not ext('config.json')) or reset:
        save_json('config.json', DEFAULT_SETTING)
    return read_json('config.json')


def modify_global_settings(global_settings):
    save_json('config.json', global_settings)


def confirm_name(name_c):
    if ':' in name_c:
        name_c = name_c.replace(':', '：')
    if '/' in name_c:
        name_c = name_c.replace('/', '／')
    if '?' in name_c:
        name_c = name_c.replace('?', '？')
    if '\\' in name_c:
        name_c = name_c.replace('\\', '／')
    if '|' in name_c:
        name_c = name_c.replace('|', '、')
    if '<' in name_c:
        name_c = name_c.replace('<', '《')
    if '>' in name_c:
        name_c = name_c.replace('>', '》')
    if '*' in name_c:
        name_c = name_c.replace('*', '∆')
    if '\"' in name_c:
        name_c = name_c.replace('\"', '\'')
    return name_c


def translate_to(code: str) -> dict[str, str]:
    ALL_TEXT = {"VERSION": {'en-US': "LightND - Release_v7.3"},
                "exit": {'en-US': "Exit", 'zh-CN': "退出"},
                "DL_Directory": {'en-US': "Save to...", 'zh-CN': "下载至..."},
                "DL_TF_1": {'en-US': "Chapters", 'zh-CN': "仅章节"},
                "DL_TF_2": {"en-US": "+ Volumes", "zh-CN": "+分卷"},
                "DL_TF_3": {"en-US": "+ Series", "zh-CN": "+系列整合"},
                "DL_DM_1": {"en-US": "Re-Down", "zh-CN": "重新下载"},
                "DL_DM_2": {"en-US": "Continue", "zh-CN": "继续下载"},
                "DL_OU_1": {"en-US": "TXT", "zh-CN": "仅TXT"},
                "DL_OU_2": {"en-US": "+ Series DOCX", "zh-CN": "+系列DOCX"},
                "DL_OU_3": {"en-US": "+ Series EPUB", "zh-CN": "+系列EPUB"},
                "DL_OU_4": {"en-US": "+ Volume EPUB", "zh-CN": "+分卷EPUB"},
                "DL_OU_5": {"en-US": "+ Series AZW3", "zh-CN": "+系列AZW3"},
                "DL_DC_1": {"en-US": "Text only", "zh-CN": "仅文字"},
                "DL_DC_2": {"en-US": "Illst only", "zh-CN": "仅插画"},
                "DL_DC_3": {"en-US": "Both", "zh-CN": "全部"},
                "DL_StartB": {"en-US": "Start Download", "zh-CN": "开始下载"},
                "DL_TDList": {"en-US": "To-do List", "zh-CN": "任务列表"},
                "DL_Numname": {"en-US": "Numname：", "zh-CN": "数字编码："},
                "DL_TABNAME": {"en-US": "Downloader", "zh-CN": "下载器"},
                "TX_DirectoryChoose": {"en-US": "Browse Directory", "zh-CN": "选择文件夹"},
                "TX_AZW2": {"en-US": "Volume AZW3", "zh-CN": "分卷AZW3"},
                "TX_DOCX1": {"en-US": "Series DOCX", "zh-CN": "系列DOCX"},
                "TX_StartB_2": {"en-US": "Start Forming", "zh-CN": "开始格式化"},
                "TX_EPUB2": {"en-US": "Volume EPUB", "zh-CN": "分卷EPUB"},
                "TX_AZW1": {"en-US": "Series AZW3", "zh-CN": "系列AZW3"},
                "TX_EPUB1": {"en-US": "Series EPUB", "zh-CN": "系列EPUB"},
                "TX_HFolder": {"en-US": "HFolder:", "zh-CN": "文件夹:"},
                "TX_DOCX2": {"en-US": "Volume DOCX", "zh-CN": "分卷DOCX"},
                "TX_TABNAME": {"en-US": "Texter", "zh-CN": "格式器"},
                "CV_FileChoose_c": {"en-US": "Select File", "zh-CN": "选择文件"},
                "CV_CoverChoose_c": {"en-US": "Select Cover", "zh-CN": "选择封面"},
                "CV_Start_c": {"en-US": "Convert", "zh-CN": "开始转换"},
                "CV_Tab_Converter": {"en-US": "Converter", "zh-CN": "转换器"},
                "CV_DOCX_input": {"en-US": "DOCX input：", "zh-CN": "DOCX输入:"},
                "CV_EPUB_output": {"en-US": "EPUB output：", "zh-CN": "EPUB输出:"},
                "CV_Cover_optional": {"en-US": "Cover(optional)：", "zh-CN": "封面(可选)"},
                "CV_Title_optional": {"en-US": "Title(optional)：", "zh-CN": "标题(可选)"},
                "CV_Writer_optional": {"en-US": "Writer(optional)：", "zh-CN": "作者(可选)"},
                "BB_TABNAME": {"en-US": "Bank", "zh-CN": "书库"},
                "BB_od_bank_init": {"en-US": "Ordered by name", "zh-CN": "按书名排序"},
                "BB_flt_bunko": {"en-US": "Select bunko", "zh-CN": "选择文库"},
                "BB_flt_genre": {"en-US": "Select genre", "zh-CN": "选择标签"},
                "TX_DetailMode": {'en-US': "DetailMode", 'zh-CN': "细节模式"},
                "DL_DetailMode": {'en-US': "DetailMode", 'zh-CN': "细节模式"},
                "BB_TextPlaceholder": {'en-US': "numname|name|writer", 'zh-CN': "数字编码|书名|作者"},
                "BB_nonesr": {'en-US': "No reselt. Click to clear all conditions.",
                              'zh-CN': "没有结果,点击清除所有条件."},
                "BB_ExportMode": {'en-US': "ExportMode", 'zh-CN': "导出模式"},
                "BB_ImportRMZ": {'en-US': "ImportRMZ", 'zh-CN': "导入RMZ"},
                "BB_Export": {'en-US': "Export", 'zh-CN': "导出"},
                "BB_MenuAll": {'en-US': "All", 'zh-CN': "全部"},
                "BB_selectgenre": {'en-US': "Select genre", 'zh-CN': "选择标签"},
                "BB_selectbunko": {'en-US': "Select bunko", 'zh-CN': "选择文库"},
                "BB_od_template": {'en-US': "Ordered by %%", 'zh-CN': "按%%排序"},
                "BB_od_name": {'en-US': "name", 'zh-CN': "书名"},
                "BB_od_numname": {'en-US': "numname", 'zh-CN': "数字编码"},
                "BB_od_rating": {'en-US': "rating", 'zh-CN': "评分"},
                "BW_rating": {'en-US': "Ratings:", 'zh-CN': "评分:"},
                "BW_progress": {'en-US': "Progress:", 'zh-CN': "进度:"},
                "BW_texter": {'en-US': "Texter", 'zh-CN': "格式化"},
                "BW_update": {'en-US': "Update", 'zh-CN': "更新"},
                "BW_lck": {'en-US': "Last Check", 'zh-CN': "上次检查"},
                "BW_simpleupd": {'en-US': "Simple Update", 'zh-CN': "一键更新"},
                "BW_detailupd": {'en-US': "Update Details", 'zh-CN': "更新细节"},
                "BW_never": {'en-US': "Never", 'zh-CN': "从未"},
                "BW_yes": {'en-US': "Update Found!", 'zh-CN': "找到更新!"},
                "BW_no": {'en-US': "No update!", 'zh-CN': "无更新!"},
                "CFG_ENABLE_PANDOC": {
                    'en-US': 'Enable pandoc for epub conversion, which will greatly boost the speed of generation. '
                             'If the picture in epub has a wrong ratio, please disable it.'
                             '\nDefault: True.',
                    'zh-CN': '启用pandoc进行epub转换，将大幅提升生成速度。若epub中图片比例异常，请禁用此选项。\n默认值: True。'
                },
                "CFG_ENABLE_ISF": {
                    'en-US': 'Enable Image Search Function. W.I.P.\nDefault: False.',
                    'zh-CN': '启用图片搜索功能。开发中。\n默认值: False。'
                },
                "CFG_COMPLICATE_SLICE_NAME": {
                    'en-US': 'Determines if the name of slice docx contains series name.\nDefault: False.',
                    'zh-CN': '决定分卷文档名称是否包含系列名称。\n默认值: False。'
                },
                "CFG_MAX_THREAD_WORKER": {
                    'en-US': 'The max threads allowed when downloading illust and text. '
                             'It\'s recommended that the value should NOT exceed 8.\nDefault: 6.',
                    'zh-CN': '下载插图和文本时允许的最大线程数。建议值不应超过8。\n默认值: 6。'
                },
                "CFG_ALWAYS_USE_DEFAULT_DOWNLOAD": {
                    'en-US': 'Always use the default download, even the book is on-shelf and has copyright. '
                             'If illust download failed, please disable this option.\nDefault: False.',
                    'zh-CN': '始终使用默认下载方式，即使书籍仍上架且具有版权。若插图下载失败，请禁用此选项。\n默认值: False。'
                },
                "CFG_ILLUSTRATION_REQUEST_SLEEP_TIME": {
                    'en-US': 'The exact time program waits between illust requests. '
                             'It\'s recommended that the value should ALWAYS exceed 0.1.\nDefault: 0.1.',
                    'zh-CN': '程序在插图请求之间的等待时间（秒）。建议值始终不低于0.1。\n默认值: 0.1。'
                },
                "CFG_TEXT_REQUEST_SLEEP_TIME": {
                    'en-US': 'The exact time program waits between non-illust requests. '
                             'It\'s recommended that the value should ALWAYS exceed 0.2.\nDefault: 0.2.',
                    'zh-CN': '程序在非插图请求之间的等待时间（秒）。建议值始终不低于0.2。\n默认值: 0.2。'
                },
                "CFG_MAX_VOLUME_THREAD_WORKER": {
                    'en-US': 'The max threads allowed when downloading volumes. '
                             'It\'s recommended that the value should NOT exceed 2.\nDefault: 2.',
                    'zh-CN': '下载分卷时允许的最大线程数。建议值不应超过2。\n默认值: 2。'
                },
                "CFG_ENABLE_BANK": {
                    'en-US': 'Enable the novel bank section. '
                             'Disabling bank will visibly shorten starting time '
                             'but will NOT stop the bank.json I/O process.'
                             '\nDefault: True.',
                    'zh-CN': '启用小说库功能。禁用书库将显著缩短启动时间，但不会停止bank.json的I/O过程。\n默认值: True。'
                },
                "CFG_AUTO_FILL_CONVERTER_INFO": {
                    'en-US': 'Enable the auto fill function in Converter section.\nDefault: True.',
                    'zh-CN': '启用转换器的自动填充功能。\n默认值: True。'
                },
                "CFG_ALLOW_WARNING_WINDOWS": {
                    'en-US': 'Enable all warning window. You may miss some auto export information if you disable it.'
                             '\nDefault: True.',
                    'zh-CN': '启用所有警告窗口。禁用后可能会错过一些自动导出信息。\n默认值: True。'
                },
                "CFG_BANK_PATH": {
                    'en-US': "The default path your book downloaded to.\nDefault: 'novel'.",
                    'zh-CN': "书籍下载的默认路径。\n默认值: 'novel'。"
                },
                "CFG_RMZ_EXPORT_PATH": {
                    'en-US': "The default path your rmz exported to.\nDefault: 'rmz'.",
                    'zh-CN': "RMZ文件导出的默认路径。\n默认值: 'rmz'。"
                },
                "CFG_RMZ_FILENAME_FORMAT": {
                    'en-US': "The format of rmz filename.\nDefault: %NUMNAME%_%TIMESTAMP%",
                    'zh-CN': "RMZ文件名的格式。\n默认值: %NUMNAME%_%TIMESTAMP%"
                },
                "CFG_DEFAULT_COVER": {
                    'en-US': "The default cover path for pandoc conversion.\nDefault: 'images/uncovered.jpg'.",
                    'zh-CN': "pandoc转换的默认封面路径。\n默认值: 'images/uncovered.jpg'。"
                },
                "CFG_LANGUAGE": {
                    'en-US': "Language of the app.\nDefault: 'en-US'.",
                    'zh-CN': "此程序使用的语言。\n默认值: 'en-US'。"
                },
                "CFG_window": {'en-US': "Config", 'zh-CN': "配置文件"},
                "CFG_save": {'en-US': "Save", 'zh-CN': "保存"},
                "CFG_apply": {'en-US': "Apply", 'zh-CN': "应用"},
                "CFG_cancel": {'en-US': "Cancel", 'zh-CN': "取消"},
                "CFG_reset": {'en-US': "Reset", 'zh-CN': "重置"},
                "CTASK_window": {'en-US': "Novel Detail", 'zh-CN': "小说细节"},
                "RT_window": {'en-US': "Novel Rating", 'zh-CN': "小说评分"},
                "PG_window": {'en-US': "Reading Progress", 'zh-CN': "阅读进度管理"},
                "UPD_window": {'en-US': "Update Details", 'zh-CN': "更新细节"},
                "DL_deatiled_download": {'en-US': "Download", 'zh-CN': "下载"},
                "CTASK_select_all": {'en-US': "Select All", 'zh-CN': "全选"},
                "CTASK_filename": {'en-US': "File name:", 'zh-CN': "文件名:"},
                "CTASK_form": {'en-US': "Form DOCX", 'zh-CN': "生成DOCX"},
                "SUCCEED": {'en-US': "Succeed!", 'zh-CN': "成功!"},
                "ALL_SUCCEED": {'en-US': "All Succeed!", 'zh-CN': "全部完成!"},
                "SELECT_FILE": {'en-US': "Select a File", 'zh-CN': "选择一个文件"},
                "SELECT_DIRECTORY": {'en-US': "Select a Directory", 'zh-CN': "选择一个文件夹"},
                "choose_RMZ": {'en-US': "Choose RMZ files", 'zh-CN': "选择多个RMZ文件"},
                "TX_Finished": {'en-US': "\nDocx Generated", 'zh-CN': "\nDOCX已生成"},
                "DL_Finished": {'en-US': "\nDownload Finished.", 'zh-CN': "\n下载已完成"},
                "CTASK_reset": {'en-US': "Reset", 'zh-CN': "重置"},
                "CTASK_save": {'en-US': "Save", 'zh-CN': "保存"},
                "": {'en-US': "", 'zh-CN': ""},
                }

    translated_text = {}
    for i in ALL_TEXT.keys():
        translated_text[i] = ALL_TEXT[i].get(code, ALL_TEXT[i]['en-US'])

    return translated_text


CONFIG = get_global_settings()
LANGUAGE = CONFIG['LANGUAGE']
LANG = translate_to(LANGUAGE)


def succeeded(info=LANG['SUCCEED']):
    print(info)
    PlaySound('dlcp.wav', 1)


CONFIG_NOTATION = {
    "ENABLE_PANDOC": LANG['CFG_ENABLE_PANDOC'],
    "ENABLE_ISF": LANG['CFG_ENABLE_ISF'],
    "COMPLICATE_SLICE_NAME": LANG['CFG_COMPLICATE_SLICE_NAME'],
    "MAX_THREAD_WORKER": LANG['CFG_MAX_THREAD_WORKER'],
    "ALWAYS_USE_DEFAULT_DOWNLOAD": LANG['CFG_ALWAYS_USE_DEFAULT_DOWNLOAD'],
    "ILLUSTRATION_REQUEST_SLEEP_TIME": LANG['CFG_ILLUSTRATION_REQUEST_SLEEP_TIME'],
    "TEXT_REQUEST_SLEEP_TIME": LANG['CFG_TEXT_REQUEST_SLEEP_TIME'],
    "MAX_VOLUME_THREAD_WORKER": LANG['CFG_MAX_VOLUME_THREAD_WORKER'],
    "ENABLE_BANK": LANG['CFG_ENABLE_BANK'],
    "AUTO_FILL_CONVERTER_INFO": LANG['CFG_AUTO_FILL_CONVERTER_INFO'],
    "ALLOW_WARNING_WINDOWS": LANG['CFG_ALLOW_WARNING_WINDOWS'],
    "BANK_PATH": LANG['CFG_BANK_PATH'],
    "RMZ_EXPORT_PATH": LANG['CFG_RMZ_EXPORT_PATH'],
    "RMZ_FILENAME_FORMAT": LANG['CFG_RMZ_FILENAME_FORMAT'],
    "DEFAULT_COVER": LANG['CFG_DEFAULT_COVER'],
    "LANGUAGE": LANG['CFG_LANGUAGE']
}
