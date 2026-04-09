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
HTML_FILE = BASE_DIR / "课后学习资料.html"

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
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: 'Inter', -apple-system, 'PingFang SC', sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{
                text-align: center;
                padding: 40px 0;
            }}
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #00d9ff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .header p {{
                color: #8892b0;
                font-size: 1.1rem;
            }}
            .nav-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                margin-top: 40px;
            }}
            .nav-card {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 30px;
                text-decoration: none;
                color: white;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }}
            .nav-card:hover {{
                transform: translateY(-5px);
                background: rgba(255,255,255,0.1);
                border-color: rgba(0,217,255,0.3);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }}
            .nav-card i {{
                font-size: 2.5rem;
                margin-bottom: 20px;
            }}
            .nav-card h2 {{
                font-size: 1.5rem;
                margin-bottom: 10px;
            }}
            .nav-card p {{
                color: #8892b0;
                line-height: 1.6;
            }}
            .card-video i {{ color: #00d9ff; }}
            .card-study i {{ color: #00ff88; }}
            .card-ai i {{ color: #a855f7; }}
            .video-player {{
                margin-top: 40px;
                background: rgba(0,0,0,0.3);
                border-radius: 16px;
                padding: 20px;
            }}
            .video-player h2 {{
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .video-wrapper {{
                background: #000;
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
                color: #666;
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
                    <p style="color: #8892b0; font-size: 0.95rem;"><i class="fas fa-lightbulb"></i> 提示：遇到重点知识，可以随时截取画面并记录笔记</p>
                    <button class="btn-screenshot" onclick="takeScreenshot()"><i class="fas fa-camera"></i> 截屏记笔记</button>
                </div>
            </div>
        </div>

        <!-- 浮动笔记按钮 -->
        <button class="floating-btn" onclick="togglePanel()" id="floatingBtn">
            <i class="fas fa-book"></i><br>笔记
        </button>

        <!-- 侧边截图与笔记面板 -->
        <div class="screenshot-panel" id="screenshotPanel">
            <div class="panel-header">
                <h3><i class="fas fa-clipboard-list"></i> 视频笔记</h3>
                <button class="panel-close" onclick="togglePanel()"><i class="fas fa-times"></i></button>
            </div>
            <div class="panel-content" id="screenshotList">
                <div class="empty-panel">
                    <i class="fas fa-image" style="font-size: 3rem; color: #444; margin-bottom: 15px;"></i>
                    <p style="color: #8892b0;">暂无笔记，点击视频下方的<br>"截屏记笔记"捕获画面</p>
                </div>
            </div>
            <div class="export-buttons">
                <button class="btn-export doc-btn" onclick="exportWord()"><i class="fas fa-file-word"></i> 导出 Word</button>
                <button class="btn-export pdf-btn" onclick="exportPDF()"><i class="fas fa-file-pdf"></i> 导出 PDF</button>
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
                background: linear-gradient(135deg, #00d9ff, #0073ff);
                color: white; border: none; padding: 12px 24px; border-radius: 12px;
                font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease;
            }
            .btn-screenshot:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 217, 255, 0.3); }
            
            .floating-btn {
                position: fixed; right: 20px; top: 50%; transform: translateY(-50%);
                background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
                color: white; padding: 15px 10px; border-radius: 12px; backdrop-filter: blur(10px);
                cursor: pointer; transition: 0.3s; z-index: 999; box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .floating-btn:hover { background: rgba(255,255,255,0.2); border-color: #00d9ff; }
            
            .screenshot-panel {
                position: fixed; right: -420px; top: 0; width: 420px; height: 100vh;
                background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(15px);
                border-left: 1px solid rgba(255,255,255,0.1); box-shadow: -10px 0 30px rgba(0,0,0,0.5);
                transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1); z-index: 1000;
                display: flex; flex-direction: column;
            }
            .screenshot-panel.open { right: 0; }
            .panel-header {
                padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);
                display: flex; justify-content: space-between; align-items: center;
            }
            .panel-header h3 { color: #00d9ff; font-size: 1.2rem; }
            .panel-close { background: none; border: none; color: #8892b0; font-size: 1.2rem; cursor: pointer; transition: 0.2s; }
            .panel-close:hover { color: #ff4757; }
            
            .panel-content { flex: 1; overflow-y: auto; padding: 15px; }
            .screenshot-item {
                background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px; margin-bottom: 20px; overflow: hidden;
            }
            .screenshot-img { width: 100%; aspect-ratio: 16/9; object-fit: cover; cursor: zoom-in; border-bottom: 1px solid rgba(255,255,255,0.1); }
            .screenshot-actions { padding: 10px; display: flex; gap: 8px; }
            .screenshot-actions button {
                flex: 1; padding: 8px; border: none; border-radius: 6px; color: white;
                font-size: 0.85rem; cursor: pointer; transition: 0.2s; font-weight: 500;
            }
            .btn-ai { background: linear-gradient(135deg, #a855f7, #7c3aed); }
            .btn-del { background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid rgba(255, 71, 87, 0.3); }
            .btn-ai:hover { box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4); }
            .btn-del:hover { background: #ff4757; color: white; }
            
            .note-area { padding: 0 10px 10px 10px; }
            .note-input {
                width: 100%; min-height: 60px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px; color: white; padding: 10px; font-size: 0.9rem; resize: vertical; outline: none;
            }
            .note-input:focus { border-color: #00d9ff; }
            
            .ai-result {
                margin: 0 10px 10px 10px; padding: 12px; background: rgba(168, 85, 247, 0.1);
                border-left: 3px solid #a855f7; border-radius: 0 8px 8px 0; font-size: 0.85rem;
                line-height: 1.5; color: #e2e8f0; max-height: 150px; overflow-y: auto;
            }
            
            .export-buttons { padding: 15px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 10px; }
            .btn-export { flex: 1; padding: 12px; border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; transition: 0.3s; }
            .doc-btn { background: #2b579a; }
            .pdf-btn { background: #c9302c; }
            .btn-export:hover { filter: brightness(1.2); }
            
            .modal {
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.85); z-index: 2000; justify-content: center; align-items: center;
                backdrop-filter: blur(5px);
            }
            .modal.open { display: flex; }
            .modal-content img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
        </style>

        <script>
            let notesData = [];

            function togglePanel() {
                const panel = document.getElementById('screenshotPanel');
                const floatingBtn = document.getElementById('floatingBtn');
                panel.classList.toggle('open');
                floatingBtn.style.display = panel.classList.contains('open') ? 'none' : 'block';
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
                
                // 打开面板
                document.getElementById('screenshotPanel').classList.add('open');
                document.getElementById('floatingBtn').style.display = 'none';
                
                // 占位加载效果
                const list = document.getElementById('screenshotList');
                if (notesData.length === 0) list.innerHTML = '';
                
                const tempId = 'loading-' + Date.now();
                list.innerHTML += `<div class="screenshot-item" id="${tempId}" style="text-align:center; padding: 20px;"><i class="fas fa-spinner fa-spin" style="font-size:2rem; color:#00d9ff;"></i><p>正在保存截图...</p></div>`;
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
                    list.innerHTML = `<div class="empty-panel"><i class="fas fa-image" style="font-size: 3rem; color: #444; margin-bottom: 15px;"></i><p style="color: #8892b0;">暂无笔记，点击视频下方的<br>"截屏记笔记"捕获画面</p></div>`;
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
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: 'Inter', -apple-system, 'PingFang SC', sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                color: white;
            }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
            .header {{
                text-align: center;
                padding: 30px 0;
            }}
            .header h1 {{
                font-size: 2rem;
                margin-bottom: 10px;
            }}
            .header h1 i {{ color: #a855f7; margin-right: 10px; }}
            .back-link {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: #8892b0;
                text-decoration: none;
                margin-bottom: 20px;
                transition: 0.2s;
            }}
            .back-link:hover {{ color: #00d9ff; }}
            .chat-container {{
                background: rgba(255,255,255,0.05);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                overflow: hidden;
            }}
            .chat-messages {{
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}
            .message {{
                max-width: 80%;
                padding: 16px 20px;
                border-radius: 16px;
                line-height: 1.6;
            }}
            .message.user {{
                align-self: flex-end;
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                border-bottom-right-radius: 4px;
            }}
            .message.assistant {{
                align-self: flex-start;
                background: rgba(255,255,255,0.1);
                border-bottom-left-radius: 4px;
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
                background: rgba(255,255,255,0.2);
            }}
            .message.assistant .avatar {{
                background: #a855f7;
            }}
            .chat-input-area {{
                padding: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
                display: flex;
                gap: 12px;
            }}
            .chat-input {{
                flex: 1;
                padding: 14px 20px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 12px;
                background: rgba(255,255,255,0.05);
                color: white;
                font-size: 1rem;
                outline: none;
                transition: 0.2s;
            }}
            .chat-input::placeholder {{ color: #666; }}
            .chat-input:focus {{ border-color: #a855f7; }}
            .send-btn {{
                padding: 14px 28px;
                background: linear-gradient(135deg, #a855f7, #7c3aed);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1rem;
                cursor: pointer;
                transition: 0.2s;
            }}
            .send-btn:hover {{ transform: scale(1.05); }}
            .send-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
            .no-api-key {{
                text-align: center;
                padding: 60px 20px;
            }}
            .no-api-key i {{
                font-size: 4rem;
                color: #f59e0b;
                margin-bottom: 20px;
            }}
            .no-api-key h2 {{ margin-bottom: 10px; }}
            .no-api-key p {{ color: #8892b0; }}
            .loading {{
                display: flex;
                align-items: center;
                gap: 10px;
                color: #8892b0;
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
                color: #8892b0;
            }}
            .welcome-message i {{
                font-size: 3rem;
                color: #a855f7;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link"><i class="fas fa-arrow-left"></i> 返回首页</a>

            <div class="header">
                <h1><i class="fas fa-robot"></i> AI助教</h1>
                <p>基于千问大模型的智能问答助手</p>
            </div>
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
            <div class="chat-container">
                <div class="chat-messages" id="messages">
                    <div class="welcome-message">
                        <i class="fas fa-robot"></i>
                        <h3>你好！我是AI助教</h3>
                        <p>关于卷积核的任何问题都可以问我</p>
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="userInput"
                           placeholder="请输入关于卷积核的问题..." autofocus>
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

                // 添加用户消息
                addMessage(message, 'user');
                userInput.value = '';

                // 显示加载状态
                const loadingMsg = addMessage('<div class="loading"><i class="fas fa-spinner"></i> AI思考中...</div>', 'assistant');

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
                        addMessage('错误: ' + data.error, 'assistant');
                    }} else {{
                        addMessage(data.response, 'assistant');
                    }}
                }} catch (err) {{
                    loadingMsg.remove();
                    addMessage('请求失败: ' + err.message, 'assistant');
                }}
            }}

            function addMessage(html, role) {{
                const div = document.createElement('div');
                div.className = 'message ' + role;
                div.innerHTML = '<span class="avatar"><i class="fas fa-' + (role === 'user' ? 'user' : 'robot') + '"></i></span>' + html;
                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return div;
            }}
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
        system_prompt = """你是一位专业的计算机视觉助教，专门教授卷积核（Convolution Kernel）的相关知识。

你可以帮助学生理解以下内容：
1. 卷积核的定义和原理
2. 常见卷积核类型（边缘检测、模糊、锐化、 Sobel等）
3. 卷积操作的过程和计算
4. 卷积神经网络中卷积层的作用
5. 实际应用场景和例子

请用通俗易懂的语言解释概念，提供具体的例子，并在适当的时候使用数学公式或代码演示。
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
        system_prompt = body.get("system_prompt", "你是一个专业、耐心的深度学习助教。")

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
║  访问地址: http://localhost:5000                               ║
║                                                               ║
║  功能页面:                                                    ║
║    📺 微课观影: http://localhost:5000/                        ║
║    📚 课后学习: http://localhost:5000/study                    ║
║    🤖 AI助教:   http://localhost:5000/ai-tutor                ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(app, host="0.0.0.0", port=5000)