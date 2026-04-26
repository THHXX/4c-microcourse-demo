# 卷积核微课 - 虚拟实验室

> 面向初中生的计算机视觉（卷积核）微课学习平台。单文件 FastAPI 后端 + 多页面 HTML 前端 + 千问大模型 AI 助教，一体化提供"看视频 → 做练习 → 问 AI → 导出笔记"完整闭环。
>
> **参赛项目**：2026 年大学生计算机设计大赛 · 微课与人工智能辅助教学组

---

## 一、项目定位

- **学习对象**：初中生（需要通俗语言、暖色调友好 UI）
- **知识主题**：卷积核（Convolution Kernel）——定义、类型、计算、在 CNN 中的作用
- **核心载体**：一段短视频（`DougongGrowth.mp4`） + 一份交互式 HTML 课后资料 + AI 对话
- **评审材料**：`1-作品信息概要表.docx`、`2-AI工具使用说明.docx`（已填写版放在根目录）

## 二、技术栈

| 层 | 用到的东西 |
|---|---|
| 后端 | Python 3 / FastAPI / Uvicorn / Jinja2 / python-dotenv / requests |
| 前端 | 原生 HTML+CSS+JS（无框架），FontAwesome 6、Google Fonts（Fredoka / Nunito / JetBrains Mono），anime.js、fabric.js、html2pdf.js、FileSaver.js（全部 CDN） |
| AI | 阿里云百炼 DashScope：`qwen-plus`（文本）+ `qwen-vl-plus`（视觉，用于截图分析） |
| 导出 | 自拼 HTML 伪 Word（`.doc`）+ 浏览器打印 PDF |
| 持久化 | 纯 `localStorage`（无数据库），服务端只存截图和导出文件到 `static/` |

**依赖清单**（`requirements.txt`）：`fastapi`, `uvicorn`, `requests`, `python-dotenv`, `streamlit`, `python-docx`, `reportlab`, `Pillow`
（注：streamlit / python-docx / reportlab / Pillow 历史遗留，当前主流程未使用。）

## 三、运行方式

```bash
pip install -r requirements.txt
# .env 已配置好 DASHSCOPE_API_KEY（不要提交到 git）
python main.py
```

- **端口固定 9000**，被占用时直接杀进程，不换端口（见 CLAUDE.md 规则）
  ```bash
  netstat -ano | findstr :9000
  taskkill /PID <PID> /F
  ```
- 启动后访问：
  - 首页 / 微课观影 → http://localhost:9000/
  - 课后学习 → http://localhost:9000/study
  - AI 助教 → http://localhost:9000/ai-tutor
  - 健康检查 → http://localhost:9000/health

## 四、目录结构

```
框架/
├── main.py                              # 后端总入口（约 2880 行，单文件把三页 HTML 全写里面了）
├── DougongGrowth.mp4                    # 核心微课视频
├── 课后学习资料_优化版.html             # 课后学习页（由 main.py 注入导出弹窗后返回）
├── requirements.txt
├── .env                                 # 千问 API Key（已本地配置，.gitignore 已忽略）
├── static/
│   ├── screenshots/                     # 用户视频截图（POST /api/screenshot 写入）
│   └── exports/                         # 导出的 Word / HTML（用于打印 PDF）
├── 小猫图/                              # 课后资料里用到的示例素材
├── screenshots/                         # 早期截图目录（历史遗留）
├── 1-作品信息概要表（已填写）.docx      # 参赛提交材料
├── 2-AI工具使用说明（已填写）.docx
├── 3-微课与人工智能辅助教学作品提交要求（2026年版）.docx
├── gen_doc1.js / gen_doc2.js            # 生成上述 docx 的一次性脚本
├── 项目复盘报告_20260409.md
└── CLAUDE.md                            # 给 Claude 看的项目规则（运行/代码/回复规范）
```

## 五、三个页面的职责

### 1. `/` 首页 / 微课观影（main.py 内嵌 HTML）
- HTML5 `<video>` 播放 `DougongGrowth.mp4`（后端 `/video/stream` 支持 Range 断点续传）
- 侧边栏集成：
  - **截图笔记**：canvas 抓取当前帧 → POST `/api/screenshot` 存盘 → 可 POST `/api/analyze-screenshot` 交给 `qwen-vl-plus` 做视觉分析
  - **AI 学习助手对话**（调 `/ai-tutor/chat`）
- 数据存 `localStorage`：`convolutionKernelNotes`（截图笔记）、`vlab_home_chat`（对话）

### 2. `/study` 课后学习（外部 HTML + 后端注入）
- 读取 `课后学习资料_优化版.html`，在 `</body>` 前注入：
  - 劫持 `addChatMessage`，把对话同步到 `localStorage['vlab_study_chat']`
  - 共享导出弹窗 + 悬浮导出按钮
- 页面本身自带：**笔记**（`convolution_notes`）、**错题本**（`convolution_wrong_questions`）、**AI 对话**（走 `/api/ask`，旧版兼容接口）

### 3. `/ai-tutor` AI 助教（main.py 内嵌 HTML）
- 专职 AI 对话界面，对话存 `localStorage['vlab_tutor_chat']`
- 调用 `/ai-tutor/chat`（系统提示词强制排版清晰、语言通俗、重点加粗）

## 六、后端路由全景

| Method | Path | 作用 |
|---|---|---|
| GET | `/` | 首页 HTML |
| GET | `/study` | 课后学习 HTML（注入后返回） |
| GET | `/ai-tutor` | AI 助教 HTML |
| GET | `/video/stream` | 视频流，支持 Range |
| GET | `/health` | 健康检查（含 video/html/api-key 状态） |
| POST | `/ai-tutor/chat` | 新版 AI 对话（返回 `{response}`） |
| POST | `/api/ask` | 旧版兼容对话（返回 `{content}`，给 `课后学习资料_优化版.html` 用） |
| POST | `/api/screenshot` | base64 图片写盘 |
| POST | `/api/analyze-screenshot` | 调 `qwen-vl-plus` 视觉分析 |
| POST | `/api/export-word` | 单模块 Word 导出（截图笔记） |
| POST | `/api/export-pdf` | 单模块 PDF（走打印另存） |
| POST | `/api/export-wrong-word` / `-pdf` | 错题本导出 |
| POST | `/api/export-notes-word` / `-pdf` | 学习笔记导出 |
| POST | `/api/export-combined` | **跨页面组合导出**，最常用 |

## 七、跨页面统一导出（重要特性）

`get_shared_export_modal()` 和 `get_shared_export_btn(page_id)` 生成同一套 HTML/CSS/JS 注入到三个页面，任意页面点「选择导出」都能弹出同一个面板，勾选任意模块组合导出。

6 个可导出模块（id → localStorage key）：

| 模块 | key | 类型 |
|---|---|---|
| 首页截图笔记 | `convolutionKernelNotes` | JSON 数组 |
| 首页 AI 对话 | `vlab_home_chat` | JSON 数组 |
| 课后学习笔记 | `convolution_notes` | HTML 字符串 |
| 课后错题本 | `convolution_wrong_questions` | JSON 数组 |
| 课后 AI 对话 | `vlab_study_chat` | JSON 数组 |
| AI 助教对话 | `vlab_tutor_chat` | JSON 数组 |

格式二选一：**Word（`.doc`，MHTML 方式，Word 能原生打开）** 或 **PDF（生成 HTML → 浏览器打印另存）**。

## 八、项目铁律（CLAUDE.md 摘要 —— 改代码前务必遵守）

**运行规范**
- 端口固定 9000，被占用就杀进程，绝不换端口

**代码规范**
- 优先 `Edit` 不要 `Write` 整个文件
- 不重复读同一轮对话里已读过的文件
- 不加未要求的功能 / 注释 / 错误处理 / 类型注解
- 单文件 ≤ 400 行、嵌套 ≤ 4 层（⚠️ `main.py` 已 2880 行，是历史遗留，新增功能别再往里堆）

**回复规范**
- 简洁，不在末尾总结刚做的事

## 九、常见改动指南（给未来的自己 / AI）

- **改视频播放 / 截图相关** → 看 `main.py` 270–1370 行首页 HTML
- **改课后学习页** → 改 `课后学习资料_优化版.html`（main.py 只做注入，尽量别碰注入逻辑）
- **改 AI 助教页** → 看 `main.py` 1440–2209 行
- **改 AI 系统提示词** → `/ai-tutor/chat` 的 `system_prompt`（约 2227 行）、`/api/ask` 的默认提示词（约 2295 行）
- **改导出** → `get_shared_export_modal()`（34 行起）+ `/api/export-combined`（约 2729 行）
- **换模型** → `.env` 里 `QWEN_MODEL`（文本），视觉模型 `qwen-vl-plus` 写死在约 2449 行

## 十、已知历史遗留

- `main-old.py`（已删，保留在 git 历史）、`main-old.py` 的老 API 契约（`/api/ask` 返回 `{content}`）仍在为 `课后学习资料_优化版.html` 服务，改这个接口前先确认前端兼容
- `requirements.txt` 里 streamlit / python-docx / reportlab / Pillow 当前流程未使用，清理需谨慎
- 根目录有多个历史截图、导出文件（git status 可见 `D` 状态），已从工作目录删除
