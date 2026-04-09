# 卷积核微课 - 虚拟实验室

一个基于FastAPI的计算机视觉微课学习平台。

## 功能特点

- 📺 **微课观影** - 观看卷积核核心知识的教学视频
- 📚 **课后学习** - 交互式HTML学习资料
- 🤖 **AI助教** - 基于千问大模型的智能问答助手

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：（我配了）
复制 `.env.example` 为 `.env` 并填入你的API密钥：
```
DASHSCOPE_API_KEY=你的千问API密钥
```

3. 运行应用：
```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

4. 打开浏览器访问：http://localhost:5000

## 项目结构

- `main.py` - 主应用程序（FastAPI后端）
- `DougongGrowth.mp4` - 核心微课视频
- `课后学习资料.html` - 课后学习HTML资料
- `requirements.txt` - Python依赖

## 常见问题

### 端口占用
如果遇到端口占用问题：
```cmd
netstat -ano | findstr ":5000"
taskkill /PID <PID> /F
```