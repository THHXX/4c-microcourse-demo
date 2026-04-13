"""
卷积核微课 - 虚拟实验室
基于FastAPI的计算机视觉微课学习平台
"""

import os
import json
import time
import base64
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# ============ 配置 ============
BASE_DIR = Path(__file__).parent
VIDEO_FILE = BASE_DIR / "DougongGrowth.mp4"
HTML_FILE = BASE_DIR / "课后学习资料_优化版.html"

# 千问API配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

# ============ FastAPI应用 ============
app = FastAPI(
    title="卷积核微课 - 虚拟实验室",
    description="计算机视觉微课学习平台",
    version="1.0.0"
)

# 静态文件及生成文件目录配置
static_dir = BASE_DIR / "static"
screenshots_dir = static_dir / "screenshots"
exports_dir = static_dir / "exports"

static_dir.mkdir(exist_ok=True)
screenshots_dir.mkdir(exist_ok=True)
exports_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Jinja2模板
templates = Jinja2Templates(directory=str(BASE_DIR))


# ============ 首页/微课观影 ============
@app.get("/", response_class=HTMLResponse)
async def index():
    """微课观影页面"""
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>卷积核微课 - 虚拟实验室</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600;700&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #FFF4E6;
                --c-coral: #C2410C;
                --c-mint: #B45309;
                --c-violet: #9A3412;
                --c-yellow: #D97706;
                --c-orange: #EA580C;
                --text-main: #1F2937;
                --text-muted: #6B7280;
                --surface: rgba(31,41,55,0.06);
                --surface-2: rgba(31,41,55,0.10);
                --border: rgba(31,41,55,0.14);
                --border-2: rgba(31,41,55,0.20);
                --shadow: 0 20px 40px rgba(17,24,39,0.14);
                --shadow-2: 0 10px 30px rgba(17,24,39,0.10);
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: 'Nunito', 'PingFang SC', -apple-system, sans-serif;
                background-color: var(--bg);
                min-height: 100vh;
                color: var(--text-main);
            }}
            .container {{ max-width: min(1200px, 100%); margin: 0 auto; padding: 20px; transition: padding 0.3s ease; }}
            .header {{
                text-align: center;
                padding: 40px 0;
            }}
            .header h1 {{
                font-family: 'Fredoka', 'PingFang SC', sans-serif;
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, var(--c-coral), var(--c-yellow));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .header p {{
                color: var(--text-muted);
                font-size: 1.1rem;
            }}
            .nav-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                margin-top: 40px;
            }}
            .nav-card {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 30px;
                text-decoration: none;
                color: var(--text-main);
                transition: all 0.3s ease;
            }}
            .nav-card:hover {{
                transform: translateY(-5px);
                background: var(--surface-2);
                border-color: rgba(217,119,6,0.35);
                box-shadow: var(--shadow);
            }}
            .nav-card i {{
                font-size: 2.5rem;
                margin-bottom: 20px;
            }}
            .nav-card h2 {{
                font-family: 'Fredoka', 'PingFang SC', sans-serif;
                font-size: 1.5rem;
                margin-bottom: 10px;
            }}
            .nav-card p {{
                color: var(--text-muted);
                line-height: 1.6;
            }}
            .card-video i {{ color: var(--c-yellow); }}
            .card-study i {{ color: var(--c-coral); }}
            .card-ai i {{ color: var(--c-mint); }}
            .video-player {{
                margin-top: 40px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 20px;
            }}
            .video-player h2 {{
                font-family: 'Fredoka', 'PingFang SC', sans-serif;
                color: var(--c-mint);
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .video-wrapper {{
                background: #1F2937;
                border-radius: 12px;
                overflow: hidden;
                aspect-ratio: 16/9;
            }}
            .video-wrapper video {{
                width: 100%;
                height: 100%;
                object-fit: contain;
            }}
            .no-video {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 400px;
                color: var(--text-muted);
                font-size: 1.1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-brain"></i> 卷积核微课</h1>
                <p>计算机视觉核心知识学习平台</p>
            </div>

            <div class="nav-cards">
                <a href="/" class="nav-card card-video">
                    <i class="fas fa-play-circle"></i>
                    <h2>📺 微课观影</h2>
                    <p>观看卷积核核心知识的教学视频</p>
                </a>
                <a href="/study" class="nav-card card-study">
                    <i class="fas fa-book-open"></i>
                    <h2>📚 课后学习</h2>
                    <p>交互式HTML学习资料与练习</p>
                </a>
                <a href="/ai-tutor" class="nav-card card-ai">
                    <i class="fas fa-robot"></i>
                    <h2>🤖 AI助教</h2>
                    <p>基于千问大模型的智能问答助手</p>
                </a>
            </div>

            <div class="video-player">
                <h2><i class="fas fa-video"></i> 核心微课视频</h2>
                <div class="video-wrapper">
    """
    if VIDEO_FILE.exists():
        html += f'''
                    <video id="mainVideo" controls preload="metadata" crossorigin="anonymous">
                        <source src="/video/stream" type="video/mp4">
                        您的浏览器不支持视频播放
                    </video>
        '''
    else:
        html += '''
                    <div class="no-video">
                        <p><i class="fas fa-exclamation-triangle"></i> 视频文件不存在</p>
                    </div>
        '''

    html += """
                </div>
    """
    
    # ======== 以下是完全无缝挂载的 [截图笔记] 前端 HTML/CSS/JS ========
    # 使用纯文本拼接以避免破坏原有 f-string 逻辑
    html += """
                <div class="video-actions" style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: var(--text-muted); font-size: 0.95rem;"><i class="fas fa-lightbulb"></i> 提示：遇到重点知识，可以随时截取画面并记录笔记</p>
                    <button class="btn-screenshot" onclick="takeScreenshot()"><i class="fas fa-camera"></i> 截屏记笔记</button>
                </div>
            </div>
        </div>

        <!-- 右侧侧边栏按钮组 -->
        <div class="right-sidebar-buttons" id="rightSidebarButtons">
            <button class="sidebar-toggle-btn active" onclick="switchPanel('notes', event)" title="我的笔记">
                <i class="fas fa-book"></i>
                <span>笔记</span>
            </button>
            <button class="sidebar-toggle-btn" onclick="switchPanel('ai', event)" title="AI助手">
                <i class="fas fa-robot"></i>
                <span>AI</span>
            </button>
            <button class="sidebar-toggle-btn" onclick="toggleRightSidebar()" title="收起侧边栏">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>

        <!-- 右侧侧边栏面板 -->
        <div class="right-sidebar" id="rightSidebar">
            <!-- 拖拽调整手柄 -->
            <div id="sidebarResizeHandle" class="sidebar-resize-handle"></div>
            <!-- 笔记面板 -->
            <div class="sidebar-panel active" id="notesPanel">
                <div class="panel-header">
                    <h3><i class="fas fa-clipboard-list"></i> 视频笔记</h3>
                    <button class="panel-close" onclick="toggleRightSidebar()"><i class="fas fa-times"></i></button>
                </div>
                <div class="panel-content" id="screenshotList">
                    <div class="empty-panel">
                        <i class="fas fa-image" style="font-size: 3rem; color: #B45309; margin-bottom: 15px;"></i>
                        <p style="color: #6B7280;">暂无笔记，点击视频下方的<br>"截屏记笔记"捕获画面</p>
                    </div>
                </div>
                <div class="export-buttons">
                    <button class="btn-export doc-btn" onclick="exportWord()"><i class="fas fa-file-word"></i> 导出 Word</button>
                    <button class="btn-export pdf-btn" onclick="exportPDF()"><i class="fas fa-file-pdf"></i> 导出 PDF</button>
                </div>
            </div>

            <!-- AI助手面板 -->
            <div class="sidebar-panel" id="aiPanel">
                <div class="panel-header">
                    <h3><i class="fas fa-robot"></i> AI学习助手</h3>
                    <button class="panel-close" onclick="toggleRightSidebar()"><i class="fas fa-times"></i></button>
                </div>
                <div class="panel-content">
                    <div class="chat-messages" id="chatMessages">
                        <div class="message assistant">
                            <span class="avatar"><i class="fas fa-robot"></i></span>
                            <div class="message-content">
                                你好！我是你的AI学习助手，有任何关于卷积核的问题都可以问我哦！
                            </div>
                        </div>
                    </div>
                    <div class="chat-input-area">
                        <input type="text" id="chatInput" placeholder="输入你的问题..." onkeypress="handleChatKeyPress(event)">
                        <button class="send-btn" onclick="sendChatMessage()"><i class="fas fa-paper-plane"></i></button>
                    </div>
                </div>
                <div class="export-buttons">
                    <button class="btn-export doc-btn" onclick="exportAIChat('word')"><i class="fas fa-file-word"></i> 导出 Word</button>
                    <button class="btn-export pdf-btn" onclick="exportAIChat('pdf')"><i class="fas fa-file-pdf"></i> 导出 PDF</button>
                </div>
            </div>
        </div>

        <!-- 图片预览模态框 -->
        <div class="modal" id="imageModal" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <img id="modalImage" src="" alt="预览">
            </div>
        </div>
        <canvas id="screenshotCanvas" style="display: none;"></canvas>

        <style>
            /* 截图功能配套样式 */
            .btn-screenshot {
                background: linear-gradient(135deg, var(--c-mint), var(--c-coral));
                color: white; border: none; padding: 12px 24px; border-radius: 12px;
                font-family: 'Nunito', sans-serif;
                font-size: 1rem; font-weight: 700; cursor: pointer; transition: all 0.3s ease;
            }
            .btn-screenshot:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(180,83,9,0.30); }

            /* 右侧侧边栏按钮组 */
            .right-sidebar-buttons {
                position: fixed;
                right: 0;
                top: 50%;
                transform: translateY(-50%);
                z-index: 999;
                display: flex;
                flex-direction: column;
                gap: 4px;
                background: rgba(255,244,230,0.92);
                border-radius: 12px 0 0 12px;
                border: 1px solid var(--border-2);
                border-right: none;
                backdrop-filter: blur(10px);
                transition: right 0.3s ease;
                box-shadow: var(--shadow-2);
            }
            .right-sidebar-buttons.collapsed {
                right: var(--right-sidebar-width);
            }
            .sidebar-toggle-btn {
                width: 50px;
                height: 50px;
                border: none;
                background: transparent;
                color: var(--text-main);
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 4px;
                font-size: 0.75rem;
                transition: 0.2s;
            }
            .sidebar-toggle-btn:first-child {
                border-radius: 12px 0 0 0;
            }
            .sidebar-toggle-btn:last-child {
                border-radius: 0 0 0 12px;
            }
            .sidebar-toggle-btn:hover {
                background: rgba(217,119,6,0.12);
                color: var(--c-yellow);
            }
            .sidebar-toggle-btn.active {
                background: rgba(217,119,6,0.15);
                color: var(--c-yellow);
            }
            .sidebar-toggle-btn i {
                font-size: 1.1rem;
            }

            :root {
                --right-sidebar-width: 420px;
            }
            .right-sidebar {
                position: fixed; right: calc(-1 * var(--right-sidebar-width)); top: 0; width: var(--right-sidebar-width);
                min-width: 280px; max-width: 600px; height: 100vh;
                background: rgba(255,244,230,0.97); backdrop-filter: blur(15px);
                border-left: 1px solid var(--border-2); box-shadow: -10px 0 30px rgba(17,24,39,0.14);
                transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1000;
                display: flex; flex-direction: column; color: var(--text-main);
            }

            /* 拖拽调整手柄 */
            .sidebar-resize-handle {
                position: absolute;
                left: 0;
                top: 0;
                width: 4px;
                height: 100%;
                background: transparent;
                cursor: col-resize;
                transition: background 0.2s;
            }
            .sidebar-resize-handle:hover,
            .sidebar-resize-handle.dragging {
                background: rgba(180,83,9,0.4);
            }

            /* 侧边栏打开时body整体缩进 */
            body.right-sidebar-open {
                padding-right: var(--right-sidebar-width);
                transition: padding-right 0.3s ease;
            }
            .right-sidebar.open { right: 0; }
            .sidebar-panel {
                display: none;
                flex: 1;
                flex-direction: column;
                height: 100%;
            }
            .sidebar-panel.active {
                display: flex;
            }
            .panel-header {
                padding: 20px; border-bottom: 1px solid var(--border);
                display: flex; justify-content: space-between; align-items: center;
            }
            .panel-header h3 { font-family: 'Fredoka', sans-serif; color: var(--c-mint); font-size: 1.2rem; }
            .panel-close { background: none; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; transition: 0.2s; }
            .panel-close:hover { color: var(--c-coral); }

            .panel-content { flex: 1; overflow-y: auto; padding: 15px; }
            .screenshot-item {
                background: var(--surface); border: 1px solid var(--border);
                border-radius: 12px; margin-bottom: 20px; overflow: hidden;
            }
            .screenshot-img { width: 100%; aspect-ratio: 16/9; object-fit: cover; cursor: zoom-in; border-bottom: 1px solid var(--border); }
            .screenshot-actions { padding: 10px; display: flex; gap: 8px; }
            .screenshot-actions button {
                flex: 1; padding: 8px; border: none; border-radius: 6px; color: white;
                font-size: 0.85rem; cursor: pointer; transition: 0.2s; font-weight: 600;
                font-family: 'Nunito', sans-serif;
            }
            .btn-ai { background: linear-gradient(135deg, var(--c-mint), var(--c-violet)); }
            .btn-del { background: rgba(194,65,12,0.10); color: var(--c-coral); border: 1px solid rgba(194,65,12,0.25); }
            .btn-ai:hover { box-shadow: 0 4px 12px rgba(180,83,9,0.30); }
            .btn-del:hover { background: var(--c-coral); color: white; }

            .note-area { padding: 0 10px 10px 10px; }
            .note-input {
                width: 100%; min-height: 60px; background: var(--surface); border: 1px solid var(--border);
                border-radius: 8px; color: var(--text-main); padding: 10px; font-size: 0.9rem; resize: vertical; outline: none;
                font-family: 'Nunito', sans-serif;
            }
            .note-input:focus { border-color: var(--c-yellow); }

            .ai-result {
                margin: 0 10px 10px 10px; padding: 12px; background: rgba(180,83,9,0.06);
                border-left: 3px solid var(--c-mint); border-radius: 0 8px 8px 0; font-size: 0.85rem;
                line-height: 1.5; color: var(--text-main); max-height: 150px; overflow-y: auto;
            }

            .export-buttons { padding: 15px; border-top: 1px solid var(--border); display: flex; gap: 10px; }
            .btn-export { flex: 1; padding: 12px; border: none; border-radius: 8px; color: white; font-weight: 700; cursor: pointer; transition: 0.3s; font-family: 'Nunito', sans-serif; }
            .doc-btn { background: #2b579a; }
            .pdf-btn { background: #c9302c; }
            .btn-export:hover { filter: brightness(1.15); transform: translateY(-1px); }

            .modal {
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(17,24,39,0.75); z-index: 2000; justify-content: center; align-items: center;
                backdrop-filter: blur(5px);
            }
            .modal.open { display: flex; }
            .modal-content img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: var(--shadow); }

            /* AI聊天样式 */
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-bottom: 15px;
                padding: 15px;
            }
            .message {
                display: flex;
                gap: 10px;
                max-width: 90%;
            }
            .message.user {
                align-self: flex-end;
                flex-direction: row-reverse;
            }
            .message .avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                font-size: 0.8rem;
            }
            .message.user .avatar {
                background: rgba(217,119,6,0.25);
                color: var(--c-yellow);
            }
            .message.assistant .avatar {
                background: rgba(180,83,9,0.20);
                color: var(--c-mint);
            }
            .message-content {
                padding: 10px 14px;
                border-radius: 12px;
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .message.user .message-content {
                background: rgba(217,119,6,0.15);
                color: var(--text-main);
                border-bottom-right-radius: 4px;
                border: 1px solid rgba(217,119,6,0.30);
            }
            .message.assistant .message-content {
                background: rgba(180,83,9,0.08);
                color: var(--text-main);
                border-bottom-left-radius: 4px;
                border: 1px solid rgba(180,83,9,0.18);
            }
            .chat-input-area {
                display: flex;
                gap: 8px;
                padding: 15px;
                border-top: 1px solid var(--border);
            }
            .chat-input-area input {
                flex: 1;
                padding: 10px 14px;
                border: 1px solid var(--border-2);
                border-radius: 8px;
                background: var(--surface);
                color: var(--text-main);
                font-size: 0.9rem;
                outline: none;
                font-family: 'Nunito', sans-serif;
            }
            .chat-input-area input:focus {
                border-color: var(--c-yellow);
            }
            .send-btn {
                padding: 0 16px;
                background: linear-gradient(135deg, var(--c-mint), var(--c-violet));
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: 0.2s;
                font-family: 'Nunito', sans-serif;
            }
            .send-btn:hover {
                filter: brightness(1.1);
                transform: translateY(-1px);
            }
            .send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .loading-dots {
                display: inline-flex;
                gap: 4px;
            }
            .loading-dots .dot {
                width: 6px;
                height: 6px;
                background: var(--c-mint);
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out;
            }
            .loading-dots .dot:nth-child(2) { animation-delay: 0.2s; }
            .loading-dots .dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
            .empty-panel { text-align: center; padding: 40px 20px; }
            .empty-panel p { color: var(--text-muted); }
        </style>

        <script>
            let notesData = [];
            let currentPanel = 'notes';

            // 页面加载时从localStorage读取笔记数据
            document.addEventListener('DOMContentLoaded', () => {
                const savedNotes = localStorage.getItem('convolutionKernelNotes');
                if (savedNotes) {
                    notesData = JSON.parse(savedNotes);
                    renderNotes();
                }
            });

            // 保存笔记数据到localStorage
            function saveNotesToLocalStorage() {
                localStorage.setItem('convolutionKernelNotes', JSON.stringify(notesData));
            }

            // 侧边栏拖拽调整功能
            let isResizing = false;
            const resizeHandle = document.getElementById('sidebarResizeHandle');
            const sidebar = document.getElementById('rightSidebar');

            resizeHandle.addEventListener('mousedown', (e) => {
                isResizing = true;
                resizeHandle.classList.add('dragging');
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
                // 移除过渡效果，让拖拽更流畅
                sidebar.style.transition = 'none';
                document.body.style.transition = 'none';
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;
                // 计算新宽度：屏幕宽度 - 鼠标X位置
                const newWidth = window.innerWidth - e.clientX;
                // 限制最小和最大宽度
                if (newWidth >= 280 && newWidth <= 600) {
                    document.documentElement.style.setProperty('--right-sidebar-width', newWidth + 'px');
                }
            });

            document.addEventListener('mouseup', () => {
                if (isResizing) {
                    isResizing = false;
                    resizeHandle.classList.remove('dragging');
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                    // 恢复过渡效果
                    sidebar.style.transition = 'right 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                    document.body.style.transition = 'padding-right 0.3s ease';
                }
            });

            // 切换侧边栏显示/隐藏
            function toggleRightSidebar() {
                const sidebar = document.getElementById('rightSidebar');
                const buttons = document.getElementById('rightSidebarButtons');
                sidebar.classList.toggle('open');
                buttons.classList.toggle('collapsed');
                document.body.classList.toggle('right-sidebar-open');
            }

            // 切换面板
            function switchPanel(panelName, event) {
                // 打开侧边栏
                const sidebar = document.getElementById('rightSidebar');
                const buttons = document.getElementById('rightSidebarButtons');
                sidebar.classList.add('open');
                buttons.classList.add('collapsed');
                document.body.classList.add('right-sidebar-open');

                // 更新按钮状态
                document.querySelectorAll('.sidebar-toggle-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                if (event) event.currentTarget.classList.add('active');

                // 切换面板显示
                document.querySelectorAll('.sidebar-panel').forEach(panel => {
                    panel.classList.remove('active');
                });
                document.getElementById(`${panelName}Panel`).classList.add('active');
                currentPanel = panelName;

                // 如果是AI面板，聚焦输入框
                if (panelName === 'ai') {
                    setTimeout(() => document.getElementById('chatInput').focus(), 100);
                }
            }

            // 兼容原来的togglePanel函数
            function togglePanel() {
                switchPanel('notes');
            }

            async function takeScreenshot() {
                const video = document.getElementById('mainVideo');
                if (!video) return alert('未找到视频播放器');
                
                const canvas = document.getElementById('screenshotCanvas');
                const ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth || 1280;
                canvas.height = video.videoHeight || 720;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const imageData = canvas.toDataURL('image/png');
                
                // 打开笔记面板
                switchPanel('notes');
                
                // 占位加载效果
                const list = document.getElementById('screenshotList');
                if (notesData.length === 0) list.innerHTML = '';
                
                const tempId = 'loading-' + Date.now();
                list.innerHTML += `<div class="screenshot-item" id="${tempId}" style="text-align:center; padding: 20px;"><i class="fas fa-spinner fa-spin" style="font-size:2rem; color:#B45309;"></i><p>正在保存截图...</p></div>`;
                list.scrollTop = list.scrollHeight;

                try {
                    const response = await fetch('/api/screenshot', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    });
                    const result = await response.json();
                    
                    document.getElementById(tempId).remove();
                    
                    if (result.success) {
                        notesData.push({
                            id: Date.now(),
                            image_url: result.url,
                            user_note: '',
                            ai_analysis: ''
                        });
                        renderNotes();
                    } else {
                        alert('截图保存失败: ' + result.error);
                    }
                } catch (e) {
                    document.getElementById(tempId)?.remove();
                    alert('网络异常: ' + e.message);
                }
            }

            function renderNotes() {
                const list = document.getElementById('screenshotList');
                if (notesData.length === 0) {
                    list.innerHTML = `<div class="empty-panel"><i class="fas fa-image" style="font-size: 3rem; color: #B45309; margin-bottom: 15px;"></i><p style="color: #6B7280;">暂无笔记，点击视频下方的<br>"截屏记笔记"捕获画面</p></div>`;
                    return;
                }
                
                list.innerHTML = notesData.map((note, index) => `
                    <div class="screenshot-item">
                        <img src="${note.image_url}" class="screenshot-img" onclick="showModal('${note.image_url}')">
                        <div class="screenshot-actions">
                            <button class="btn-ai" onclick="analyzeImage(${index}, this)"><i class="fas fa-magic"></i> AI 帮我记</button>
                            <button class="btn-del" onclick="deleteNote(${index})"><i class="fas fa-trash"></i></button>
                        </div>
                        ${note.ai_analysis ? `<div class="ai-result"><b><i class="fas fa-robot"></i> AI解析：</b><br>${note.ai_analysis}</div>` : ''}
                        <div class="note-area">
                            <textarea class="note-input" placeholder="写下你的感悟..." onchange="updateNoteText(${index}, this.value)">${note.user_note}</textarea>
                        </div>
                    </div>
                `).join('');
                list.scrollTop = list.scrollHeight;
                // 保存到localStorage
                saveNotesToLocalStorage();
            }

            async function analyzeImage(index, btnEl) {
                const note = notesData[index];
                const originalHtml = btnEl.innerHTML;
                btnEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 解析中...';
                btnEl.disabled = true;

                try {
                    const response = await fetch('/api/analyze-screenshot', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image_path: note.image_url })
                    });
                    const result = await response.json();
                    
                    if (result.content) {
                        notesData[index].ai_analysis = result.content;
                        renderNotes();
                    } else {
                        alert('AI解析失败: ' + (result.error || '未知错误'));
                        btnEl.innerHTML = originalHtml;
                        btnEl.disabled = false;
                    }
                } catch (e) {
                    alert('网络异常: ' + e.message);
                    btnEl.innerHTML = originalHtml;
                    btnEl.disabled = false;
                }
            }

            function updateNoteText(index, val) { notesData[index].user_note = val; }
            function deleteNote(index) { if (confirm('确定要删除这条笔记吗？')) { notesData.splice(index, 1); renderNotes(); } }
            
            function showModal(src) {
                document.getElementById('modalImage').src = src;
                document.getElementById('imageModal').classList.add('open');
            }
            function closeModal() { document.getElementById('imageModal').classList.remove('open'); }

            async function exportWord() {
                if(notesData.length === 0) return alert('没有内容可以导出哦~');
                try {
                    const res = await fetch('/api/export-word', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ notes: notesData })
                    });
                    const data = await res.json();
                    if(data.success) window.open(data.url, '_blank');
                    else alert('导出失败');
                } catch(e) { alert('导出错误'); }
            }

            async function exportPDF() {
                if(notesData.length === 0) return alert('没有内容可以导出哦~');
                try {
                    const res = await fetch('/api/export-pdf', {
                        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ notes: notesData })
                    });
                    const data = await res.json();
                    if(data.success) {
                        const win = window.open(data.url, '_blank');
                        // 提示用户使用浏览器的打印功能保存为 PDF
                        setTimeout(() => alert('提示：在弹出的页面中，请使用快捷键 Ctrl+P (或 Cmd+P)，并选择"另存为 PDF"即可！'), 500);
                    }
                    else alert('导出失败');
                } catch(e) { alert('导出错误'); }
            }

            // ========== AI聊天功能 ==========
            // 简单Markdown解析函数，适合初中生阅读的轻量格式
            function parseMarkdown(text) {
                // 转义HTML防止XSS
                text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');

                // **加粗**
                text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');

                // 标题 ## 或 ###
                text = text.replace(/^### (.*?)$/gm, '<h4 style="margin: 10px 0; color: #B45309;">$1</h4>');
                text = text.replace(/^## (.*?)$/gm, '<h3 style="margin: 12px 0; color: #D97706;">$1</h3>');

                // 有序列表 1. 2.
                text = text.replace(/^(\\d+)\\. (.*?)$/gm, '<div style="margin: 5px 0 5px 20px;"><strong>$1.</strong> $2</div>');

                // 无序列表 - 或 *
                text = text.replace(/^[-*] (.*?)$/gm, '<div style="margin: 5px 0 5px 20px;">• $1</div>');

                // 换行
                text = text.replace(/\\n/g, '<br>');

                // 代码块 ``
                text = text.replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>');

                return text;
            }

            function addChatMessage(content, role) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;

                const icon = role === 'user' ? 'user' : 'robot';
                // AI消息需要解析Markdown，用户消息不需要
                const formattedContent = role === 'assistant' ? parseMarkdown(content) : content;

                messageDiv.innerHTML = `
                    <span class="avatar"><i class="fas fa-${icon}"></i></span>
                    <div class="message-content">${formattedContent}</div>
                `;

                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return messageDiv;
            }

            async function sendChatMessage() {
                const input = document.getElementById('chatInput');
                const message = input.value.trim();
                if (!message) return;

                // 添加用户消息
                addChatMessage(message, 'user');
                input.value = '';

                // 显示加载状态
                const loadingMsg = addChatMessage('<div class="loading-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>', 'assistant');

                // 重试机制：最多3次重试，每次间隔1秒
                const retries = 3;
                for (let i = 0; i < retries; i++) {
                    try {
                        const response = await fetch('/ai-tutor/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message }),
                            signal: AbortSignal.timeout(15000) // 15秒超时
                        });

                        const data = await response.json();

                        // 移除加载消息
                        loadingMsg.remove();

                        if (data.error) {
                            if (i === retries - 1) {
                                addChatMessage('错误: ' + data.error, 'assistant');
                            } else {
                                // 继续重试
                                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                                continue;
                            }
                        } else {
                            addChatMessage(data.response, 'assistant');
                            break;
                        }
                    } catch (err) {
                        if (i === retries - 1) {
                            loadingMsg.remove();
                            if (err.name === 'TimeoutError') {
                                addChatMessage(`⏱️ 请求超时，请稍后重试。已尝试 ${retries} 次连接。`, 'assistant');
                            } else {
                                addChatMessage('请求失败: ' + err.message, 'assistant');
                            }
                        } else {
                            // 等待后重试
                            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                        }
                    }
                }
            }

            // 保存AI聊天历史，用于导出
            let aiChatHistory = [
                { role: 'assistant', content: '你好！我是你的AI学习助手，有任何关于卷积核的问题都可以问我哦！' }
            ];

            // 重写addChatMessage函数，保存历史
            const originalAddChatMessage = addChatMessage;
            addChatMessage = function(content, role) {
                // 保存到历史，跳过加载和错误消息
                if (!content.includes('loading-dots') && !content.includes('❌ 错误') && !content.includes('请求失败')) {
                    aiChatHistory.push({ role, content });
                }
                return originalAddChatMessage(content, role);
            };

            // 导出AI聊天记录
            async function exportAIChat(type) {
                if (aiChatHistory.length === 0) {
                    alert('没有聊天记录可以导出哦~');
                    return;
                }

                // 组装聊天内容
                let content = '';
                aiChatHistory.forEach(msg => {
                    const roleName = msg.role === 'user' ? '你' : 'AI助手';
                    const formattedContent = msg.role === 'assistant' ? parseMarkdown(msg.content) : msg.content;
                    content += `<h3>${roleName}:</h3><div>${formattedContent}</div><br/>`;
                });

                if (type === 'word') {
                    // 导出Word - 调用现有的导出接口
                    try {
                        const res = await fetch('/api/export-notes-word', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                content: `<h1 style="text-align:center; color: #a855f7;">AI学习助手对话记录</h1><hr/>${content}`
                            })
                        });
                        const data = await res.json();
                        if(data.success) window.open(data.url, '_blank');
                        else alert('导出失败');
                    } catch(e) { alert('导出错误: ' + e.message); }
                } else if (type === 'pdf') {
                    // 导出PDF - 调用现有的导出接口
                    try {
                        const res = await fetch('/api/export-notes-pdf', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                content: `<h1 style="text-align:center; color: #a855f7;">AI学习助手对话记录</h1><hr/>${content}`
                            })
                        });
                        const data = await res.json();
                        if(data.success) {
                            const win = window.open(data.url, '_blank');
                            // 提示用户使用浏览器的打印功能保存为 PDF
                            setTimeout(() => alert('提示：在弹出的页面中，请使用快捷键 Ctrl+P (或 Cmd+P)，并选择"另存为 PDF"即可！'), 500);
                        }
                        else alert('导出失败');
                    } catch(e) { alert('导出错误: ' + e.message); }
                }
            }

            function handleChatKeyPress(event) {
                if (event.key === 'Enter') {
                    sendChatMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return html


# ============ 课后学习 ============
@app.get("/study", response_class=HTMLResponse)
async def study():
    """课后学习页面"""
    if not HTML_FILE.exists():
        raise HTTPException(status_code=404, detail="学习资料文件不存在")

    # 读取HTML文件内容
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return html_content


# ============ AI助教 ============
@app.get("/ai-tutor", response_class=HTMLResponse)
async def ai_tutor():
    """AI助教页面"""
    has_api_key = bool(DASHSCOPE_API_KEY)

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI助教 - 卷积核微课</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600;700&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
        <style>
            :root {{
                --bg: #FFF4E6;
                --c-coral: #C2410C;
                --c-mint: #B45309;
                --c-violet: #9A3412;
                --c-yellow: #D97706;
                --text-main: #1F2937;
                --text-muted: #6B7280;
                --surface: rgba(31,41,55,0.06);
                --surface-2: rgba(31,41,55,0.10);
                --border: rgba(31,41,55,0.14);
                --border-2: rgba(31,41,55,0.20);
                --shadow: 0 20px 40px rgba(17,24,39,0.14);
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{
                font-family: 'Nunito', 'PingFang SC', -apple-system, sans-serif;
                background-color: var(--bg);
                height: 100vh;
                overflow: hidden;
                color: var(--text-main);
            }}
            .container {{
                height: 100vh;
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 20px 20px 20px;
                display: flex;
                flex-direction: column;
            }}
            .header-bar {{
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 12px 0;
                border-bottom: 1px solid var(--border);
                flex-shrink: 0;
                position: relative;
            }}
            .header-bar h1 {{
                font-family: 'Fredoka', 'PingFang SC', sans-serif;
                font-size: 1.3rem;
                font-weight: 600;
                color: var(--c-mint);
            }}
            .header h1 {{
                font-family: 'Fredoka', 'PingFang SC', sans-serif;
                font-size: 2rem;
                margin-bottom: 10px;
                color: var(--text-main);
            }}
            .header h1 i {{ color: var(--c-mint); margin-right: 10px; }}
            .back-link {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: var(--text-muted);
                text-decoration: none;
                margin-bottom: 20px;
                transition: 0.2s;
            }}
            .back-link:hover {{ color: var(--c-yellow); }}
            .chat-messages {{
                flex: 1;
                overflow-y: auto;
                padding: 20px 0;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            .message {{
                max-width: 92%;
                padding: 12px 16px;
                border-radius: 12px;
                line-height: 1.6;
                font-size: 0.95rem;
            }}
            .message.user {{
                align-self: flex-end;
                background: rgba(217,119,6,0.15);
                border-bottom-right-radius: 4px;
                border: 1px solid rgba(217,119,6,0.30);
                color: var(--text-main);
            }}
            .message.assistant {{
                align-self: flex-start;
                background: rgba(180,83,9,0.08);
                border-bottom-left-radius: 4px;
                border: 1px solid rgba(180,83,9,0.18);
                color: var(--text-main);
            }}
            .message .avatar {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                vertical-align: middle;
            }}
            .message.user .avatar {{
                background: rgba(217,119,6,0.20);
                color: var(--c-yellow);
            }}
            .message.assistant .avatar {{
                background: rgba(180,83,9,0.18);
                color: var(--c-mint);
            }}
            .chat-input-area {{
                padding: 16px 0 0 0;
                border-top: 1px solid var(--border);
                display: flex;
                gap: 12px;
            }}
            .chat-input {{
                flex: 1;
                padding: 14px 20px;
                border: 1px solid var(--border-2);
                border-radius: 12px;
                background: var(--surface);
                color: var(--text-main);
                font-size: 1rem;
                outline: none;
                transition: 0.2s;
                font-family: 'Nunito', sans-serif;
            }}
            .chat-input::placeholder {{ color: var(--text-muted); }}
            .chat-input:focus {{ border-color: var(--c-yellow); }}
            .send-btn {{
                padding: 14px 28px;
                background: linear-gradient(135deg, var(--c-mint), var(--c-violet));
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1rem;
                font-weight: 700;
                cursor: pointer;
                transition: 0.2s;
                font-family: 'Nunito', sans-serif;
            }}
            .send-btn:hover {{ transform: scale(1.03); filter: brightness(1.1); }}
            .send-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
            .no-api-key {{
                text-align: center;
                padding: 60px 20px;
            }}
            .no-api-key i {{
                font-size: 4rem;
                color: var(--c-yellow);
                margin-bottom: 20px;
            }}
            .no-api-key h2 {{ margin-bottom: 10px; font-family: 'Fredoka', sans-serif; color: var(--c-mint); }}
            .no-api-key p {{ color: var(--text-muted); }}
            .loading {{
                display: flex;
                align-items: center;
                gap: 10px;
                color: var(--text-muted);
            }}
            .loading i {{
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            .welcome-message {{
                text-align: center;
                padding: 40px;
                color: var(--text-muted);
            }}
            .welcome-message i {{
                font-size: 3rem;
                color: var(--c-mint);
                margin-bottom: 20px;
            }}

            /* 自定义滚动条样式 - 适配暖色主题 */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: rgba(31,41,55,0.04);
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb {{
                background: rgba(180,83,9,0.28);
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: rgba(180,83,9,0.45);
            }}

            /* 操作按钮区域 */
            .chat-actions {{
                display: flex;
                gap: 8px;
                padding: 0 20px 10px;
                justify-content: flex-end;
            }}
            .action-btn {{
                padding: 6px 12px;
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 6px;
                color: var(--text-muted);
                font-size: 0.85rem;
                cursor: pointer;
                transition: 0.2s;
                font-family: 'Nunito', sans-serif;
            }}
            .action-btn:hover {{
                background: rgba(180,83,9,0.10);
                color: var(--c-mint);
                border-color: rgba(180,83,9,0.30);
            }}

            /* 响应式适配 */
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                .header h1 {{
                    font-size: 1.5rem;
                }}
                .chat-messages {{
                    padding: 15px;
                }}
                .message {{
                    max-width: 95%;
                    padding: 10px 14px;
                    font-size: 0.9rem;
                }}
                .chat-input-area {{
                    padding: 15px 10px;
                }}
                .send-btn {{
                    padding: 12px 20px;
                }}
                .chat-actions {{
                    padding: 0 10px 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
    """

    if not has_api_key:
        html += """
            <div class="no-api-key">
                <i class="fas fa-key"></i>
                <h2>API密钥未配置</h2>
                <p>请在 .env 文件中配置 DASHSCOPE_API_KEY</p>
            </div>
        </div>
    </body>
    </html>
        """
    else:
        html += f"""
            <div class="header-bar">
                <a href="/" class="back-link" style="position: absolute; left: 0; color: #6B7280; text-decoration: none; transition: 0.2s;"><i class="fas fa-arrow-left"></i> 返回首页</a>
                <h1>AI助手</h1>
            </div>
            <div class="chat-messages" id="messages">
            </div>
            <div class="chat-actions" style="padding: 10px 0; justify-content: flex-end; gap: 8px;">
                <button class="action-btn" onclick="exportChat('word')"><i class="fas fa-file-word"></i> 导出Word</button>
                <button class="action-btn" onclick="exportChat('pdf')"><i class="fas fa-file-pdf"></i> 导出PDF</button>
                <button class="action-btn" onclick="clearChat()"><i class="fas fa-trash"></i> 清空对话</button>
                <button class="action-btn" onclick="copyLastAnswer()"><i class="fas fa-copy"></i> 复制最后回复</button>
            </div>
            <div class="chat-input-area" style="padding: 0 0 16px 0;">
                    <input type="text" class="chat-input" id="userInput"
                           placeholder="输入你关于卷积核/计算机视觉的问题..." autofocus>
                    <button class="send-btn" onclick="sendMessage()">
                        <i class="fas fa-paper-plane"></i> 发送
                    </button>
                </div>
            </div>
        </div>

        <script>
            const messagesDiv = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendBtn = document.querySelector('.send-btn');

            userInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});

            async function sendMessage() {{
                const message = userInput.value.trim();
                if (!message) return;

                // 禁用发送按钮，防止重复提交
                sendBtn.disabled = true;
                userInput.disabled = true;

                // 添加用户消息
                addMessage(message, 'user');
                userInput.value = '';

                // 显示加载状态（跳过Markdown解析，直接显示HTML）
                const loadingMsg = addMessage('<div class="loading"><i class="fas fa-spinner"></i> AI思考中...</div>', 'assistant', true);

                try {{
                    const response = await fetch('/ai-tutor/chat', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message }})
                    }});

                    const data = await response.json();

                    // 移除加载消息
                    loadingMsg.remove();

                    if (data.error) {{
                        addMessage('❌ 错误: ' + data.error, 'assistant');
                    }} else {{
                        addMessage(data.response, 'assistant');
                    }}
                }} catch (err) {{
                    loadingMsg.remove();
                    addMessage('❌ 请求失败: ' + err.message, 'assistant');
                }} finally {{
                    // 恢复按钮状态
                    sendBtn.disabled = false;
                    userInput.disabled = false;
                    userInput.focus();
                }}
            }}

            // 增强版Markdown解析函数，支持公式、表格、引用等格式
            function parseMarkdown(text) {{
                // 转义HTML防止XSS
                text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');

                // 数学公式 $$...$$
                text = text.replace(/\\$\\$(.*?)\\$\\$/g, '<div style="text-align:center; margin: 15px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-family: monospace, "Times New Roman"; font-size: 1.1rem;">$1</div>');
                // 行内公式 $...$
                text = text.replace(/\\$(.*?)\\$/g, '<span style="font-family: monospace, "Times New Roman"; font-style: italic;">$1</span>');

                // **加粗**
                text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                // *斜体*
                text = text.replace(/\\*(.*?)\\*/g, '<em>$1</em>');

                // 标题层级
                text = text.replace(/^#### (.*?)$/gm, '<h5 style="margin: 8px 0; color: #a855f7; font-size: 1rem;">$1</h5>');
                text = text.replace(/^### (.*?)$/gm, '<h4 style="margin: 10px 0; color: #a855f7; font-size: 1.1rem;">$1</h4>');
                text = text.replace(/^## (.*?)$/gm, '<h3 style="margin: 12px 0; color: #a855f7; font-size: 1.2rem;">$1</h3>');
                text = text.replace(/^# (.*?)$/gm, '<h2 style="margin: 14px 0; color: #a855f7; font-size: 1.3rem;">$1</h2>');

                // 表格解析 | 表头1 | 表头2 |
                text = text.replace(/^\\|(.*?)\\|\\s*$/gm, (match, row) => {{
                    const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
                    if (cells.length === 0) return match;
                    return '<div style="display: grid; grid-template-columns: repeat(' + cells.length + ', 1fr); gap: 1px; background: rgba(255,255,255,0.2); margin: 10px 0; border-radius: 8px; overflow: hidden;">'
                        + cells.map(cell => '<div style="background: rgba(168, 85, 247, 0.2); padding: 8px; text-align: center; font-weight: bold;">' + cell + '</div>').join('')
                        + '</div>';
                }});
                // 表格内容行
                text = text.replace(/^\\|(?!.*:-)(.*?)\\|\\s*$/gm, (match, row) => {{
                    const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
                    if (cells.length === 0 || row.includes('---')) return '';
                    return '<div style="display: grid; grid-template-columns: repeat(' + cells.length + ', 1fr); gap: 1px; background: rgba(255,255,255,0.2); margin-top: -1px;">'
                        + cells.map(cell => '<div style="background: rgba(255,255,255,0.05); padding: 8px; text-align: center;">' + cell + '</div>').join('')
                        + '</div>';
                }});

                // 引用块 > 内容
                text = text.replace(/^> (.*?)$/gm, '<blockquote style="margin: 10px 0; padding: 10px 15px; border-left: 4px solid #a855f7; background: rgba(168, 85, 247, 0.1); border-radius: 0 8px 8px 0;">$1</blockquote>');

                // 有序列表 1. 2.
                text = text.replace(/^(\\d+)\\. (.*?)$/gm, '<div style="margin: 6px 0 6px 24px; line-height: 1.7;"><strong>$1.</strong> $2</div>');

                // 无序列表 - 或 *
                text = text.replace(/^[-*] (.*?)$/gm, '<div style="margin: 6px 0 6px 24px; line-height: 1.7;">• $1</div>');

                // 分割线 ---
                text = text.replace(/^---\\s*$/gm, '<hr style="border: none; height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;">');

                // 换行（先处理列表、表格等块元素再换行）
                text = text.replace(/\\n/g, '<br>');

                // 行内代码 `code`
                text = text.replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 6px; font-family: monospace; font-size: 0.9rem;">$1</code>');
                // 代码块 ```...```
                text = text.replace(/```([\\s\\S]*?)```/g, '<pre style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; overflow-x: auto; margin: 10px 0; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">$1</pre>');

                return text;
            }}

            // 存储聊天历史，方便复制和清空
            let chatHistory = [];

            function addMessage(html, role, skipParse = false) {{
                const div = document.createElement('div');
                div.className = 'message ' + role;
                // AI消息需要解析Markdown，用户消息和loading不需要
                const formattedContent = (role === 'assistant' && !skipParse) ? parseMarkdown(html) : html;

                // 保存到历史
                chatHistory.push({{ role, content: html, formatted: formattedContent }});

                div.innerHTML = '<span class="avatar"><i class="fas fa-' + (role === 'user' ? 'user' : 'robot') + '"></i></span>' + formattedContent;

                // 添加复制按钮，hover显示
                if (role === 'assistant') {{
                    const copyBtn = document.createElement('button');
                    copyBtn.className = 'copy-btn';
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    copyBtn.style.cssText = `
                        position: absolute;
                        top: 8px;
                        right: 8px;
                        background: rgba(255,255,255,0.1);
                        border: none;
                        color: #8892b0;
                        padding: 4px 6px;
                        border-radius: 4px;
                        cursor: pointer;
                        opacity: 0;
                        transition: opacity 0.2s;
                        font-size: 0.75rem;
                    `;
                    copyBtn.onclick = () => copyToClipboard(html);
                    div.style.position = 'relative';
                    div.appendChild(copyBtn);

                    // hover显示复制按钮
                    div.addEventListener('mouseenter', () => copyBtn.style.opacity = '1');
                    div.addEventListener('mouseleave', () => copyBtn.style.opacity = '0');
                }}

                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return div;
            }}

            // 复制文本到剪贴板
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text).then(() => {{
                    // 显示复制成功提示
                    const toast = document.createElement('div');
                    toast.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: #10b981;
                        color: white;
                        padding: 10px 16px;
                        border-radius: 8px;
                        z-index: 9999;
                        animation: slideIn 0.3s ease;
                    `;
                    toast.textContent = '✅ 已复制到剪贴板';
                    document.body.appendChild(toast);
                    setTimeout(() => toast.remove(), 2000);
                }}).catch(err => {{
                    alert('复制失败: ' + err);
                }});
            }}

            // 清空对话
            function clearChat() {{
                if (confirm('确定要清空所有聊天记录吗？')) {{
                    messagesDiv.innerHTML = ``;
                    chatHistory = [];
                }}
            }}

            // 复制最后一条AI回复
            function copyLastAnswer() {{
                const lastAiMsg = chatHistory.slice().reverse().find(msg => msg.role === 'assistant');
                if (lastAiMsg) {{
                    copyToClipboard(lastAiMsg.content);
                }} else {{
                    alert('没有可复制的AI回复');
                }}
            }}

            // 导出聊天记录
            function exportChat(type) {{
                if (chatHistory.length === 0) {{
                    alert('没有聊天记录可以导出');
                    return;
                }}

                if (type === 'pdf') {{
                    // 导出PDF - 直接使用当前页面的聊天内容
                    const opt = {{
                        margin: 15,
                        filename: 'AI对话记录.pdf',
                        image: {{ type: 'jpeg', quality: 0.98 }},
                        html2canvas: {{ scale: 2, useCORS: true }},
                        jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'portrait' }}
                    }};
                    // 创建一个临时容器，包含标题和所有聊天内容
                    const exportContainer = document.createElement('div');
                    exportContainer.style.padding = '40px';
                    exportContainer.style.fontFamily = '微软雅黑, sans-serif';
                    exportContainer.style.background = 'white';
                    exportContainer.style.color = '#333';
                    exportContainer.style.maxWidth = '800px';
                    exportContainer.style.margin = '0 auto';

                    // 添加标题
                    const header = document.createElement('div');
                    header.style.textAlign = 'center';
                    header.style.marginBottom = '30px';
                    header.style.paddingBottom = '20px';
                    header.style.borderBottom = '2px solid #a855f7';
                    header.innerHTML = '<h1 style=\"color: #a855f7; margin: 0; font-size: 24px;\">卷积核AI助手对话记录</h1>' +
                        '<p style=\"color: #666; margin-top: 15px; font-size: 14px;\">导出时间: ' + new Date().toLocaleString('zh-CN') + '</p>';
                    exportContainer.appendChild(header);

                    // 添加所有消息，过滤掉loading状态的消息并优化样式
                    const messagesClone = document.getElementById('messages').cloneNode(true);
                    // 移除所有包含loading的消息
                    const loadingMessages = messagesClone.querySelectorAll('.loading');
                    loadingMessages.forEach(loading => {{
                        const msgElement = loading.closest('.message');
                        if (msgElement) msgElement.remove();
                    }});

                    // 优化消息样式，适配打印
                    const messages = messagesClone.querySelectorAll('.message');
                    messages.forEach(msg => {{
                        msg.style.marginBottom = '20px';
                        msg.style.padding = '15px';
                        msg.style.borderRadius = '8px';
                        msg.style.maxWidth = '85%';
                        msg.style.pageBreakInside = 'avoid';
                        msg.style.wordWrap = 'break-word';

                        if (msg.classList.contains('user')) {{
                            msg.style.background = '#e8f0fe';
                            msg.style.marginLeft = 'auto';
                            const role = msg.querySelector('.role');
                            if (role) role.style.color = '#2563eb';
                        }} else {{
                            msg.style.background = '#f5f0ff';
                            msg.style.marginRight = 'auto';
                            const role = msg.querySelector('.role');
                            if (role) role.style.color = '#7c3aed';
                        }}

                        // 优化角色样式
                        const role = msg.querySelector('.role');
                        if (role) {{
                            role.style.fontWeight = 'bold';
                            role.style.marginBottom = '8px';
                            role.style.fontSize = '14px';
                        }}

                        // 优化内容样式
                        const content = msg.querySelector('.content');
                        if (content) {{
                            content.style.lineHeight = '1.8';
                            content.style.fontSize = '14px';

                            // 优化代码块样式
                            const codeBlocks = content.querySelectorAll('code');
                            codeBlocks.forEach(code => {{
                                code.style.background = 'rgba(0,0,0,0.05)';
                                code.style.padding = '2px 8px';
                                code.style.borderRadius = '4px';
                                code.style.fontFamily = 'monospace';
                                code.style.fontSize = '13px';
                            }});

                            // 优化表格样式
                            const tables = content.querySelectorAll('table');
                            tables.forEach(table => {{
                                table.style.width = '100%';
                                table.style.borderCollapse = 'collapse';
                                table.style.margin = '10px 0';
                                table.style.borderRadius = '8px';
                                table.style.overflow = 'hidden';

                                const cells = table.querySelectorAll('td, th');
                                cells.forEach(cell => {{
                                    cell.style.border = '1px solid rgba(0,0,0,0.1)';
                                    cell.style.padding = '8px';
                                    cell.style.textAlign = 'left';
                                }});

                                const headers = table.querySelectorAll('th');
                                headers.forEach(th => {{
                                    th.style.background = 'rgba(168, 85, 247, 0.1)';
                                    th.style.fontWeight = 'bold';
                                }});
                            }});
                        }}
                    }});

                    exportContainer.appendChild(messagesClone);

                    html2pdf().set(opt).from(exportContainer).save();

                }} else if (type === 'word') {{
                    // 导出Word - 生成原生HTML
                    let content = '<!DOCTYPE html>\\n' +
                    '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">\\n' +
                    '<head>\\n' +
                    '<meta charset="UTF-8">\\n' +
                    '<title>卷积核AI助手对话记录</title>\\n' +
                    '<!--[if gte mso 9]>\\n' +
                    '<xml>\\n' +
                    '    <w:WordDocument>\\n' +
                    '        <w:View>Print</w:View>\\n' +
                    '        <w:Zoom>90</w:Zoom>\\n' +
                    '        <w:DoNotOptimizeForBrowser/>\\n' +
                    '    </w:WordDocument>\\n' +
                    '</xml>\\n' +
                    '<![endif]-->\\n' +
                    '<style>\\n' +
                    '    body {{ font-family: "微软雅黑", sans-serif; line-height: 1.8; padding: 40px; font-size: 14px; color: #333; max-width: 800px; margin: 0 auto; }}\\n' +
                    '    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #a855f7; padding-bottom: 20px; }}\\n' +
                    '    .header h1 {{ color: #a855f7; margin: 0; font-size: 24px; }}\\n' +
                    '    .header p {{ color: #666; margin-top: 15px; font-size: 14px; }}\\n' +
                    '    .message {{ margin-bottom: 20px; padding: 15px; border-radius: 8px; max-width: 85%; page-break-inside: avoid; word-wrap: break-word; }}\\n' +
                    '    .message.user {{ background: #e8f0fe; margin-left: auto; }}\\n' +
                    '    .message.assistant {{ background: #f5f0ff; margin-right: auto; }}\\n' +
                    '    .role {{ font-weight: bold; margin-bottom: 8px; font-size: 14px; }}\\n' +
                    '    .user .role {{ color: #2563eb; }}\\n' +
                    '    .assistant .role {{ color: #7c3aed; }}\\n' +
                    '    .content {{ line-height: 1.8; font-size: 14px; }}\\n' +
                    '    code {{ background: rgba(0,0,0,0.05); padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; }}\\n' +
                    '    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; border-radius: 8px; overflow: hidden; }}\\n' +
                    '    table td, table th {{ border: 1px solid rgba(0,0,0,0.1); padding: 8px; text-align: left; }}\\n' +
                    '    table th {{ background: rgba(168, 85, 247, 0.1); font-weight: bold; }}\\n' +
                    '    img {{ max-width: 100%; border-radius: 8px; margin: 10px 0; }}\\n' +
                    '    hr {{ border: none; height: 1px; background: rgba(0,0,0,0.1); margin: 15px 0; }}\\n' +
                    '    h4 {{ margin: 10px 0; color: #a855f7; font-size: 1.1rem; }}\\n' +
                    '</style>\\n' +
                    '</head>\\n' +
                    '<body>\\n' +
                    '<div class="header">\\n' +
                    '    <h1>卷积核AI助手对话记录</h1>\\n' +
                    '    <p>导出时间: ' + new Date().toLocaleString('zh-CN') + '</p>\\n' +
                    '</div>\\n';

                    // 添加聊天内容，过滤掉loading状态的消息
                    chatHistory.forEach(msg => {{
                        const roleName = msg.role === 'user' ? '你' : 'AI助手';
                        const msgContent = msg.formatted || msg.content;
                        // 跳过包含loading的消息
                        if (msgContent.includes('AI思考中...') && msgContent.includes('fa-spinner')) {{
                            return;
                        }}
                        content += '<div class="message ' + msg.role + '">\\n' +
                            '    <div class="role">' + roleName + '</div>\\n' +
                            '    <div class="content">' + msgContent + '</div>\\n' +
                            '</div>\\n';
                    }});

                    content += '</body>\\n</html>';

                    // 导出Word，使用正确的编码
                    const blob = new Blob([content], {{ type: 'application/msword;charset=utf-8;' }});
                    saveAs(blob, 'AI对话记录_' + new Date().getTime() + '.doc');
                }}
            }}

            // 滑入动画
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {{
                    from {{ transform: translateX(100%); opacity: 0; }}
                    to {{ transform: translateX(0); opacity: 1; }}
                }}
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
        """

    return html


# ============ AI聊天API ============
@app.post("/ai-tutor/chat")
async def chat(request: Request):
    """AI聊天接口"""
    if not DASHSCOPE_API_KEY:
        return JSONResponse({"error": "API密钥未配置"}, status_code=400)

    try:
        body = await request.json()
        user_message = body.get("message", "")

        if not user_message:
            return JSONResponse({"error": "消息不能为空"}, status_code=400)

        # 系统提示词
        system_prompt = """你是一位专业的计算机视觉助教，专门面向初中生讲解卷积核（Convolution Kernel）的相关知识。

### 回答要求：
1. **排版清晰**：必须分段，用数字列表或项目符号展示要点，大段内容要拆分
2. **语言简单**：避免专业术语，用初中生能理解的通俗语言解释
3. **重点突出**：重要概念用**加粗**标记，关键步骤单独成行
4. **结构友好**：先讲结论，再讲细节，例子单独放在代码块或引用块里
5. **避免密集**：每部分内容不要超过3行，多空行分隔

你可以帮助学生理解以下内容：
- 卷积核的定义和原理
- 常见卷积核类型（边缘检测、模糊、锐化、Sobel等）
- 卷积操作的过程和计算
- 卷积神经网络中卷积层的作用
- 实际应用场景和例子

如果学生问的问题与卷积核或计算机视觉无关，请礼貌地引导他们回到主题上来。"""

        # 调用千问API
        url = f"{DASHSCOPE_BASE_URL}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": QWEN_MODEL,
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if "output" in result and "choices" in result["output"]:
            ai_response = result["output"]["choices"][0]["message"]["content"]
        elif "usage" in result:
            # 处理其他响应格式
            ai_response = str(result)
        else:
            return JSONResponse({"error": f"API响应异常: {result}"}, status_code=500)

        return {"response": ai_response}

    except requests.Timeout:
        return JSONResponse({"error": "请求超时，请稍后重试"}, status_code=504)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ============ 兼容旧版课后学习的API ============
@app.post("/api/ask")
async def ask_compatibility(request: Request):
    """专门为了兼容 课后学习资料.html 中写死的旧版请求"""
    if not DASHSCOPE_API_KEY:
        return JSONResponse({"error": "API密钥未配置"}, status_code=400)

    try:
        body = await request.json()
        # 课后学习资料.html 传的参数名叫 question
        question = body.get("question", "")
        system_prompt = body.get("system_prompt", """你是一个专业、耐心的深度学习助教，面向初中生讲解卷积核知识。
### 回答要求：
1. 排版清晰：必须分段，用数字列表或项目符号展示要点，大段内容要拆分
2. 语言简单：避免专业术语，用初中生能理解的通俗语言解释
3. 重点突出：重要概念用**加粗**标记，关键步骤单独成行
4. 结构友好：先讲结论，再讲细节，例子单独展示
5. 避免密集：每部分内容不要超过3行，多空行分隔
""")

        if not question:
            return JSONResponse({"error": "消息不能为空"}, status_code=400)

        url = f"{DASHSCOPE_BASE_URL}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": QWEN_MODEL,
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ]
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if "output" in result and "choices" in result["output"]:
            ai_response = result["output"]["choices"][0]["message"]["content"]
            # 关键：老版本 HTML 期望的返回值格式是 {"content": "..."}
            return {"content": ai_response}
        else:
            return JSONResponse({"error": "API响应异常"}, status_code=500)

    except requests.Timeout:
        return JSONResponse({"error": "请求超时"}, status_code=504)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ============ 视频流 ============
@app.get("/video/stream")
async def stream_video(request: Request):
    """视频流式传输 (支持拖动进度条/Range断点续传)"""
    if not VIDEO_FILE.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    file_size = VIDEO_FILE.stat().st_size
    range_header = request.headers.get("Range")

    if range_header:
        # 解析 Range 头，例如 "bytes=5000000-10000000"
        range_str = range_header.replace("bytes=", "")
        start_str, end_str = range_str.split("-")
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1
        status_code = 206  # 206 Partial Content 表示部分内容
    else:
        start = 0
        end = file_size - 1
        status_code = 200

    # 确保 range 合法
    if start >= file_size or end >= file_size:
        return StreamingResponse(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})

    chunk_size = end - start + 1

    def iter_file_range(start_byte, length):
        with open(VIDEO_FILE, "rb") as f:
            f.seek(start_byte)  # 直接跳到浏览器请求的时间点
            bytes_read = 0
            while bytes_read < length:
                read_size = min(1024 * 1024, length - bytes_read)  # 每次读1MB
                chunk = f.read(read_size)
                if not chunk:
                    break
                bytes_read += len(chunk)
                yield chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": "video/mp4",
    }

    return StreamingResponse(
        iter_file_range(start, chunk_size),
        status_code=status_code,
        headers=headers
    )


# ============ 新增：截图笔记与导出API ============
@app.post("/api/screenshot")
async def save_screenshot(request: Request):
    """保存前端传来的视频截图"""
    try:
        data = await request.json()
        image_data = data.get("image", "")
        if not image_data:
            return {"success": False, "error": "没有收到图片数据"}

        # 解析 base64 (格式: data:image/png;base64,iVBORw0KGgo...)
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        filename = f"screenshot_{int(time.time())}.png"
        filepath = screenshots_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(img_bytes)

        return {"success": True, "url": f"/static/screenshots/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/analyze-screenshot")
async def analyze_screenshot(request: Request):
    """调用千问大模型进行图像视觉分析 (多模态)"""
    if not DASHSCOPE_API_KEY:
        return JSONResponse({"error": "未配置 DashScope API Key"}, status_code=400)

    try:
        data = await request.json()
        image_url = data.get("image_path")
        if not image_url:
            return JSONResponse({"error": "缺少图片参数"}, status_code=400)

        # 提取真实文件路径
        filename = image_url.split("/")[-1]
        filepath = screenshots_dir / filename
        if not filepath.exists():
            return JSONResponse({"error": "图片文件不存在"}, status_code=404)

        # 转换为 base64 以保证 API 可以读取到本地图片
        with open(filepath, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')

        # 使用兼容 OpenAI 格式的多模态请求 (调用 qwen-vl-plus)
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-vl-plus",  # 视觉模型
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                        },
                        {
                            "type": "text",
                            "text": "你是一个专业的计算机视觉助教。请仔细观察这张视频教学截图，提取其中关于卷积核或图像处理的核心知识点，用通俗易懂的语言总结画面内容。要求简明扼要，有条理。"
                        }
                    ]
                }
            ]
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=40)
        result = resp.json()

        if "choices" in result and len(result["choices"]) > 0:
            ai_text = result["choices"][0]["message"]["content"]
            # 简单处理 Markdown 换行，使其在前端可以正常显示
            formatted_text = ai_text.replace('\n', '<br>')
            return {"content": formatted_text}
        else:
            return {"error": f"大模型无法解析图片，请稍后重试。"}
    except requests.Timeout:
        return {"error": "AI 解析超时，可能图片较大或网络拥堵"}
    except Exception as e:
        return {"error": f"服务器内部错误: {str(e)}"}


@app.post("/api/export-word")
async def export_word(request: Request):
    """导出为 Word 兼容格式 (无需安装 python-docx 依赖)"""
    try:
        data = await request.json()
        notes = data.get("notes", [])
        
        # 组装纯净的 HTML，Word 能够原生无损解析这套结构
        html_content = "<html><head><meta charset='utf-8'><title>学习笔记</title></head><body>"
        html_content += "<h1 style='text-align:center;'>计算机视觉微课 - 学习笔记</h1><hr/>"
        
        for i, note in enumerate(notes):
            html_content += f"<h2>截图 {i+1}</h2>"
            # 植入 Base64 图片，确保断网也能看
            img_path = BASE_DIR / note['image_url'].lstrip('/')
            if img_path.exists():
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                html_content += f"<img src='data:image/png;base64,{b64}' width='500'/><br><br>"
                
            if note.get('user_note'):
                html_content += f"<h3>📝 我的感悟：</h3><p style='background:#f5f5f5;padding:10px;'>{note['user_note']}</p>"
            if note.get('ai_analysis'):
                html_content += f"<h3>🤖 AI 分析：</h3><p style='background:#eef8ff;padding:10px;'>{note['ai_analysis']}</p>"
            html_content += "<br><hr/>"
            
        html_content += "</body></html>"
        
        filename = f"StudyNotes_{int(time.time())}.doc"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/export-pdf")
async def export_pdf(request: Request):
    """生成排版精美的独立网页，便于用户通过浏览器打印成高清 PDF (免依赖)"""
    try:
        data = await request.json()
        notes = data.get("notes", [])
        
        html_content = f"""
        <html><head><meta charset='utf-8'><title>学习笔记 (PDF打印版)</title>
        <style>
            body {{ font-family: 'PingFang SC', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }}
            h1 {{ text-align: center; color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }}
            .note-card {{ border: 1px solid #cbd5e1; padding: 20px; margin-bottom: 30px; border-radius: 12px; page-break-inside: avoid; background: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            img {{ max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0; margin: 15px 0; }}
            .section {{ padding: 15px; border-radius: 8px; margin-top: 15px; }}
            .user-note {{ background: #f8fafc; border-left: 4px solid #3b82f6; }}
            .ai-note {{ background: #faf5ff; border-left: 4px solid #a855f7; }}
            @media print {{ body {{ padding: 0; }} .note-card {{ box-shadow: none; border: 1px solid #000; }} }}
        </style>
        </head><body onload="setTimeout(()=>window.print(), 500)">
        <h1>计算机视觉微课 - 学习笔记</h1>
        """
        
        for i, note in enumerate(notes):
            html_content += f"<div class='note-card'><h2>关键画面 {i+1}</h2>"
            img_path = BASE_DIR / note['image_url'].lstrip('/')
            if img_path.exists():
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                html_content += f"<img src='data:image/png;base64,{b64}'/>"
            
            if note.get('user_note'):
                html_content += f"<div class='section user-note'><b>📝 我的感悟：</b><br>{note['user_note']}</div>"
            if note.get('ai_analysis'):
                html_content += f"<div class='section ai-note'><b>🤖 AI 分析：</b><br>{note['ai_analysis']}</div>"
            html_content += "</div>"
            
        html_content += "</body></html>"
        
        filename = f"StudyNotes_Print_{int(time.time())}.html"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ 错题本导出接口 ============
@app.post("/api/export-wrong-word")
async def export_wrong_word(request: Request):
    """导出错题本为Word格式"""
    try:
        data = await request.json()
        wrongQuestions = data.get("wrongQuestions", [])

        html_content = "<html><head><meta charset='utf-8'><title>卷积核错题本</title></head><body>"
        html_content += "<h1 style='text-align:center;'>卷积核课后练习 - 错题本</h1><hr/>"

        for i, q in enumerate(wrongQuestions):
            html_content += f"<h2>{i+1}. {q['title']}</h2>"
            html_content += f"<p><strong>题目：</strong>{q['question']}</p>"
            html_content += "<h3>选项：</h3><ul>"
            for opt in q['options']:
                if opt == q['correctAnswer']:
                    html_content += f"<li style='color: green;'>{opt} ✅ (正确答案)</li>"
                elif opt.startswith(q['userChoice']):
                    html_content += f"<li style='color: red;'>{opt} ❌ (你的选择)</li>"
                else:
                    html_content += f"<li>{opt}</li>"
            html_content += "</ul>"
            html_content += f"<p><strong>AI解析：</strong></p><p style='background:#f5f3ff;padding:10px;'>{q['aiExplanation']}</p>"
            html_content += f"<p style='color:#666;'>添加时间：{q['addTime']}</p>"
            html_content += "<br><hr/>"

        html_content += "</body></html>"

        filename = f"WrongQuestions_{int(time.time())}.doc"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/export-wrong-pdf")
async def export_wrong_pdf(request: Request):
    """导出错题本为PDF格式"""
    try:
        data = await request.json()
        wrongQuestions = data.get("wrongQuestions", [])

        html_content = f"""
        <html><head><meta charset='utf-8'><title>错题本 (PDF打印版)</title>
        <style>
            body {{ font-family: 'PingFang SC', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }}
            h1 {{ text-align: center; color: #991B1B; border-bottom: 2px solid #FECDD3; padding-bottom: 20px; }}
            .wrong-card {{ border: 1px solid #FECDD3; padding: 20px; margin-bottom: 30px; border-radius: 12px; page-break-inside: avoid; background: #FFF1F2; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .option-item {{ margin: 5px 0; }}
            .correct {{ color: #065F46; font-weight: bold; }}
            .wrong {{ color: #991B1B; text-decoration: line-through; }}
            .ai-explanation {{ background: #F5F3FF; padding: 15px; border-radius: 8px; border-left: 4px solid #8B5CF6; margin: 10px 0; }}
            .time {{ color: #666; font-size: 0.9rem; }}
            @media print {{ body {{ padding: 0; }} .wrong-card {{ box-shadow: none; border: 1px solid #991B1B; }} }}
        </style>
        </head><body onload="setTimeout(()=>window.print(), 500)">
        <h1>📕 卷积核课后练习 - 错题本</h1>
        """

        for i, q in enumerate(wrongQuestions):
            html_content += f"<div class='wrong-card'><h2>{i+1}. {q['title']}</h2>"
            html_content += f"<p><strong>题目：</strong>{q['question']}</p>"
            html_content += "<h4>选项：</h4>"
            for opt in q['options']:
                if opt == q['correctAnswer']:
                    html_content += f"<p class='option-item correct'>{opt} ✅ (正确答案)</p>"
                elif opt.startswith(q['userChoice']):
                    html_content += f"<p class='option-item wrong'>{opt} ❌ (你的选择)</p>"
                else:
                    html_content += f"<p class='option-item'>{opt}</p>"
            html_content += f"<div class='ai-explanation'><strong>🤖 AI解析：</strong><br>{q['aiExplanation']}</div>"
            html_content += f"<p class='time'>添加时间：{q['addTime']}</p>"
            html_content += "</div>"

        html_content += "</body></html>"

        filename = f"WrongQuestions_Print_{int(time.time())}.html"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ 学习笔记导出接口 ============
@app.post("/api/export-notes-word")
async def export_notes_word(request: Request):
    """导出学习笔记为Word格式"""
    try:
        data = await request.json()
        content = data.get("content", "")

        if not content or content.strip() == '':
            return {"success": False, "error": "笔记内容为空"}

        html_content = "<html><head><meta charset='utf-8'><title>卷积核学习笔记</title></head><body>"
        html_content += "<h1 style='text-align:center;'>卷积核学习笔记</h1><hr/>"
        html_content += content
        html_content += f"<br><br><p style='text-align:right; color:#666;'>导出时间：{time.strftime('%Y-%m-%d %H:%M:%S')}</p>"
        html_content += "</body></html>"

        filename = f"StudyNotes_{int(time.time())}.doc"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/export-notes-pdf")
async def export_notes_pdf(request: Request):
    """导出学习笔记为PDF格式"""
    try:
        data = await request.json()
        content = data.get("content", "")

        if not content or content.strip() == '':
            return {"success": False, "error": "笔记内容为空"}

        html_content = f"""
        <html><head><meta charset='utf-8'><title>学习笔记 (PDF打印版)</title>
        <style>
            body {{ font-family: 'PingFang SC', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }}
            h1 {{ text-align: center; color: #3B82F6; border-bottom: 2px solid #DBEAFE; padding-bottom: 20px; }}
            .note-content {{ line-height: 1.8; }}
            img {{ max-width: 100%; border-radius: 8px; margin: 10px 0; }}
            .footer {{ text-align: right; color: #666; margin-top: 40px; padding-top: 20px; border-top: 1px solid #E2E8F0; }}
            @media print {{ body {{ padding: 0; }} }}
        </style>
        </head><body onload="setTimeout(()=>window.print(), 500)">
        <h1>📝 卷积核学习笔记</h1>
        <div class="note-content">
        {content}
        </div>
        <div class="footer">
            导出时间：{time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        </body></html>
        """

        filename = f"StudyNotes_Print_{int(time.time())}.html"
        filepath = exports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {"success": True, "url": f"/static/exports/{filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============ 健康检查 ============
@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "video_exists": VIDEO_FILE.exists(),
        "html_exists": HTML_FILE.exists(),
        "api_configured": bool(DASHSCOPE_API_KEY)
    }


# ============ 启动 ============
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║           卷积核微课 - 虚拟实验室 启动中...                     ║
╠══════════════════════════════════════════════════════════════╣
║  访问地址: http://localhost:9000                               ║
║                                                               ║
║  功能页面:                                                    ║
║    📺 微课观影: http://localhost:9000/                        ║
║    📚 课后学习: http://localhost:9000/study                    ║
║    🤖 AI助教:   http://localhost:9000/ai-tutor                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=9000)