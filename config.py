import json
from os.path import exists as ext
from os import listdir as ldr, makedirs as mkd

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
    "RMZ_FILENAME_FORMAT": "%NUMNAME%_%TMSTAMP%",
    "RMZ_FILENAME_SUFFIX": "(%NUM%)",
    "DEFAULT_COVER": "images/uncovered.jpg",
    "LANGUAGE": "en-US",
    "SHOW_FORMATED_FILE": True,
    "AUTO_UNLOCK_TEXTER": False,
    "SIMPLE_BANK_FILE": False,
    "PROXY_PORT": -1,
    "ENABLE_CLOUD_SYNC": False,
    "FTP_HOST": "",
    "FTP_PORT": 21,
    "FTP_USERNAME": "",
    "FTP_PASSWORD": "",
    "BANK_RESOLUTION": (1068, 640),
    "SCROLL_POSTION_KEEPER": 2,
    "RESIZE_DELAY": 16,
    "RENDER_RANGE": 0,
    "ADVANCED_SEARCH_TRIGGER": '',
    "BORDER_TOLERANCE": 3,
    "RLM_NEIGHBOR_RANGE": 1800,
    "SEARCH_RANGE": 2000
}


class TProgressBar:
    def __init__(self, total, length, text):
        self.total = total
        self.length = length
        self.text = text
        self.iteration = 0

    def next(self):
        self.iteration += 1
        filled_length = int(30 * self.iteration / self.total + 0.5)
        bar = '=' * filled_length + ' ' * (self.length - filled_length)
        print(f"{self.text}: [{bar}] {(self.iteration / self.total) * 100:.2f}% ({self.iteration}/{self.total})",
              end='\r')
        if self.iteration == self.total:
            print('\n')
            del self


def ordered_ldr(path, typ='.txt'):
    pre_ldrlist = ldr(path)
    b_ill = '插图' in pre_ldrlist
    if b_ill:
        pre_ldrlist.remove('插图')
    ldrlist = []
    for i in pre_ldrlist:
        try:
            ldrlist.append(int(i.split('.')[0]))
        except ValueError:
            continue
    ldrlist.sort()
    ldrlist = [str(i) + typ for i in ldrlist]
    return ldrlist, b_ill


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


def makedir(fname):
    if not ext(fname):
        mkd(fname)


def find_hmz(path, default=None):
    """

    :param default: Default return value
    :param path:
    :return: Only the filename without global path.
    """
    for i in ldr(path):
        if i.endswith('.hmz'):
            return i
    return default


def get_global_settings(reset: bool = False) -> dict:
    if reset or (not ext('config.json')):
        config = DEFAULT_SETTING
    else:
        config = read_json('config.json')
    sh_config = {i: config[i] if config.get(i, None) is not None else DEFAULT_SETTING[i] for i in DEFAULT_SETTING}

    save_json('config.json', sh_config)
    return read_json('config.json')


def modify_global_settings(global_settings):
    save_json('config.json', global_settings)


def confirm_name(name_c) -> str:
    if ':' in name_c:
        name_c = name_c.replace(':', '：')
    if '/' in name_c:
        name_c = name_c.replace('/', '／')
    if '?' in name_c:
        name_c = name_c.replace('?', '？')
    if '\\' in name_c:
        name_c = name_c.replace('\\', '＼')
    if '|' in name_c:
        name_c = name_c.replace('|', '、')
    if '<' in name_c:
        name_c = name_c.replace('<', '《')
    if '>' in name_c:
        name_c = name_c.replace('>', '》')
    if '*' in name_c:
        name_c = name_c.replace('*', '✱')
    if '\"' in name_c:
        name_c = name_c.replace('\"', '\'')
    return name_c


def translate_to(code: str) -> dict[str, str]:
    ALL_TEXT = {"VERSION": {'en-US': "LightND - Release_v8.6"},
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
                "DL_TDList": {"en-US": "To-do List", "zh-CN": "多任务"},
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
                "BB_od_bank_init": {"en-US": "Name", "zh-CN": "书名"},
                "BB_flt_bunko": {"en-US": "Select bunko", "zh-CN": "选择文库"},
                "BB_flt_genre": {"en-US": "Select genre", "zh-CN": "选择标签"},
                "TX_DetailMode": {'en-US': "DetailMode", 'zh-CN': "细节模式"},
                "DL_DetailMode": {'en-US': "DetailMode", 'zh-CN': "细节模式"},
                "BB_TextPlaceholder": {'en-US': "numname | name | writer", 'zh-CN': "数字编码 | 书名 | 作者"},
                "BB_nonesr": {'en-US': "No reselt. Click to clear all conditions.",
                              'zh-CN': "没有结果,点击清除所有条件."},
                "BB_ExportMode": {'en-US': "Manage", 'zh-CN': "管理"},
                "BB_ImportRMZ": {'en-US': "ImportRMZ", 'zh-CN': "导入RMZ"},
                "BB_Export": {'en-US': "ExportRMZ", 'zh-CN': "导出RMZ"},
                "BB_Delete": {'en-US': "Delete", 'zh-CN': "删除"},
                "BB_ConfirmDelete": {'en-US': "Confirm Delete?", 'zh-CN': "确认删除？"},
                "BB_MenuAll": {'en-US': "All", 'zh-CN': "全部"},
                "BB_selectgenre": {'en-US': "Select genre", 'zh-CN': "选择标签"},
                "BB_selectbunko": {'en-US': "Select bunko", 'zh-CN': "选择文库"},
                "BB_od_template": {'en-US': "Ordered by %%", 'zh-CN': "按%%排序"},
                "BB_od_name": {'en-US': "Name", 'zh-CN': "书名"},
                "BB_od_numname": {'en-US': "Numname", 'zh-CN': "数字编码"},
                "BB_od_rating": {'en-US': "Rating", 'zh-CN': "评分"},
                "BB_od_addtime": {'en-US': "Addtime", 'zh-CN': "入库时间"},
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
                             '\nDefault: {}.',
                    'zh-CN': '启用pandoc进行epub转换，将大幅提升生成速度。若epub中图片比例异常，请禁用此选项。\n默认值: {}。'
                },
                "CFG_ENABLE_ISF": {
                    'en-US': 'Enable Image Search Function. W.I.P.\nDefault: {}.',
                    'zh-CN': '启用图片搜索功能。开发中。\n默认值: {}。'
                },
                "CFG_COMPLICATE_SLICE_NAME": {
                    'en-US': 'Determines if the name of slice docx contains series name.\nDefault: {}.',
                    'zh-CN': '决定分卷文档名称是否包含系列名称。\n默认值: {}。'
                },
                "CFG_MAX_THREAD_WORKER": {
                    'en-US': 'The max threads allowed when downloading illust and text. '
                             'It\'s recommended that the value should NOT exceed 8.\nDefault: {}.',
                    'zh-CN': '下载插图和文本时允许的最大线程数。建议值不应超过8。\n默认值: {}。'
                },
                "CFG_ALWAYS_USE_DEFAULT_DOWNLOAD": {
                    'en-US': 'Always use the default download, even the book is on-shelf and has copyright. '
                             'If illust download failed, please disable this option.\nDefault: {}.',
                    'zh-CN': '始终使用默认下载方式，即使书籍仍上架且具有版权。若插图下载失败，请禁用此选项。\n默认值: {}。'
                },
                "CFG_ILLUSTRATION_REQUEST_SLEEP_TIME": {
                    'en-US': 'The exact time program waits between illust requests. '
                             'It\'s recommended that the value should ALWAYS exceed 0.1.\nDefault: {}.',
                    'zh-CN': '程序在插图请求之间的等待时间（秒）。建议值始终不低于0.1。\n默认值: {}。'
                },
                "CFG_TEXT_REQUEST_SLEEP_TIME": {
                    'en-US': 'The exact time program waits between non-illust requests. '
                             'It\'s recommended that the value should ALWAYS exceed 0.2.\nDefault: {}.',
                    'zh-CN': '程序在非插图请求之间的等待时间（秒）。建议值始终不低于0.2。\n默认值: {}。'
                },
                "CFG_MAX_VOLUME_THREAD_WORKER": {
                    'en-US': 'The max threads allowed when downloading volumes. '
                             'It\'s recommended that the value should NOT exceed 2.\nDefault: {}.',
                    'zh-CN': '下载分卷时允许的最大线程数。建议值不应超过2。\n默认值: {}。'
                },
                "CFG_ENABLE_BANK": {
                    'en-US': 'Enable the novel bank section. '
                             'Disabling bank will visibly shorten starting time '
                             'but will NOT stop the bank.json I/O process.'
                             '\nDefault: {}.',
                    'zh-CN': '启用小说库功能。禁用书库将显著缩短启动时间，但不会停止bank.json的I/O过程。\n默认值: {}。'
                },
                "CFG_AUTO_FILL_CONVERTER_INFO": {
                    'en-US': 'Enable the auto fill function in Converter section.\nDefault: {}.',
                    'zh-CN': '启用转换器的自动填充功能。\n默认值: {}。'
                },
                "CFG_ALLOW_WARNING_WINDOWS": {
                    'en-US': 'Enable all warning window. You may miss some auto export information if you disable it.'
                             '\nDefault: {}.',
                    'zh-CN': '启用所有警告窗口。禁用后可能会错过一些自动导出信息。\n默认值: {}。'
                },
                "CFG_BANK_PATH": {
                    'en-US': "The default path your book downloaded to.\nDefault: '{}'.",
                    'zh-CN': "书籍下载的默认路径。\n默认值: '{}'。"
                },
                "CFG_RMZ_EXPORT_PATH": {
                    'en-US': "The default path your rmz exported to.\nDefault: '{}'.",
                    'zh-CN': "RMZ文件导出的默认路径。\n默认值: '{}'。"
                },
                "CFG_RMZ_FILENAME_FORMAT": {
                    'en-US': "The format of rmz filename.\nDefault: {}",
                    'zh-CN': "RMZ文件名的格式。\n默认值: {}"
                },
                "CFG_RMZ_FILENAME_SUFFIX": {
                    'en-US': "The format of rmz filename suffix.\nDefault: {}",
                    'zh-CN': "RMZ文件名后缀的格式。\n默认值: {}"
                },
                "CFG_DEFAULT_COVER": {
                    'en-US': "The default cover path for pandoc conversion.\nDefault: '{}'.",
                    'zh-CN': "pandoc转换的默认封面路径。\n默认值: '{}'。"
                },
                "CFG_LANGUAGE": {
                    'en-US': "Language of the app.\nDefault: '{}'.",
                    'zh-CN': "此程序使用的语言。\n默认值: '{}'。"
                },
                "CFG_SHOW_FORMATED_FILE": {
                    'en-US': "Mark options in Texter as finished if corresponding formated files exists."
                             "\nDefault: {}.",
                    'zh-CN': "为已存在对应文件的格式器选项打钩。\n默认值: {}。"
                },
                "CFG_AUTO_UNLOCK_TEXTER": {
                    'en-US': "Auto unlock the option restriction in Texter.\nDefault: {}.",
                    'zh-CN': "自动解锁格式器选项限制。\n默认值: {}。"
                },
                "CFG_SIMPLE_BANK_FILE": {
                    'en-US': "Toggle if the bank.json is more readable(False) or space-efficient(True)."
                             "\nDefault: {}.",
                    'zh-CN': "切换bank.json存储模式，使之更易读（False）或更省空间（True）。\n默认值: {}。"
                },
                "CFG_PROXY_PORT": {
                    'en-US': "The proxy port of GET requests. -1 for not enabled, 0 for partially enabled."
                             "\nDefault: {}.",
                    'zh-CN': "GET请求的代理端口。设置为-1时不起效，0时部分起效。\n默认值: {}。"
                },
                "CFG_BANK_RESOLUTION": {
                    'en-US': "The default resolution of bank page."
                             "\nDefault: {} x {}.",
                    'zh-CN': "书库页的默认分辨率。\n默认值: {} x {}。"
                },
                "CFG_SCROLL_POSTION_KEEPER": {
                    'en-US': "The mode how bank page save your scroll progress."
                             "\nDefault: {}.",
                    'zh-CN': "书库页存储滚动进度的模式。\n默认值: {}。"
                },
                "CFG_RESIZE_DELAY": {
                    'en-US': "Dicide how often the bank page render while resizing."
                             "\nDefault: {}.",
                    'zh-CN': "决定拖动书库页大小时的渲染延迟。\n默认值: {}。"
                },
                "CFG_RENDER_RANGE": {
                    'en-US': "Dicide how many more rows of book widget should be rendered dynamically."
                             "\nDefault: {}.",
                    'zh-CN': "决定额外动态渲染的图书组件行数。\n默认值: {}。"
                },
                "CFG_ADVANCED_SEARCH_TRIGGER": {
                    'en-US': "Use Advanced Search if the search text begin with this string."
                             "\nDefault: {}.",
                    'zh-CN': "如果搜索文本以该字符串开头，触发高级搜索。\n默认值: {}。"
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
                "TASK_type_TEXTER": {'en-US': "DOCX Generation", 'zh-CN': "DOCX生成"},
                "TASK_type_EPUB": {'en-US': "EPUB Conversion", 'zh-CN': "EPUB转换"},
                "TASK_type_DOWNLOADER": {'en-US': "Novel Download", 'zh-CN': "小说下载"},
                "MIS_Window": {'en-US': "Missions Window", 'zh-CN': "任务视窗"},
                "MIS_button": {'en-US': "Tasks", 'zh-CN': "任务视窗"},
                "TX_Unlock": {'en-US': "Unlock", 'zh-CN': "解锁"},
                "TODOLIST_window": {'en-US': "To-do List", 'zh-CN': "任务清单"},
                "CLOUD_TABNAME": {'en-US': "Cloud Sync", 'zh-CN': "云同步"},
                "CLOUD_ENABLE": {'en-US': "Enable Cloud Sync", 'zh-CN': "启用云同步"},
                "CLOUD_HOST": {'en-US': "FTP Host:", 'zh-CN': "FTP主机:"},
                "CLOUD_PORT": {'en-US': "Port:", 'zh-CN': "端口:"},
                "CLOUD_USERNAME": {'en-US': "Username:", 'zh-CN': "用户名:"},
                "CLOUD_PASSWORD": {'en-US': "Password:", 'zh-CN': "密码:"},
                "CLOUD_TEST": {'en-US': "Test Connection && Save", 'zh-CN': "测试连接并保存"},
                "CLOUD_UPLOAD": {'en-US': "Upload to Cloud", 'zh-CN': "上传到云端"},
                "CLOUD_DOWNLOAD": {'en-US': "Download from Cloud", 'zh-CN': "从云端下载"},
                "CLOUD_BACKUP_CB": {'en-US': "Backup Local Library", 'zh-CN': "创建书库本地备份"},
                "CLOUD_DELETE_CB": {'en-US': "Delete removed books", 'zh-CN': "删除已移除的书籍"},
                "CLOUD_STATUS_IDLE": {'en-US': "Idle", 'zh-CN': "就绪"},
                "CLOUD_STATUS_CONNECTING": {'en-US': "Testing connection...", 'zh-CN': "正在测试连接..."},
                "CLOUD_STATUS_CONNECTED": {'en-US': "Connection successful, settings saved.", 'zh-CN': "连接成功，设置已保存。"},
                "CLOUD_STATUS_FAILED": {'en-US': "Connection failed", 'zh-CN': "连接失败"},
                "CLOUD_STATUS_UPLOADING": {'en-US': "Uploading...", 'zh-CN': "正在上传..."},
                "CLOUD_STATUS_DOWNLOADING": {'en-US': "Downloading...", 'zh-CN': "正在下载..."},
                "CLOUD_STATUS_UPLOADED": {'en-US': "Upload complete", 'zh-CN': "上传完成"},
                "CLOUD_STATUS_DOWNLOADED": {'en-US': "Download complete, bank refreshed.", 'zh-CN': "下载完成，书库已刷新。"},
                "CLOUD_STATUS_ERROR": {'en-US': "Error", 'zh-CN': "错误"},
                "CLOUD_BACKUP_CREATED": {'en-US': "Local backup created", 'zh-CN': "本地备份已创建"},
                "CLOUD_DOWNLOADING_NEW": {'en-US': "Downloading new books...", 'zh-CN': "正在下载新书..."},
                "CLOUD_DELETING_REMOVED": {'en-US': "Deleting removed books...", 'zh-CN': "正在删除已移除的书籍..."},
                "CLOUD_N_BOOKS_ADDED": {'en-US': "{} new book(s) to download.", 'zh-CN': "{} 本新书待下载。"},
                "CLOUD_N_BOOKS_REMOVED": {'en-US': "{} book(s) to delete.", 'zh-CN': "{} 本书待删除。"},
                "CLOUD_BOOKS_MERGED": {'en-US': "{} local book(s) merged.", 'zh-CN': "{} 本本地书籍已合并。"},
                "CLOUD_ERR_EMPTY_HOST": {'en-US': "FTP host address cannot be empty.", 'zh-CN': "FTP主机地址不能为空。"},
                "CLOUD_ERR_REMOTE_NOT_FOUND": {'en-US': "Remote file not found. Please upload first.",
                                               'zh-CN': "远程文件未找到，请先上传。"},
                "CLOUD_ERR_BANK_NOT_FOUND": {'en-US': "Local bank.json not found. Nothing to upload.",
                                             'zh-CN': "本地bank.json未找到，无内容可上传。"},
                "CLOUD_ERR_INVALID_JSON": {'en-US': "Downloaded file is not valid JSON. Aborted.",
                                           'zh-CN': "下载的文件不是有效的JSON格式，已中止。"},
                "CFG_ENABLE_CLOUD_SYNC": {
                    'en-US': "Enable cloud synchronization via FTP. Configure server in the Cloud Sync tab.\nDefault: "
                             "{}.",
                    'zh-CN': "启用基于远程FTP云同步。请在云同步标签页中配置FTP服务器。\n默认值: {}。"
                },
                "CFG_NONE": {
                    'en-US': "No Info for {}.",
                    'zh-CN': "无 {} 信息。"
                },
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


CONFIG_NOTATION = {i: LANG.get(f'CFG_{i}', LANG['CFG_NONE']).format(*((DEFAULT_SETTING[i],) if not isinstance(DEFAULT_SETTING[i], tuple) else DEFAULT_SETTING[i])) for i in DEFAULT_SETTING}  # NOQA
