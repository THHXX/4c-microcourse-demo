import streamlit as st
import os
import requests
import time
import json
import streamlit.components.v1 as components

# 注意：Streamlit Cloud 的 Secrets 会自动加载为环境变量
# 本地开发时可在 .streamlit/secrets.toml 中配置，或保留 .env 文件

# 1. 页面基本设置
st.set_page_config(page_title="卷积核微课 - 虚拟实验室", page_icon="🧠", layout="wide")

# ================= API 配置 =================
# 优先使用环境变量（Streamlit Cloud Secrets），本地开发也可从 .env 加载
def get_api_key():
    key = os.getenv("DASHSCOPE_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            key = os.getenv("DASHSCOPE_API_KEY")
        except:
            pass
    return key

DASHSCOPE_API_KEY = get_api_key()
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

def call_qwen_api(prompt, system_prompt="你是一个专业、耐心的深度学习助教，擅长用简洁易懂的语言讲解卷积核和计算机视觉相关知识。"):
    """调用千问 API"""
    if not DASHSCOPE_API_KEY:
        return {"error": "请先在 Secrets 中配置 DASHSCOPE_API_KEY"}

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

    # 增加超时时间到60秒，并添加重试机制
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=60)
            if response.ok:
                data = response.json()
                return {"content": data["output"]["choices"][0]["message"]["content"]}
            elif response.status_code == 429:
                time.sleep(2)
                continue
            else:
                return {"error": f"API 错误: {response.status_code}"}
        except requests.exceptions.Timeout:
            if attempt < 2:
                continue
            return {"error": "请求超时，请稍后重试"}
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return {"error": f"连接错误: {str(e)}"}
    return {"error": "请稍后重试"}

# 检查是否是 API 调用（通过 query params）
query_params = st.query_params
if "question" in query_params and query_params["question"]:
    # API 模式：返回 JSON
    question = query_params["question"]

    # 尝试获取type参数，默认default
    hint_type = query_params.get("type", "default")
    if not hint_type:
        hint_type = "default"

    # 根据类型设置不同的 system prompt
    system_prompts = {
        "hint": "你是一个耐心的AI助教，给学生提供学习提示和引导。回复要简洁，不直接给答案。",
        "error": "你是一个耐心的AI助教，指出学生的错误并给出正确思路。不要直接说答案。",
        "discuss": "你是一个AI学习伙伴，与学生讨论他们的想法，给出鼓励和深入的问题。",
        "summary": "你是AI学习报告生成器，根据学生的学习表现生成个性化报告。",
        "default": "你是一个专业、耐心的深度学习助教，擅长讲解卷积核和计算机视觉相关知识。"
    }

    result = call_qwen_api(question, system_prompts.get(hint_type, system_prompts["default"]))
    st.json(result)
    st.stop()
elif "question" in query_params:
    # question参数存在但为空
    st.json({"error": "问题参数为空"})
    st.stop()

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
