# 卷积核微课 - 虚拟实验室

一个基于Streamlit的计算机视觉微课学习平台。

## 功能特点

- 📺 **微课观影** - 观看卷积核核心知识的教学视频
- 📚 **课后学习** - 交互式HTML学习资料
- 🤖 **AI助教** - 基于千问大模型的智能问答助手

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
复制 `.env.example` 为 `.env` 并填入你的API密钥：
```
DASHSCOPE_API_KEY=你的千问API密钥
```

3. 运行应用：
```bash
streamlit run app.py
```

## 项目结构

- `app.py` - 主应用程序
- `DougongGrowth.mp4` - 核心微课视频
- `课后学习资料.html` - 课后学习HTML资料
- `requirements.txt` - Python依赖