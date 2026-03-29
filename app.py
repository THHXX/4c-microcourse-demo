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

    # 初始化学习状态
    if "learn_state" not in st.session_state:
        st.session_state["learn_state"] = {
            "q1_answered": False,
            "q2_answered": False,
            "q3_answered": False,
            "q1_answer": None,
            "q2_answer": None,
            "q3_answer": None,
            "ai_responses": {}
        }

    # 题目1
    with st.expander("📝 题目1：图像的计算机表示", expanded=True):
        st.markdown("计算机中存储图像最常用的数据结构是什么？")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("A. 矢量方程", key="q1_a"):
                st.session_state["learn_state"]["q1_answered"] = True
                st.session_state["learn_state"]["q1_answer"] = "A"
                if "A" != "B":  # 正确答案
                    prompt = "学生选择了'A. 矢量方程'，这是错误的。请给出纠错提示，说明照片是像素图。"
                    resp = call_qwen_api(prompt)
                    st.session_state["learn_state"]["ai_responses"]["q1"] = resp
                st.rerun()
        with col2:
            if st.button("B. 矩阵/像素阵列", key="q1_b"):
                st.session_state["learn_state"]["q1_answered"] = True
                st.session_state["learn_state"]["q1_answer"] = "B"
                st.rerun()

        if st.session_state["learn_state"]["q1_answered"]:
            if st.session_state["learn_state"]["q1_answer"] == "B":
                st.success("✅ 正确！图像在计算机中用矩阵表示，每个像素是一个数值。")
            else:
                st.error("❌ 不对哦~")
                if "q1" in st.session_state["learn_state"]["ai_responses"]:
                    st.info(st.session_state["learn_state"]["ai_responses"]["q1"])

    # 题目2
    with st.expander("📝 题目2：卷积运算"):
        st.markdown("计算卷积：与核 [[-1,0,1],[-1,0,1],[-1,0,1]] 的点积结果？")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("A. 0", key="q2_a"):
                st.session_state["learn_state"]["q2_answered"] = True
                st.session_state["learn_state"]["q2_answer"] = "A"
                st.rerun()
        with col2:
            if st.button("B. 3", key="q2_b"):
                st.session_state["learn_state"]["q2_answered"] = True
                st.session_state["learn_state"]["q2_answer"] = "B"
                if "B" != "B":
                    prompt = "请给出提示"
                    resp = call_qwen_api(prompt)
                    st.session_state["learn_state"]["ai_responses"]["q2"] = resp
                st.rerun()

        if st.session_state["learn_state"]["q2_answered"]:
            if st.session_state["learn_state"]["q2_answer"] == "B":
                st.success("✅ 正确！")

    # 题目3
    with st.expander("📝 题目3：卷积核方向"):
        st.markdown("核 [[-1,0,1],[-1,0,1],[-1,0,1]] 检测什么方向的边缘？")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("A. 水平", key="q3_a"):
                st.session_state["learn_state"]["q3_answered"] = True
                st.session_state["learn_state"]["q3_answer"] = "A"
                st.rerun()
        with col2:
            if st.button("B. 垂直", key="q3_b"):
                st.session_state["learn_state"]["q3_answered"] = True
                st.session_state["learn_state"]["q3_answer"] = "B"
                st.rerun()

        if st.session_state["learn_state"]["q3_answered"]:
            if st.session_state["learn_state"]["q3_answer"] == "B":
                st.success("✅ 正确！这是左右结构的核，检测垂直边缘。")

    # AI讨论区
    st.markdown("---")
    st.markdown("### 💬 与AI讨论学习")
    user_thought = st.text_area("写下你的学习心得或疑问，AI会和你讨论：", key="thought_input")
    if st.button("🚀 提交与AI交流"):
        if user_thought:
            with st.spinner("AI正在思考..."):
                prompt = f"请与学生进行深度讨论，主题是：{user_thought}"
                response = call_qwen_api(prompt)
                st.info(response)

    # 学习报告
    st.markdown("---")
    if st.button("📊 生成AI学习报告"):
        with st.spinner("正在生成报告..."):
            summary = "学生完成了课后学习，请生成个性化学习报告。"
            report = call_qwen_api(summary)
            st.markdown(f"**🏆 你的AI学习报告：**\n\n{report}")

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
