from ui.ui_bookwidget import BookWidget

# LightND 开发者指南

> 版本：Release v8.5.3  
> 最后更新：2026-05-13

---

## 目录

1. [项目简介](#1-项目简介)
2. [技术栈](#2-技术栈)
3. [环境搭建](#3-环境搭建)
4. [项目结构详解](#4-项目结构详解)
5. [核心模块说明](#5-核心模块说明)
6. [数据模型](#6-数据模型)
7. [数据流与生命周期](#7-数据流与生命周期)
8. [UI 架构](#8-ui-架构)
9. [配置系统](#9-配置系统)
10. [国际化 (i18n)](#10-国际化-i18n)
11. [RMZ 文件格式](#11-rmz-文件格式)
12. [线程模型](#12-线程模型)
13. [测试与调试](#13-测试与调试)
14. [版本历史摘要](#14-版本历史摘要)

---

## 1. 项目简介

LightND 是一款基于 **PySide6**(QT) 构建的 Windows 桌面应用程序，面向轻小说读者，提供从在线书库下载、文本格式化、电子书转换到阅读进度管理的完整工作流。

### 核心功能模块

| 模块                   | 功能                                           |
|----------------------|----------------------------------------------|
| **下载器 (Downloader)** | 按数字编码下载轻小说，支持逐卷/整本模式，支持插图下载                  |
| **格式器 (Texter)**     | 将下载的 txt 文件格式化为 DOCX，支持分卷/合集两种模式             |
| **转换器 (Converter)**  | DOCX → EPUB → AZW3 格式转换（依赖 pandoc / calibre） |
| **书库 (BookBank)**    | 浏览、排序、筛选、搜索已下载书籍，支持收藏筛选                      |
| **阅读进度**             | 按卷/章节粒度追踪阅读进度                                |
| **评分系统**             | 5 星评分（每半星一档，共 10 级），按卷独立评分                   |
| **RMZ 导入/导出**        | 自定义格式持久化阅读数据，支持跨设备迁移                         |
| **多任务清单**            | 批量下载管理，支持从文件导入任务列表                           |

### 架构分层

```
┌──────────────────────────────────────────────┐
│  UI 层 (ui/)                                 │
│  ┌──────────┬──────────┬──────────┬────────┐ │
│  │MainWindow│BookWidget│ConfigWin │DetailWin││
│  └──────────┴──────────┴──────────┴────────┘ │
├──────────────────────────────────────────────┤
│  自定义控件层 (BySide.py)                     │
│  ClickableLabel | WidgetGrid | ScrollField   │
├──────────────────────────────────────────────┤
│  业务逻辑层                                   │
│  ┌──────────┬──────────┬──────────┬────────┐ │
│  │download   │txtprocess│bookbank  │prg_    │ │
│  │process.py │.py       │.py       │export/ │ │
│  │           │          │          │import  │ │
│  └──────────┴──────────┴──────────┴────────┘ │
├──────────────────────────────────────────────┤
│  领域模型层 (book_struct.py)                  │
│  Book → BankedBook → HmzedBook → BookLuxury  │
├──────────────────────────────────────────────┤
│  基础设施层                                   │
│  ┌──────────┬──────────┬──────────┐          │
│  │netwk.py  │config.py │BySide.py │          │
│  │(HTTP/HTML│(配置/i18n)│(Qt工具)  │          │
│  └──────────┴──────────┴──────────┘          │
├──────────────────────────────────────────────┤
│  外部依赖                                     │
│  PySide6 | BeautifulSoup4 | python-docx      │
│  Pillow  | pandoc/calibre | requests         │
└──────────────────────────────────────────────┘
```

---

## 2. 技术栈

### 运行时依赖

| 包                  | 版本       | 用途                        |
|--------------------|----------|---------------------------|
| PySide6            | 6.9.2    | Qt 框架的 Python 绑定，GUI 构建   |
| PySide6_Addons     | 6.9.2    | Qt 附加模块                   |
| PySide6_Essentials | 6.9.2    | Qt 核心模块                   |
| shiboken6          | 6.9.2    | PySide6 的 C++ 绑定生成器       |
| beautifulsoup4     | 4.13.5   | HTML 解析                   |
| lxml               | 6.0.1    | XML/HTML 高性能解析器           |
| requests           | 2.32.5   | HTTP 客户端                  |
| python-docx        | 1.2.0    | DOCX 文件生成                 |
| Pillow             | 11.3.0   | 图像处理                      |
| pypinyin           | 0.55.0   | 中文拼音排序                    |
| python-dateutil    | 2.9.0    | 日期解析                      |
| pyYAML             | 6.0.2    | YAML 元数据生成（pandoc）        |
| Jinja2             | 3.1.6    | 模板引擎（pandoc 元数据）          |
| MarkupSafe         | 3.0.3    | Jinja2 的安全转义依赖            |
| statsmodels        | 0.14.5   | 统计建模（插图搜索用）               |
| soupsieve          | 2.7      | CSS 选择器（BeautifulSoup 依赖） |
| networkx           | 3.5      | 图数据结构（间接依赖）               |
| mpmath             | 1.3.0    | 高精度数学（间接依赖）               |
| sympy              | 1.14.0   | 符号数学（间接依赖）                |
| packaging          | 25.0     | 版本号解析（间接依赖）               |
| certifi            | 2025.8.3 | SSL 证书                    |
| charset-normalizer | 3.4.3    | 字符编码检测                    |
| idna               | 3.10     | 国际化域名                     |
| urllib3            | 2.5.0    | HTTP 底层库                  |
| typing_extensions  | 4.15.0   | 类型注解扩展                    |

### 外部工具依赖

| 工具                      | 用途                 | 配置项             |
|-------------------------|--------------------|-----------------|
| pandoc                  | DOCX → EPUB 转换（推荐） | `ENABLE_PANDOC` |
| calibre (ebook-convert) | EPUB → AZW3 转换     | —               |

---

## 3. 环境搭建

### 前置要求

- Python 3.12+
- Windows 操作系统（PySide6 依赖）
- （可选）pandoc 用于 EPUB 生成
- （可选）calibre 用于 AZW3 生成

### 安装步骤

```bash
# 1. 克隆仓库
git clone <repository-url>
cd LightND

# 2. 创建虚拟环境
python -m venv venv
# Windows 激活：
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python LightNV.py
```

首次运行会自动在根目录生成 `config.json`（默认配置）和 `bank.json`（书库索引）。下载的书籍默认存储在 `novel/` 目录下。

### 开发注意事项

- `.gitignore` 排除了 `bank.json`、`config.json`、`novel/`、`rmz/` 等运行时生成的文件。若需共享测试数据，请从备份中恢复。
- UI 文件（`ui/*.py`）由 Qt Designer 生成的 `.ui` 文件经 `pyuic6` 转换而来。转换命令封装在 `txtprocess.py:ui_2_py()` 函数中。

---

## 4. 项目结构详解

```
LightND/
│
├── LightNV.py              # ★ 应用入口 & 主窗口控制器
│   ├── MainWindow          # 主窗口类，管理所有 UI 信号/槽连接
│   ├── Downloader          # 下载参数封装（numname, content, mode 等）
│   ├── Texter              # 格式化参数封装 & 执行
│   ├── Todolist            # 多任务清单管理
│   ├── WorkerRunnable      # QRunnable 封装，用于线程池任务提交
│   └── activate()          # 启动函数：创建窗口 → 渲染书库 → 连接信号
│
├── config.py               # ★ 全局配置 & 国际化
│   ├── DEFAULT_SETTING     # 默认配置字典（20 项配置）
│   ├── get_global_settings()  # 读取/初始化 config.json
│   ├── modify_global_settings() # 写入 config.json
│   ├── translate_to()      # 国际化翻译函数
│   ├── ALL_TEXT            # 全部文本的翻译映射表
│   ├── CONFIG_NOTATION     # 配置项说明文本映射
│   ├── confirm_name()      # 文件名非法字符替换
│   ├── find_hmz()          # 在目录中查找 .hmz 文件
│   └── succeeded()         # 操作成功提示（打印 + 音效）
│
├── book_struct.py          # ★ 领域模型层
│   ├── Book                # 基类：numname + name + writer
│   ├── BankedBook(Book)    # 书库条目（存储在 bank.json）
│   ├── HmzedBook(Book)     # 书籍元数据（存储在 *.hmz）
│   └── BookLuxury          # 附加数据（prg, rtg, fav, lck）
│
├── bookbank.py             # ★ 书库管理层
│   ├── read_bank_file()    # 读取 bank.json → List[BankedBook]
│   ├── save_as_bank()      # 序列化并写入 bank.json
│   ├── generate_book_bank()# 扫描 novel/ 目录重建书库
│   ├── add_to_bank()       # 添加/更新书籍记录
│   ├── read_hmz_par()      # 读取并缓存 .hmz 文件
│   ├── get_global_hmzfiles() # 多线程预加载全部 .hmz
│   ├── update_hmzfiles()   # 刷新 .hmz 缓存
│   ├── filter_bw()         # 按文库/标签筛选
│   ├── order_bw()          # 按名称/编码/时间排序
│   ├── order_bw_ranked()   # 按评分排序
│   ├── search_bw()         # 关键词搜索
│   ├── filter_liked_bw()   # 收藏筛选
│   ├── get_all_info()      # 获取全部文库/标签枚举值
│   └── getBookFromNumname()# 按编码查找书籍
│
├── netwk.py                # ★ 网络请求层
│   ├── GetRq               # HTTP 请求封装类
│   │   ├── request()       # 发起 GET 请求（支持代理）
│   │   ├── book_page_parser()    # 解析书籍信息页
│   │   ├── index_page_parser()   # 解析目录页
│   │   ├── text_page_parser()    # 解析章节正文
│   │   ├── image_page_parser()   # 获取单张图片
│   │   ├── image_folder_page_parser() # 获取插图文件夹
│   │   ├── thumbrail_page_parser()    # 获取缩略图
│   │   └── run()           # 统一入口，按类型分发
│   ├── get_alllist()       # 获取书籍全部卷/章节列表
│   └── get_fullinfo()      # 获取完整书籍信息（合并书页+目录页）
│
├── downloadprocess.py      # ★ 下载流程层
│   ├── DownloadTask        # 下载任务类
│   │   ├── __init__()      # 初始化：获取元数据，创建 BankedBook/HmzedBook
│   │   ├── pre_download()  # 下载缩略图 + 入库
│   │   ├── download()      # 主下载流程：路由到详细/默认下载
│   │   ├── detailedDownload()    # 逐卷下载（多线程）
│   │   ├── default_download()    # 整本下载（单文件）
│   │   ├── download_volume()     # 下载单卷
│   │   ├── downloadslice()       # 按选择下载指定卷
│   │   ├── download_volumes_from_allnet() # 更新时批量下载
│   │   ├── process_page()        # 处理单页（章节或插图）
│   │   ├── read_page()           # 下载并保存单章文本
│   │   ├── illu_page()           # 下载并保存插图
│   │   ├── txt_split()           # 拆分合并的文本为分卷/章节
│   │   ├── mergeToVol()          # 卷内章节合并
│   │   └── mergeToSeries()       # 系列合并
│   ├── get_img()           # 获取/下载书籍缩略图
│   ├── save_file()         # 保存文本文件
│   └── save_img()          # 保存图片文件
│
├── txtprocess.py           # ★ 文本格式化 & 转换层
│   ├── HFolder             # 书籍文件夹处理类
│   │   ├── formfd()        # 生成 DOCX（mode=1 合集, mode=0 分卷）
│   │   ├── formepub()      # DOCX → EPUB
│   │   ├── formazw3()      # EPUB → AZW3
│   │   ├── formslice()     # 生成自定义卷范围的 DOCX
│   │   ├── form_each_volume()    # 处理单卷内容
│   │   ├── form_text()           # 排版正文（标题 + 段落）
│   │   └── form_pict_fdr()       # 排版插图
│   ├── Novel_docx()        # 创建标准格式的 Document 对象
│   ├── put_headings()      # 添加标题（含字体设置）
│   ├── put_title_page()    # 添加扉页
│   ├── put_pict()          # 插入图片（自适应尺寸）
│   ├── convert_to_epub()   # 使用 calibre 转换 EPUB
│   ├── convert_to_azw3()   # 使用 calibre 转换 AZW3
│   ├── convert2epub_pandoc() # 使用 pandoc 转换 EPUB
│   ├── generate_yaml()     # 生成 pandoc 元数据 YAML
│   ├── get_cover_from()    # 从插图文件夹获取封面
│   └── NotAHFolderError    # 非书籍文件夹异常
│
├── BySide.py               # ★ 自定义 Qt 控件库
│   ├── ClickableLabel      # 支持左/右键点击信号的 QLabel
│   ├── DPushButton         # 支持左/右键区分的 QPushButton
│   ├── AdvButtonGroup      # 增强的 QButtonGroup
│   ├── ScrollField         # 垂直滚动区域（动态添加/移除控件）
│   ├── WidgetGrid          # 网格布局容器（用于书库卡片排列）
│   ├── BoundWidgetGrid     # 固定数量的网格布局
│   ├── GroupedWidgets      # 分组控件容器
│   ├── ExitButton          # 预配置的退出按钮
│   ├── DefaultFont         # 预配置的默认字体
│   ├── BinaryCheckBox      # 二态复选框（禁用三态）
│   ├── AbstractSignalBond  # 信号绑定抽象（防止重入）
│   └── extand_list_to()    # 二维列表扩展工具函数
│
├── prg_export.py           # RMZ 导出模块
│   ├── save_as_rmz()       # 导出为 .rmz 文件
│   ├── read_from_rmz()     # 从 .rmz 文件读取
│   ├── parse_rmz_format()  # 解析文件名模板
│   └── tag_replace()       # 替换模板标签
│
├── prg_import.py           # RMZ 导入模块
│   ├── RmzImportWindow     # 导入对比窗口
│   ├── BookTitle           # 书籍标题组件
│   ├── PrgWidget           # 进度展示/编辑组件
│   ├── PrgChapterWidget    # 单章进度复选框
│   └── RtgWidget           # 评分展示/编辑组件
│
├── ui/                     # UI 组件目录
│   ├── ui_LightNV.py       # 主窗口布局
│   ├── ui_bookwidget.py    # 书库书籍卡片
│   ├── ui_config.py        # 配置编辑窗口
│   ├── ui_ctask.py         # 细节窗口
│   ├── ui_rating.py        # 星级评分 & 收藏控件
│   ├── ui_missions.py      # 任务进度窗口
│   ├── ui_tdl.py           # 多任务编辑窗口
│   └── ui_update.py        # 更新细节窗口
│
├── checklist.json          # 默认下载清单
├── appending.css           # EPUB CSS 注入
├── dlcp.wav                # 操作完成提示音
├── requirements.txt        # Python 依赖
├── images/                 # 图标 & 默认资源
│   ├── icon.ico            # 应用图标
│   ├── dft.png             # 默认封面占位
│   ├── *.png               # 各种 UI 图标
│   └── thumbnails/         # 书籍缩略图缓存
├── novel/                  # 默认下载目录 (gitignore)
└── rmz/                    # 默认导出目录 (gitignore)
```

---

## 5. 核心模块说明

### 5.1 LightNV.py — 应用主入口

`LightNV.py` 包含 `MainWindow` 类，是整个应用的枢纽。该类负责：

- **UI 初始化**：通过 `Ui_MainWindow.setupUi()` 构建界面
- **信号/槽连接**：`set_connection()` 方法集中管理全部信号绑定
- **下载流程控制**：`downloadStart()` → `downloadSingle()` / `downloadMuti()`
- **格式化流程控制**：`textformer()` → `HFolder` 方法链
- **书库状态管理**：`render_book_bank()`、`process_bw_list()`、排序/筛选参数维护
- **线程池调度**：通过 `QThreadPool` + `WorkerRunnable` 提交异步任务

关键实例变量：

```python
bb_param = ['', '', [1, 1], '']  # [genre, bunko, [order, sign], search_key]
bb_liked = 0                        # 0=全部, 1=收藏, 2=未收藏
bw_list: list[BookWidget]                # 全部书籍卡片列表
```

### 5.2 netwk.py — 网络请求与解析

`GetRq` 类封装了完整的 HTTP 请求和 HTML 解析逻辑。核心设计：

- **统一入口**：`run(_type)` 方法根据类型标识符分发到不同的解析器
- **代理支持**：通过 `PROXY_PORT` 配置项控制三级代理行为（-1 不设置 / 0 部分 / >0 全部）
- **请求节流**：`IRST`（插图请求间隔，默认 0.1s）和 `TRST`（文本请求间隔，默认 0.2s）
- **多线程下载插图**：`image_folder_page_parser()` 使用 `ThreadPoolExecutor` 并行获取插图

类型标识符对照：

| `_type` | 功能      | 返回值                                             |
|---------|---------|-------------------------------------------------|
| `'i'`   | 解析目录页   | `(allnet, allname)`                             |
| `'b'`   | 解析书籍信息页 | `(name, author, desc, genre, bunko, copyright)` |
| `'t'`   | 解析章节正文  | `str`                                           |
| `'p'`   | 获取图片    | `bytes`                                         |
| `'m'`   | 获取缩略图   | `bytes`                                         |
| `'f'`   | 获取插图文件夹 | `list[bytes]`                                   |
| `'w'`   | 获取整本下载页 | `str`                                           |

### 5.3 downloadprocess.py — 下载流程

`DownloadTask` 类是下载操作的核心抽象。一次下载的生命周期：

```
__init__()               解析元数据，创建 HmzedBook 和 BankedBook
    ↓
pre_download()           下载缩略图，调用 add_to_bank() 入库
    ↓
download()               路由决策：
    ├── copyright=False → default_download() → txt_split()
    ├── AUDD=True       → default_download() → txt_split()
    └── 正常            → detailedDownload()
                              ↓
                         逐卷循环 download_volume()
                              ↓
                         ThreadPoolExecutor 多线程 process_page()
```

### 5.4 txtprocess.py — 格式化与转换

`HFolder` 类封装对已下载书籍文件夹的操作。格式化链：

```
TXT 文件（按卷/章节组织）
    ↓ formfd(mode=1)
系列 DOCX（{name}.docx）
    ↓ formepub(mode=1)
系列 EPUB（{name}.epub）
    ↓ formazw3(mode=1)
系列 AZW3（{name}.azw3）

TXT 文件
    ↓ formfd(mode=0)
分卷 DOCX（Volume_docx/{vol}.docx）
    ↓ formepub(mode=0)
分卷 EPUB（Volume_epub/{vol}.epub）
    ↓ formazw3(mode=0)
分卷 AZW3（Volume_azw3/{vol}.azw3）

TXT 文件（自定义卷范围）
    ↓ formslice(ind, name)
切片 DOCX（Slices/{name}.docx）
```

EPUB 生成支持两条路径：
- **pandoc**（`ENABLE_PANDOC=True`）：速度快，通过 YAML 元数据注入封面和元信息
- **calibre ebook-convert**（`ENABLE_PANDOC=False`）：兼容性好，通过命令行参数

### 5.5 bookbank.py — 书库管理

核心数据文件：
- **`bank.json`**：书库索引，存储 `List[BankedBook]`。通过 `SIMPLE_BANK_FILE` 配置项控制格式（易读 vs 紧凑）。
- **`{numname}.hmz`**：每本书的元数据文件，存储 `HmzedBook`，包含全部卷/章节信息。

重要函数说明：

| 函数                      | 说明                                    |
|-------------------------|---------------------------------------|
| `read_bank_file()`      | 读取 bank.json，自动重建缺失的书库                |
| `generate_book_bank()`  | 扫描 novel/ 目录，从各 .hmz 文件重建 bank.json   |
| `get_global_hmzfiles()` | 多线程预加载全部 .hmz 文件（启动时调用）               |
| `add_to_bank()`         | 添加书籍，自动检测书名变更并导出旧数据为 RMZ              |
| `filter_bw()`           | 按指定字段筛选（3=bunko, 4=genre）             |
| `order_bw()`            | 按指定字段排序（0=numname, 1=name, 2=addtime） |
| `search_bw()`           | 模糊搜索（拼音 + 原文）                         |

### 5.6 BySide.py — 自定义控件库

提供项目特有的 Qt 控件扩展：

| 控件                   | 基类          | 增强功能                                |
|----------------------|-------------|-------------------------------------|
| `ClickableLabel`     | QLabel      | 左/右键点击信号分离（`lclicked` / `rclicked`） |
| `DPushButton`        | QPushButton | 左/右键点击区分                            |
| `ScrollField`        | QScrollArea | 动态 add/remove Widget，自动布局           |
| `WidgetGrid`         | QWidget     | 自适应网格，自动填充空白位置                      |
| `BoundWidgetGrid`    | QWidget     | 固定数量的网格布局，用于渲染优化                    |
| `BinaryCheckBox`     | QCheckBox   | 强制二态（禁用 PartiallyChecked）           |
| `AbstractSignalBond` | —           | 防止并发的信号绑定封装                         |

---

## 6. 数据模型

### 6.1 类层级

```
Book (book_struct.py)
├── 字段: numname: str, name: str, writer: str
├── 方法: __eq__ (按 numname), __contains__ (按 numname/name/writer)
│
├── BankedBook(Book)
│   ├── 字段: bunko, genre, addtime, directory, lux: BookLuxury
│   ├── 方法: toDict(), __getitem__ (支持 str/int 索引)
│   └── 存储: bank.json 中的一条记录
│
└── HmzedBook(Book)
    ├── 字段: allnet, allname, description
    ├── 方法: toDict(), save_at(path)
    └── 存储: {numname}.hmz 文件

BookLuxury (dataclass)
├── 字段: prg: list, rtg: dict, fav: int, lck: int
├── 方法: toDict(), __bool__
└── 嵌入在: BankedBook.lux
```

### 6.2 数据格式

**bank.json 示例（SIMPLE_BANK_FILE=False，易读模式）：**
```json
[
  {
    "numname": "2784",
    "name": "弹珠汽水瓶里的千岁同学",
    "writer": "裕梦",
    "bunko": "GAGAGA文库",
    "genre": ["校园", "恋爱", "日常"],
    "addtime": 1711000000,
    "lux": {
      "prg": [["第一卷", "第一章", "第二章"], ["第二卷", "第一章"]],
      "rtg": {"第一卷": 10, "第二卷": 10},
      "fav": 1,
      "lck": 1711000000
    },
    "directory": ""
  }
]
```

**.hmz 文件示例：**
```json
{
  "numname": "2784",
  "name": "弹珠汽水瓶里的千岁同学",
  "writer": "裕梦",
  "allnet": [
    ["第一卷", "/novel/1/2784/...", "/novel/1/2784/...", "插图"],
    ["第二卷", "/novel/1/2784/...", "/novel/1/2784/..."]
  ],
  "allname": [
    ["第一卷", "序章", "第一章", "第二章", "插图"],
    ["第二卷", "序章", "第一章"]
  ],
  "description": "在漫长的暑假即将开始之时……"
}
```

### 6.3 索引访问约定

`BankedBook.__getitem__` 支持数字和字符串索引：

| 索引              | 字段    |
|-----------------|-------|
| 0 / `'numname'` | 数字编码  |
| 1 / `'name'`    | 书名    |
| 2 / `'writer'`  | 作者    |
| 3 / `'bunko'`   | 文库    |
| 4 / `'genre'`   | 标签列表  |
| 5 / `'addtime'` | 入库时间戳 |

---

## 7. 数据流与生命周期

### 7.1 应用启动流程

```
__main__ → timetest(activate)
    ↓
activate()
    ├── MainWindow.__init__()
    │     ├── Ui_MainWindow.setupUi()       # 构建 UI
    │     ├── read_bank_file()              # 加载书库
    │     │     └── (首次) generate_book_bank() # 扫描 novel/ 重建
    │     ├── get_all_info()                # 获取文库/标签枚举
    │     ├── 创建 BookWidget 列表
    │     └── 初始化信号连接
    ├── window.render_book_bank()           # 首屏渲染（前 15 本）
    ├── window.show()                       # 显示窗口
    └── window.set_connection()             # 连接全部信号/槽
```

### 7.2 下载一本书的完整数据流

```
用户输入: numname="2784"
    ↓
downloadStart()
    ├── 从 UI 收集参数至 Downloader 对象
    └── 提交 WorkerRunnable(downloadSingle, "2784")
        ↓
downloadSingle("2784")
    ├── DownloadTask("2784", ...).__init__()
    │     ├── get_fullinfo("2784", return_type=0)
    │     │     ├── GetRq(.../index.htm).run('i') → allnet, allname
    │     │     └── GetRq(.../book/2784.htm).run('b') → name, writer, ...
    │     ├── HmzedBook(...)  ← 元数据
    │     └── BankedBook(...) ← 书库条目
    ├── task.download()
    │     ├── pre_download()           # 缩略图 + 入库
    │     └── detailedDownload()       # 逐卷下载
    │           └── for each volume:
    │                 download_volume(i)
    │                   └── ThreadPoolExecutor:
    │                         for each chapter:
    │                           process_page(vol, ch)
    │                             ├── read_page() → 保存 .txt
    │                             └── illu_page() → 下载插图
    ├── handleWarning(task.getWarning())  # 处理警告
    └── textformer(task.hmzbook.name)     # 自动格式化
          └── HFolder.format_chain → DOCX/EPUB/AZW3
```

### 7.3 书库刷新流程

```
用户点击刷新按钮
    ↓
refresh_bw_list()
    ├── get_all_info()                  # 获取最新文库/标签
    ├── read_bank_file()                # 重新读取 bank.json
    ├── update_hmzfiles()               # 多线程刷新 .hmz 缓存
    ├── 比对现有 BookWidget 列表与最新 bank：
    │     ├── 新增的书 → 创建新 BookWidget
    │     └── 已有的书 → update_hmzinfo() 更新元数据显示
    └── render_book_bank(process_bw_list())  # 按当前参数重新渲染
```

### 7.4 RMZ 导入/导出流程

**导出：**
```
用户点击导出 → setExportMode(True)
    ↓ 勾选要导出的书
点击导出按钮 → handleExport()
    ↓ 遍历 BookWidget 列表
save_as_rmz(1, bankinfo, RMZ_EXPORT_PATH, RMZ_FILENAME_FORMAT)
    ↓
parse_rmz_format() → 替换 %NUMNAME%, %TMSTAMP%, %BKNAME% 等标签
    ↓ 处理文件名冲突（自动递增后缀）
写入 .rmz 文件: b'RHMZ' + b'BANK' + JSON
```

**导入：**
```
用户选择 .rmz 文件 → handleImport()
    ↓
read_from_rmz(filename) → (data, type)
    ↓
handleSingleImport() → 按 numname 匹配当前书库
    ↓
比对 prg/rtg 差异 → RmzImportWindow 左右对比
    ↓ 用户确认
更新 bank.json 中的 lux 数据
```

---

## 8. UI 架构

### 8.1 主窗口结构

MainWindow 使用 `QTabWidget` 管理三个标签页：

| 索引 | 标签         | 功能                       | 窗口尺寸     |
|----|------------|--------------------------|----------|
| 0  | Downloader | 下载器 + 配置                 | 660×380  |
| 1  | Texter     | 格式器                      | 660×380  |
| 2  | Converter  | 转换器                      | 660×380  |
| 3  | BookBank   | 书库（需 ENABLE_BANK）        | 1068×640 |
| 4  | CloudSync  | 云同步（需 ENABLE_CLOUD_SYNC） | 660×380  |

标签页切换时窗口尺寸会自动调整（`tab_change_event()`）。

### 8.2 书库渲染机制

书库采用**动态渲染（懒加载）**策略：

1. `render_book_bank()` 创建 `WidgetGrid`，设置若干列网格，计算总高度
2. 仅屏幕上需显示的书调用 `Initialize()` 完成完整渲染
3. 其余书作为占位控件加入网格
4. 用户滚动时，`init_bwlist(y_pos)` 根据当前滚动位置计算可见行，按需初始化相邻区域的 BookWidget
5. 未渲染的书被移到 `hidden_veil`（隐藏容器）以避免资源占用

### 8.3 信号/槽连接

主要信号连接（定义在 `MainWindow.set_connection()` 中）：

```python
# 下载控制
ui.DC.buttonClicked → DownloadContentControl()
ui.DM.buttonClicked → DownloadModeControl()
ui.TF.buttonClicked → TextFormulaControl()
ui.StartB.clicked   → downloadStart()

# 书库控制
ui.od_bank.lclicked → 排序菜单
ui.flt_genre.lclicked → 标签筛选菜单
ui.flt_bunko.lclicked → 文库筛选菜单
ui.flt_search.textChanged → sr_edit_update()  # 实时搜索
ui.flt_liked.lclicked/rclicked → 收藏筛选切换
ui.refresh_bank.lclicked → refresh_bw_list()
ui.order_arrow.clicked → 升降序切换
scr_bar.valueChanged → init_bwlist()  # 滚动懒加载

# RMZ 导入/导出
ui.export_btn.clicked → setExportMode()
ui.start_export.lclicked → handleExport()
ui.import_btn.clicked → handleImport()

# 其他
ui.Exit.clicked → sys.exit()  # 直接退出进程
ui.GLB_setting.clicked → uiConfig.show()  # 配置窗口
```

---

## 9. 配置系统

### 9.1 配置生命周期

```
首次启动 → 不存在 config.json
    ↓
get_global_settings() → 按 DEFAULT_SETTING 生成 config.json
    ↓
运行时修改 → Ui_Config 调用 modify_global_settings()
    ↓
保存/应用 → 写入 config.json 并更新全局 CONFIG 字典
```

### 9.2 配置项完整列表

| 配置项                               | 类型    | 默认值                      | 说明                   |
|-----------------------------------|-------|--------------------------|----------------------|
| `ENABLE_PANDOC`                   | bool  | `true`                   | 启用 pandoc 进行 EPUB 转换 |
| `ENABLE_ISF`                      | bool  | `false`                  | 启用图片搜索功能（开发中）        |
| `COMPLICATE_SLICE_NAME`           | bool  | `false`                  | 分卷 DOCX 名是否包含系列名     |
| `MAX_THREAD_WORKER`               | int   | `6`                      | 图文下载最大线程数（建议 ≤8）     |
| `ALWAYS_USE_DEFAULT_DOWNLOAD`     | bool  | `false`                  | 始终使用默认下载方式           |
| `ILLUSTRATION_REQUEST_SLEEP_TIME` | float | `0.1`                    | 插图请求间隔（秒）            |
| `TEXT_REQUEST_SLEEP_TIME`         | float | `0.2`                    | 文本请求间隔（秒）            |
| `MAX_VOLUME_THREAD_WORKER`        | int   | `2`                      | 分卷下载最大线程数            |
| `ENABLE_BANK`                     | bool  | `true`                   | 启用书库模块               |
| `AUTO_FILL_CONVERTER_INFO`        | bool  | `true`                   | 转换器自动填充元数据           |
| `ALLOW_WARNING_WINDOWS`           | bool  | `true`                   | 启用警告弹窗               |
| `BANK_PATH`                       | str   | `"novel"`                | 书籍下载默认路径             |
| `RMZ_EXPORT_PATH`                 | str   | `"rmz"`                  | RMZ 导出默认路径           |
| `RMZ_FILENAME_FORMAT`             | str   | `"%NUMNAME%_%TMSTAMP%"`  | RMZ 文件名模板            |
| `RMZ_FILENAME_SUFFIX`             | str   | `"(%NUM%)"`              | 文件名冲突时的后缀模板          |
| `DEFAULT_COVER`                   | str   | `"images/uncovered.jpg"` | pandoc 默认封面路径        |
| `LANGUAGE`                        | str   | `"en-US"`                | 界面语言（en-US / zh-CN）  |
| `SHOW_FORMATED_FILE`              | bool  | `true`                   | 自动勾选已存在的格式化文件        |
| `AUTO_UNLOCK_TEXTER`              | bool  | `false`                  | 自动解锁格式器选项限制          |
| `SIMPLE_BANK_FILE`                | bool  | `false`                  | bank.json 紧凑存储模式     |
| `PROXY_PORT`                      | int   | `-1`                     | GET 请求代理端口           |
| `ENABLE_CLOUD_SYNC`               | bool  | `false`                  | 启用云同步页面              |
| `FTP_HOST`                        | str   | `""`                     | FTP 服务器地址(隐藏)        |
| `FTP_PORT`                        | int   | `21`                     | FTP 服务器端口(隐藏)        |
| `FTP_USERNAME`                    | str   | `""`                     | FTP 登录用户名(隐藏)        |
| `FTP_PASSWORD`                    | str   | `""`                     | FTP 登录密码(隐藏)         |
| `BANK_RESOLUTION`                 | tuple | `(1068, 640)`            | 书库页的默认分辨率            |
| `SCROLL_POSTION_KEEPER`           | int   | `2`                      | 书库页存储滚动进度的模式         |
| `RESIZE_DELAY`                    | int   | `16`                     | 拖动书库页大小时的渲染延迟        |
| `RENDER_RANGE`                    | int   | `0`                      | 额外动态渲染的图书组件行数        |
---

## 10. 国际化 (i18n)

### 10.1 架构

所有用户可见文本集中在 `config.py` 的 `ALL_TEXT` 字典中：

```python
ALL_TEXT = {
    "KEY": {
        'en-US': "English text",
        'zh-CN': "中文文本"
    },
    ...
}
```

`translate_to(code)` 函数遍历 `ALL_TEXT`，提取指定语言（通过 `CONFIG['LANGUAGE']` 配置）的文本，生成 `LANG` 字典。

### 10.2 使用方式

```python
from config import LANG

# 获取翻译文本
label.setText(LANG['DL_StartB'])  # "Start Download" 或 "开始下载"
```

### 10.3 命名约定

翻译 Key 的命名前缀：

| 前缀          | 含义                | 示例                                 |
|-------------|-------------------|------------------------------------|
| `DL_`       | 下载器 (Downloader)  | `DL_StartB`, `DL_Numname`          |
| `TX_`       | 格式器 (Texter)      | `TX_DirectoryChoose`, `TX_HFolder` |
| `CV_`       | 转换器 (Converter)   | `CV_FileChoose_c`, `CV_Start_c`    |
| `BB_`       | 书库 (BookBank)     | `BB_TABNAME`, `BB_flt_bunko`       |
| `BW_`       | 书籍卡片 (BookWidget) | `BW_rating`, `BW_progress`         |
| `CFG_`      | 配置 (Config)       | `CFG_ENABLE_PANDOC`, `CFG_window`  |
| `CTASK_`    | 细节窗口              | `CTASK_window`, `CTASK_select_all` |
| `RT_`       | 评分 (Rating)       | `RT_window`                        |
| `PG_`       | 进度 (Progress)     | `PG_window`                        |
| `UPD_`      | 更新 (Update)       | `UPD_window`                       |
| `MIS_`      | 任务 (Missions)     | `MIS_Window`, `MIS_button`         |
| `TASK_`     | 任务类型              | `TASK_type_DOWNLOADER`             |
| `TODOLIST_` | 待办清单              | `TODOLIST_window`                  |

---

## 11. RMZ 文件格式

RMZ 是 LightND 自定义的数据交换格式，用于阅读进度和评分的持久化导出。

### 11.1 二进制结构

```
偏移    长度    内容
0       4       Magic: b'RHMZ'
4       4       Type:  b'BANK' | b'LUXU' | b'PRRT'
8       N       Payload: UTF-8 JSON
```

### 11.2 类型说明

| Type | 值         | 含义      | JSON 内容                    |
|------|-----------|---------|----------------------------|
| BANK | `b'BANK'` | 完整书库条目  | `BankedBook.toDict()`      |
| LUXU | `b'LUXU'` | 仅附加数据   | `BookLuxury.toDict()`      |
| PRRT | `b'PRRT'` | 进度 + 评分 | `{'prg': ..., 'rtg': ...}` |

### 11.3 文件名模板

`RMZ_FILENAME_FORMAT` 支持以下标签：

| 标签           | 替换为         | 示例值                   | 切片支持                  |
|--------------|-------------|-----------------------|-----------------------|
| `%NUMNAME%`  | 数字编码        | `2784`                | `%NUMNAME[2]%` → `27` |
| `%BKNAME%`   | 书名          | `弹珠汽水瓶里的千岁同学`         | `%BKNAME[-3]%`        |
| `%TMSTAMP%`  | Unix 时间戳（秒） | `1711234567`          | ✓                     |
| `%DATETIME%` | 日期时间字符串     | `2025_04_30_14_30_00` | ✓                     |

文件名冲突时使用 `RMZ_FILENAME_SUFFIX` 模板（`%NUM%` 替换为自增序号）。

---

## 12. 线程模型

### 12.1 线程池

应用使用两层线程池：

1. **QThreadPool**（UI 线程池）：
   - 通过 `MainWindow.start_task()` 提交 `WorkerRunnable`
   - 用于下载任务、格式化任务、转换任务等长时间操作
   - 避免阻塞 UI 线程

2. **ThreadPoolExecutor**（数据线程池）：
   - `netwk.py`：并发下载插图（`MAX_WAORKERS` 控制）
   - `bookbank.py`：并发读取 `.hmz` 文件启动加速
   - `downloadprocess.py`：并发下载卷内章节

### 12.2 线程安全

- 线程池任务通过 `WorkerRunnable` 执行 `callback()` 回到主线程
- `AbstractSignalBond` 提供了防重入的信号绑定（`__is_locked__` 标志）
- HMZ 文件缓存（`HMZFILES` 全局变量）在 `update_hmzfiles()` 时全量替换

---

## 13. 测试与调试

### 13.1 性能测试

`LightNV.py` 内置 `timetest()` 函数，用于测量启动耗时：

```python
def timetest(func, *args, **kwargs):
    app = QApplication(sys.argv)
    a = pfc()  # perf_counter
    func(*args, **kwargs)
    b = pfc()
    print(f'{b - a:2f} seconds used to activate.')
```

### 13.2 模块独立运行

部分模块支持直接运行进行测试：

```bash
python book_struct.py   # 测试数据模型
python downloadprocess.py  # 测试下载（会创建测试任务）
python netwk.py         # 测试网络请求
python image_search.py  # 测试插图搜索
```

---

## 14. 版本历史摘要

| 版本     | 日期         | 主要变更                               |
|--------|------------|------------------------------------|
| v8.5.3 | 2026-05-13 | 配置项动态生成、更新窗口图标、修复配置项名称显示问题         |
| v8.5.2 | 2026-05-12 | 书库分辨率可配置、新增配置项说明、部分功能隐藏/移出仓库       |
| v8.5.1 | 2026-05-05 | 书库高级搜索、搜索性能优化                      |
| v8.5   | 2026-05-03 | 书库管理模式、界面重排与清晰度提升、书库窗口自由缩放         |
| v8.4   | 2026-05-02 | FTP 云同步、Book 对象可哈希化                |
| v8.3.5 | 2026-05-01 | 外源 bank.json 加载接口                  |
| v8.3.4 | 2026-04-30 | 评分组件悬浮数字自动更新                       |
| v8.3.3 | 2026-04-28 | 书库刷新性能优化（增量更新，不再全量重载）              |
| v8.3.2 | 2026-04-20 | 修复书库刷新排序失效与动态渲染问题                  |
| v8.3   | 2026-04-14 | 多线程启动（启动加速最高 50%）、细节菜单 UI 翻新       |
| v8.2.1 | 2026-04-12 | 书库动态渲染（启动加速 60%+）、ENABLE_BANK 配置增强 |
| v8.2   | 2026-04-03 | 代理端口配置（PROXY_PORT）、配置项整型范围限制       |
| v8.1   | 2026-03-31 | RMZ 后缀模板、文本格式化切片功能                 |
| v8.0   | 2026-03-31 | 书籍结构化重整、SIMPLE_BANK_FILE 配置、入库时间排序 |
| v7.5   | 2026-03-12 | 多任务菜单、导入多任务功能                      |

完整更新日志见 [CHANGELOG.md](CHANGELOG.md)。
