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

    # 显示原有HTML内容
    html_path = "课后学习资料.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        # 只显示HTML的学习内容部分，不包含交互（交互由下方Streamlit接管）
        components.html(html_content, height=1200, scrolling=True)
    else:
        st.error(f"未找到 HTML 文件: {html_path}")

    # 在下方添加AI学习助手（Streamlit原生实现）
    st.markdown("---")
    st.markdown("### 🤖 AI 学习助手")
    st.info("💡 在这里可以获取学习提示、纠错帮助，或与AI讨论学习心得！")

    # 初始化Tab2的session_state
    if "tab2_response" not in st.session_state:
        st.session_state["tab2_response"] = None

    # 选择功能类型
    ai_mode = st.selectbox("选择功能：", ["💡 获取提示", "❌ 错题解析", "💬 学习讨论", "📊 学习报告"], key="ai_mode_tab2")

    if ai_mode == "💡 获取提示":
        topic = st.selectbox("选择主题：", ["图像表示", "卷积运算", "边缘检测", "其他问题"], key="topic_tab2")
        if st.button("获取AI提示", key="btn_hint"):
            prompts = {
                "图像表示": "请给我一个关于'图像在计算机中如何表示'的简洁提示，帮助学生理解像素和矩阵的概念。",
                "卷积运算": "请给我一个关于'卷积运算如何进行'的简洁提示，引导学生理解滑动窗口和点积的概念。",
                "边缘检测": "请给我一个关于'卷积核如何检测边缘'的简洁提示，帮助学生理解不同方向核的作用。",
                "其他问题": "请给我一个学习卷积核的提示。"
            }
            with st.spinner("AI正在思考..."):
                result = call_qwen_api(prompts[topic])
                st.session_state["tab2_response"] = result.get("content") or result.get("error", "未知错误")
                st.rerun()

    elif ai_mode == "❌ 错题解析":
        wrong_topic = st.text_input("输入你做错的题目或知识点：", key="wrong_topic")
        if st.button("获取错题解析", key="btn_error"):
            if wrong_topic:
                with st.spinner("AI正在分析..."):
                    prompt = f"请分析以下学习难点，给出详细的错题解析和正确思路：{wrong_topic}"
                    result = call_qwen_api(prompt)
                    st.session_state["tab2_response"] = result.get("content") or result.get("error", "未知错误")
                    st.rerun()

    elif ai_mode == "💬 学习讨论":
        thought = st.text_area("写下你的学习心得或疑问：", key="thought_tab2")
        if st.button("与AI讨论", key="btn_discuss"):
            if thought:
                with st.spinner("AI正在与你讨论..."):
                    prompt = f"请与学生进行友好的学习讨论，给出鼓励和深入的引导，主题是：{thought}"
                    result = call_qwen_api(prompt)
                    st.session_state["tab2_response"] = result.get("content") or result.get("error", "未知错误")
                    st.rerun()

    elif ai_mode == "📊 学习报告":
        if st.button("生成学习报告", key="btn_report"):
            with st.spinner("正在生成个性化报告..."):
                prompt = "请根据学生的学习情况，生成一份个性化学习报告，包括学习进度、掌握程度和建议。"
                result = call_qwen_api(prompt)
                st.session_state["tab2_response"] = result.get("content") or result.get("error", "未知错误")
                st.rerun()

    # 渲染结果（在按钮外部，重跑后依然存在）
    if st.session_state["tab2_response"]:
        if "错误" in st.session_state["tab2_response"] or "请" in st.session_state["tab2_response"]:
            st.error(st.session_state["tab2_response"])
        else:
            st.success(st.session_state["tab2_response"])

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

    # 聊天输入框
    if prompt := st.chat_input("💭 输入你的问题，比如：卷积核是如何提取图像特征的？"):
        # 添加用户消息
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # 调用 AI 回复
        with st.spinner("AI 正在思考..."):
            result = call_qwen_api(prompt)
            content = result.get("content") or result.get("error", "请求失败")

        # 添加AI回复到历史
        st.session_state["messages"].append({"role": "assistant", "content": content})
        st.rerun()

    # 渲染聊天记录（在输入框之后，确保重跑后消息不丢失）
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
