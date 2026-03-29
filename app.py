import streamlit as st
import os
import requests
from dotenv import load_dotenv
import streamlit.components.v1 as components

# 加载环境变量
load_dotenv()

# 1. 页面基本设置
st.set_page_config(page_title="卷积核微课 - 虚拟实验室", page_icon="🧠", layout="wide")

# 自定义 CSS 样式
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        font-size: 1.4rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        white-space: pre-wrap;
        border-radius: 10px 10px 0 0;
        padding: 0 30px;
        font-size: 1.15rem;
        font-weight: 600;
    }
    .stVideo {
        border-radius: 12px;
        overflow: hidden;
    }
    .chat-container {
        border: 2px solid #E0F2FE;
        border-radius: 16px;
        padding: 20px;
        background: #F8FAFC;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 卷积核微课：揭秘计算机视觉的眼睛")
st.markdown("---")

# 使用标签页组织内容
tab1, tab2, tab3 = st.tabs(["📺  微课观影", "📚  课后学习", "🤖  AI 助教"])

# ================= 标签页 1：微课观影 =================
with tab1:
    st.subheader("🎬 核心微课")
    video_path = "DougongGrowth.mp4"
    if os.path.exists(video_path):
        st.video(video_path)
    else:
        st.error(f"未找到视频文件: {video_path}")

# ================= 标签页 2：课后学习资料 =================
with tab2:
    st.subheader("📖 课后学习资料")
    html_path = "课后学习资料.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=1500, scrolling=True)
    else:
        st.error(f"未找到 HTML 文件: {html_path}")

# ================= 标签页 3：AI 助教 =================
with tab3:
    st.subheader("💬 AI 专属助教")
    st.info("💡 在这里可以问任何关于卷积核、计算机视觉的问题！")

    # 千问 API 配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

    def call_qwen_api(prompt, system_prompt="你是一个专业、耐心的深度学习助教，擅长讲解卷积核和计算机视觉相关知识。"):
        """调用千问 API"""
        if not DASHSCOPE_API_KEY:
            return "⚠️ 请先在 .env 文件中配置 DASHSCOPE_API_KEY"

        url = f"{DASHSCOPE_BASE_URL}/services/aigc/text-generation/generation"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
        }

        body = {
            "model": QWEN_MODEL,
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)
            if response.ok:
                data = response.json()
                return data["output"]["choices"][0]["message"]["content"]
            else:
                return f"❌ API 错误: {response.status_code}"
        except Exception as e:
            return f"🔌 连接错误: {str(e)}"

    # 初始化聊天记录
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant",
             "content": "你好！我是你的专属深度学习助教。有关卷积核、计算机视觉或 Python 编程的问题，都可以问我哦！"}
        ]

    # 聊天容器
    chat_container = st.container()
    with chat_container:
        # 显示历史聊天记录
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 聊天输入框 - 放在最底部，Streamlit 自动固定在下方
    if prompt := st.chat_input("💭 输入你的问题，比如：卷积核是如何提取图像特征的？"):
        # 添加用户消息
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # 调用 AI 回复
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("AI 正在思考..."):
                    reply = call_qwen_api(prompt)
                    st.markdown(reply)
                    st.session_state["messages"].append({"role": "assistant", "content": reply})
