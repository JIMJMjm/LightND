# LightND

> 轻小说下载、管理与格式转换桌面工具  
> Light Novel Downloader & Manager — 基于 PySide6 构建

**当前版本**: Release v8.3.4  
**运行平台**: Windows (x64)  
**语言支持**: English / 中文

---

## 功能

- **小说下载** — 输入数字编码即可下载整本轻小说（含插图），支持逐卷/整本模式、断点续传与批量任务
- **文本格式化** — 将下载的 txt 文件格式化为排版精良的 DOCX 文档，支持系列合集与分卷两种模式
- **电子书转换** — DOCX → EPUB → AZW3 全链路转换，支持 pandoc（快速）与 calibre（兼容）双引擎
- **书库管理** — 浏览、排序、筛选、搜索已下载书籍；支持按文库、标签、收藏状态筛选，按书名/编码/评分/入库时间排序
- **阅读进度追踪** — 按卷/章节粒度记录阅读进度，数据可导出备份
- **评分系统** — 10 级评分（半星粒度），按卷独立评价
- **数据迁移** — 通过 `.rmz` 文件导出/导入阅读进度与评分，支持跨设备迁移
- **更新检测** — 自动检测已入库书籍是否有新卷发布，支持一键更新

---

## 快速开始

### 环境要求

- Python 3.13+
- Windows 操作系统
- （可选）[pandoc](https://pandoc.org/) — 用于 EPUB 生成（推荐）
- （可选）[calibre](https://calibre-ebook.com/) — 用于 AZW3 生成

### 安装

```bash
# 1. 克隆仓库
git clone <repo-url>
cd LightND

# 2. 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
python LightNV.py
```

首次运行会自动在根目录生成 `config.json`（默认配置）和 `bank.json`（书库索引）。下载的书籍默认存储在 `novel/` 目录。

### 基本使用

1. **下载**：在「Downloader」标签页输入书籍的数字编码，选择下载选项，点击「Start Download」
2. **格式化**：切换到「Texter」标签页，选择已下载的书籍文件夹，勾选需要的格式，点击「Start Forming」
3. **转换**：在「Converter」标签页选择 DOCX 文件，自动填充元数据后点击「Convert」
4. **管理**：在「BookBank」标签页浏览、排序、筛选书库，点击书籍卡片的「Texter」跳转到格式器
5. **批量下载**：点击「To-do List」创建/编辑多任务清单，在输入框输入 `#Todo-List#` 后启动下载

---

## 配置

所有配置项可通过应用内「Config」按钮实时修改，或直接编辑根目录下的 `config.json`。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `ENABLE_BANK` | bool | `true` | 启用书库模块（禁用可加速启动） |
| `ENABLE_PANDOC` | bool | `true` | 使用 pandoc 转换 EPUB（更快） |
| `BANK_PATH` | str | `"novel"` | 书籍下载目录 |
| `RMZ_EXPORT_PATH` | str | `"rmz"` | RMZ 导出目录 |
| `RMZ_FILENAME_FORMAT` | str | `"%NUMNAME%_%TMSTAMP%"` | RMZ 文件名模板 |
| `PROXY_PORT` | int | `-1` | 代理端口（-1=不启用，0=部分启用，>0=全部） |
| `LANGUAGE` | str | `"en-US"` | 界面语言（`en-US` / `zh-CN`） |
| `MAX_THREAD_WORKER` | int | `6` | 下载线程数（建议不超过 8） |
| `SIMPLE_BANK_FILE` | bool | `false` | bank.json 紧凑存储（可节省 40-60% 空间） |
| `ALLOW_WARNING_WINDOWS` | bool | `true` | 启用警告弹窗 |

完整配置列表及说明见 [config.py](config.py) 中的 `DEFAULT_SETTING` 与 `CONFIG_NOTATION`。

---

## 项目结构

```
LightND/
├── LightNV.py              # 应用主入口 & 主窗口控制器
├── config.py               # 全局配置 & 国际化 (i18n)
├── book_struct.py          # 领域模型 (Book / BankedBook / HmzedBook)
├── bookbank.py             # 书库管理 (bank.json 读写、排序、筛选)
├── netwk.py                # 网络请求 & HTML 解析
├── downloadprocess.py      # 下载流程控制
├── txtprocess.py           # 文本格式化 & 电子书转换
├── BySide.py               # 自定义 Qt 控件库
├── prg_export.py           # RMZ 导出 (阅读数据序列化)
├── prg_import.py           # RMZ 导入 (含冲突对比界面)
├── image_search.py         # 插图搜索 (实验性)
├── line_fit.py             # 线性回归工具
├── novelsrh.py             # 小说搜索 (开发中)
├── ui/                     # UI 组件
│   ├── ui_LightNV.py       #   主窗口布局
│   ├── ui_bookwidget.py    #   书籍卡片组件
│   ├── ui_config.py        #   配置编辑窗口
│   ├── ui_ctask.py         #   细节窗口 (卷列表/评分/进度)
│   ├── ui_rating.py        #   星级评分控件
│   ├── ui_missions.py      #   任务进度窗口
│   ├── ui_tdl.py           #   多任务编辑窗口
│   └── ui_update.py        #   更新详情窗口
├── images/                 # 图标 & 资源文件
├── requirements.txt        # Python 依赖
└── samples.json            # 插图搜索样本数据
```

更多架构细节见 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)。

---

## 注意事项

- 自 **Release v8.0** 起，书籍信息存储结构变更，旧版本数据无法直接兼容。升级后请在项目根目录运行以下命令迁移数据：

  ```bash
  python bookbank.py
  ```

- 下载功能依赖外部网络服务。如遇下载失败，请检查网络连接、代理设置（`PROXY_PORT`）或等待后重试。
- 请遵守相关版权法规，仅下载您拥有合法访问权限的内容。

---

## 依赖

核心依赖：**PySide6** (Qt GUI框架) · **BeautifulSoup4** (HTML解析) · **requests** (HTTP客户端) · **python-docx** (DOCX生成) · **Pillow** (图像处理) · **pypinyin** (拼音排序)

外部工具：**pandoc** (EPUB转换) · **calibre** (AZW3转换)

完整依赖列表见 [requirements.txt](requirements.txt)。

---

## License

本项目仅供学习与研究使用。
