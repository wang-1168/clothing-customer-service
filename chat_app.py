"""前端应用模块 - Streamlit 界面与交互"""
import json
import time

import streamlit as st

from config import DATA_FILE, BG_URL
from vector_store import VectorStoreService
from rag_service import RagService


class ChatApp:
    VERSION = "1.3.0"
    INIT_MSG = "您好！我是服装客服小助手 👕，可为您解答尺码、退换货、物流、面料洗护等问题，请问有什么可以帮您？"
    QUICK_QUESTIONS = ["男装175cm 70kg穿什么码？", "7天无理由退换货规则？", "顺丰一般几天送达？",
                       "羊毛衫怎么洗护？", "满多少包邮？"]
    PAGES = ["💬 智能客服", "📚 知识库", "⚙️ 设置", "ℹ️ 关于"]
    TECHS = [("Streamlit", "交互式前端"), ("LangChain", "编排检索-生成链路"),
             ("Chroma", "本地持久化向量库"), ("DashScope Embedding", "text-embedding-v2"),
             ("通义千问 ChatTongyi", "大语言模型生成")]

    CSS = f"""
    <style>
    html, body, .stApp {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif; }}

    .stApp {{
        background:
            linear-gradient(135deg, rgba(255,248,240,0.70) 0%, rgba(244,228,234,0.78) 100%),
            url('{BG_URL}') center/cover no-repeat fixed;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(26,8,16,0.97) 0%, rgba(50,18,34,0.97) 100%);
        backdrop-filter: blur(6px);
        border-right: 1px solid rgba(212,160,23,0.20);
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] p {{ color: #f3e4ea !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: rgba(212,160,23,0.20); }}
    .sidebar-logo {{ font-size: 22px; font-weight: 800;
        background: linear-gradient(135deg,#fff 0%,#e8a9bd 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .sidebar-sub {{ font-size: 12px; color:#e8a9bd; letter-spacing:0.5px; }}

    .app-header {{ display:flex; align-items:center; justify-content:space-between;
        padding: 8px 0 16px 0; border-bottom: 1px solid rgba(212,160,23,0.28); margin-bottom: 12px; }}
    .app-title {{ font-size: 26px; font-weight: 800;
        background: linear-gradient(135deg,#2b0d18 0%,#a01a4a 55%,#d4a017 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .app-subtitle {{ font-size: 13px; color:#7a5a68; margin-top: 4px; }}

    .badge {{ display:inline-flex; align-items:center; gap:6px;
        padding: 5px 14px; border-radius: 999px; font-size: 12px; font-weight:600;
        backdrop-filter: blur(4px); }}
    .badge-ok {{ background: rgba(253,234,240,0.85); color:#a01a4a; border:1px solid rgba(214,51,132,0.3); }}
    .dot {{ width:8px; height:8px; border-radius:50%; display:inline-block; }}
    .dot-ok {{ background:#d63384; animation: pulse 2s infinite; }}
    @keyframes pulse {{
        0% {{ box-shadow:0 0 0 0 rgba(214,51,132,0.5); }}
        70% {{ box-shadow:0 0 0 8px rgba(214,51,132,0); }}
        100% {{ box-shadow:0 0 0 0 rgba(214,51,132,0); }}
    }}

    .metric-card {{ background: rgba(255,250,243,0.78); backdrop-filter: blur(10px);
        border-radius:14px; padding:16px 18px;
        box-shadow:0 4px 16px rgba(74,23,41,0.10); border:1px solid rgba(212,160,23,0.22);
        height:100%; transition: all 0.25s ease; }}
    .metric-card:hover {{ transform: translateY(-3px); box-shadow:0 8px 24px rgba(74,23,41,0.16); }}
    .metric-label {{ font-size:12px; color:#8a6a78; margin-bottom:6px; letter-spacing:0.3px; }}
    .metric-value {{ font-size:22px; font-weight:700; color:#2b0d18; }}
    .metric-hint {{ font-size:11px; color:#a88a98; margin-top:4px; }}

    .stButton > button, .stDownloadButton > button {{
        border-radius: 999px; border:1px solid #a01a4a; color:#a01a4a;
        background: rgba(255,255,255,0.92); font-weight:600;
        transition: all 0.2s ease; }}
    .stButton > button:hover {{ background:#a01a4a; color:#fff; transform: translateY(-2px);
        box-shadow:0 6px 16px rgba(160,26,74,0.28); }}
    .stButton > button:active {{ transform: translateY(0); }}

    [data-testid="stChatMessage"] {{
        background: rgba(255,250,243,0.82); backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius:16px; border:1px solid rgba(212,160,23,0.25);
        border-left:5px solid #d4a017;
        box-shadow:0 4px 18px rgba(74,23,41,0.12);
        padding:14px 18px; transition: all 0.25s ease;
        animation: msgIn 0.45s cubic-bezier(0.22,1,0.36,1); }}
    [data-testid="stChatMessage"]:hover {{ box-shadow:0 8px 26px rgba(74,23,41,0.18); }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] div {{ color:#5c1530 !important;
        font-size:15.5px; line-height:1.8; }}
    [data-testid="stChatMessage"] strong {{ color:#a01a4a; }}
    @keyframes msgIn {{
        from {{ opacity:0; transform: translateY(12px); }}
        to {{ opacity:1; transform: translateY(0); }}
    }}

    [data-testid="stChatInput"] textarea {{
        border-radius: 14px !important; border:1px solid rgba(212,160,23,0.35) !important;
        background: rgba(255,250,243,0.92) !important; font-size: 15px !important; }}

    ::-webkit-scrollbar {{ width:9px; height:9px; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(160,26,74,0.3); border-radius:6px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(160,26,74,0.5); }}
    ::-webkit-scrollbar-track {{ background:transparent; }}

    footer, #MainMenu {{visibility:hidden;}}
    .stApp > header {{background:transparent;}}
    </style>
    """

    def __init__(self):
        self.ss = st.session_state

    # ---- 状态访问 ----
    @property
    def vs(self): return self.ss.vs
    @property
    def rag(self): return self.ss.rag
    @property
    def settings(self): return self.ss.settings
    @property
    def page(self): return self.ss.get("page", self.PAGES[0])
    @property
    def session(self): return self.ss.sessions.get(self.ss.current_sid)

    # ---- 初始化 / 会话管理 ----
    @classmethod
    def init_state(cls):
        ss = st.session_state
        if "vs" in ss:
            return
        vs = VectorStoreService()
        if not vs.load():
            vs.build_from_file(DATA_FILE)
        ss.vs = vs
        ss.settings = {"model": "qwen-plus", "temperature": 0.3, "k": 3, "stream": True}
        ss.rag = RagService(vs.get_retriever(k=3), "qwen-plus", 0.3)
        ss.session_counter = 0
        ss.sessions = {}
        ss.current_sid = None
        ss.page = cls.PAGES[0]
        cls.new_conversation()

    @classmethod
    def new_conversation(cls):
        ss = st.session_state
        ss.session_counter += 1
        sid = f"sess_{ss.session_counter}"
        ss.sessions[sid] = {"title": "新对话",
                           "messages": [{"role": "assistant", "content": cls.INIT_MSG, "sources": []}],
                           "created": time.time()}
        ss.current_sid = sid

    def rebuild_rag(self):
        s = self.settings
        self.ss.rag = RagService(self.vs.get_retriever(k=s["k"]), s["model"], s["temperature"])

    # ---- 工具方法 ----
    @staticmethod
    def _doc_fields(doc):
        if isinstance(doc, dict):
            content, meta = doc.get("page_content", ""), (doc.get("metadata") or {})
        else:
            content, meta = doc.page_content, (doc.metadata or {})
        src = meta.get("source", "-") if isinstance(meta, dict) else getattr(meta, "source", "-")
        return content, str(src).split("/")[-1]

    @classmethod
    def _render_sources(cls, sources):
        for i, doc in enumerate(sources, 1):
            content, src = cls._doc_fields(doc)
            st.markdown(f"**片段 {i}**　`来源: {src}`")
            st.caption(content.strip().replace("\n", "  \n"))
            st.divider()

    @staticmethod
    def _header(title, subtitle="", online=False):
        badge = '<div class="badge badge-ok"><span class="dot dot-ok"></span>在线</div>' if online else ""
        st.markdown(f"""<div class="app-header"><div>
            <div class="app-title">{title}</div>
            <div class="app-subtitle">{subtitle}</div></div>{badge}</div>""", unsafe_allow_html=True)

    def export(self, md=True):
        sess = self.session
        if not sess:
            return ""
        if md:
            lines = [f"# {sess['title']}", ""]
            for m in sess["messages"]:
                role = "👤 顾客" if m["role"] == "user" else "🧑‍💼 客服"
                lines.append(f"### {role}\n\n{m['content']}\n")
            return "\n".join(lines)
        return json.dumps({"title": sess["title"], "messages": sess["messages"]}, ensure_ascii=False, indent=2)

    # ---- 页面：智能客服 ----
    def render_chat(self):
        sess = self.session
        if sess is None:
            self.new_conversation()
            sess = self.session
        msgs = sess["messages"]

        self._header("👕 服装电商智能客服",
                     f"基于检索增强生成 (RAG) · 知识库实时检索 · 模型 {self.settings['model']}", online=True)

        c1, c2, c3, _ = st.columns([1, 1, 1, 6])
        if c1.button("🧹 清空对话", use_container_width=True):
            sess["messages"] = [{"role": "assistant", "content": self.INIT_MSG, "sources": []}]
            sess["title"] = "新对话"
            st.rerun()
        if c2.button("📄 导出 Markdown", use_container_width=True):
            self.ss["_export_fmt"] = "md"
        if c3.button("🧾 导出 JSON", use_container_width=True):
            self.ss["_export_fmt"] = "json"

        fmt = self.ss.pop("_export_fmt", None)
        if fmt:
            data = self.export(md=(fmt == "md"))
            ext = "md" if fmt == "md" else "json"
            st.download_button(f"⬇️ 下载 {ext.upper()} 文件", data,
                               file_name=f"{sess['title'] or '对话'}.{ext}", mime="text/plain")

        st.markdown("**💡 常见问题**")
        qcols = st.columns(len(self.QUICK_QUESTIONS))
        for i, q in enumerate(self.QUICK_QUESTIONS):
            if qcols[i].button(q, key=f"quick_{i}", use_container_width=True):
                self.ss["pending_question"] = q
                st.rerun()

        st.divider()

        for msg in msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander(f"📖 参考来源（{len(msg['sources'])} 条）"):
                        self._render_sources(msg["sources"])

        pending = self.ss.pop("pending_question", None)
        user_input = pending or st.chat_input("请输入您的问题，例如：男装175穿什么码？")
        if user_input:
            if sess["title"] == "新对话":
                sess["title"] = user_input[:14] + ("…" if len(user_input) > 14 else "")
            msgs.append({"role": "user", "content": user_input, "sources": []})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("正在检索知识库…"):
                    sources = self.rag.retrieve(user_input)
                if self.settings["stream"]:
                    full = st.write_stream(self.rag.stream_answer(user_input, sources))
                else:
                    with st.spinner("正在生成回答…"):
                        full = self.rag.answer(user_input, sources)
                    st.markdown(full)
                if sources:
                    with st.expander(f"📖 参考来源（{len(sources)} 条）"):
                        self._render_sources(sources)
            msgs.append({"role": "assistant", "content": full,
                         "sources": [{"page_content": d.page_content, "metadata": d.metadata} for d in sources]})
            st.rerun()

    # ---- 页面：知识库 ----
    def render_knowledge(self):
        self._header("📚 知识库管理", "查看向量库状态、重建索引、上传补充知识")
        info = self.vs.status()

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(self._metric("知识块数量", info['chunk_count'], "向量条数"))
        c2.markdown(self._metric("加载状态", '✅ 已就绪' if info['loaded'] else '⚠️ 未加载', "Chroma 向量库"))
        c3.markdown(self._metric("数据文件", f"{info['data_file_size']//1024 if info['data_file_exists'] else 0} KB",
                                 DATA_FILE if info['data_file_exists'] else '数据文件缺失'))
        c4.markdown(self._metric("集合名称", info['collection'], info['persist_dir'], small=True))

        st.write("")
        st.subheader("🔧 索引维护")
        if st.columns([1, 3])[0].button("♻️ 从数据文件重建", use_container_width=True):
            with st.spinner("正在重建向量库…"):
                try:
                    self.vs.rebuild(DATA_FILE)
                    self.rebuild_rag()
                    st.success(f"重建完成，共 {self.vs.last_chunk_count} 个知识块")
                except Exception as e:
                    st.error(f"重建失败: {e}")
                st.rerun()

        st.subheader("📤 上传补充知识")
        up = st.file_uploader("上传 .txt / .md 文件追加到知识库", type=["txt", "md"])
        if up is not None:
            try:
                text = up.read().decode("utf-8")
                if st.button("➕ 追加到向量库", use_container_width=True):
                    with st.spinner("正在切分并入库…"):
                        n = self.vs.add_text(text, source=up.name)
                        self.rebuild_rag()
                        st.success(f"成功追加 {n} 个知识块，当前共 {self.vs.last_chunk_count} 块")
                    st.rerun()
            except Exception as e:
                st.error(f"上传失败: {e}")

        st.subheader("🔍 检索测试")
        test_q = st.text_input("输入测试问题，查看检索命中的知识片段", placeholder="例如：羊毛衫怎么洗？")
        if test_q.strip():
            retriever = self.vs.get_retriever(k=self.settings["k"])
            if retriever:
                with st.spinner("检索中…"):
                    docs = retriever.invoke(test_q)
                if not docs:
                    st.warning("未检索到相关内容")
                for i, d in enumerate(docs, 1):
                    st.markdown(f"**片段 {i}**")
                    st.caption(d.page_content.strip().replace("\n", "  \n"))
                    st.divider()

    # ---- 页面：设置 ----
    def render_settings(self):
        self._header("⚙️ 参数设置", "调整模型与检索参数，应用后立即生效")
        s = self.settings
        models = ["qwen-plus", "qwen-max", "qwen-turbo"]
        new_model = st.selectbox("对话模型", models, index=models.index(s["model"]))
        new_temp = st.slider("回答多样性 (temperature)", 0.0, 1.0, float(s["temperature"]), 0.05)
        new_k = st.slider("检索片段数 (k)", 1, 8, int(s["k"]))
        new_stream = st.toggle("流式输出", value=bool(s["stream"]))
        st.divider()
        if st.columns([1, 3])[0].button("✅ 应用设置", use_container_width=True):
            self.ss.settings = {"model": new_model, "temperature": new_temp, "k": new_k, "stream": new_stream}
            self.rebuild_rag()
            st.success("设置已应用，新对话立即生效")
            st.rerun()
        st.caption("💡 qwen-max 质量更高但更慢更贵；qwen-turbo 更快更省；k 越大参考越多但可能引入噪声。")

    # ---- 页面：关于 ----
    def render_about(self):
        self._header("ℹ️ 关于本系统", "服装电商智能客服 RAG 系统")
        st.markdown(f"""<div class="metric-card">
            <h3 style="margin-top:0;color:#2b0d18">👕 服装电商智能客服</h3>
            <p style="color:#7a5a68">版本 <b>v{self.VERSION}</b> · 基于检索增强生成 (RAG) 架构</p>
            <p>本系统通过向量检索从服装知识库召回相关片段，再由大语言模型生成亲切自然的客服回答，避免无中生有。</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        st.subheader("🧩 技术栈")
        cols = st.columns(len(self.TECHS))
        for col, (name, desc) in zip(cols, self.TECHS):
            col.markdown(self._metric(name, "", desc, small=True, value_as_name=True), unsafe_allow_html=True)
        st.subheader("📖 使用说明")
        st.markdown("""1. **智能客服**：直接提问或点击常见问题，回答下方可展开查看参考来源。
2. **知识库**：查看状态、重建索引、上传 .txt/.md 补充知识、检索测试。
3. **设置**：切换模型、调整回答多样性与检索片段数，应用后生效。
4. **多会话**：左侧栏可新建 / 切换 / 删除历史对话，各自独立。""")

    # ---- 侧边栏 ----
    def render_sidebar(self):
        with st.sidebar:
            st.markdown('<div class="sidebar-logo">👕 服装客服</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-sub">智能 RAG 客服系统 v{self.VERSION}</div>', unsafe_allow_html=True)
            st.write("")
            st.radio("导航", self.PAGES, label_visibility="collapsed", key="page")

            info = self.vs.status()
            txt = f"向量库就绪 · {info['chunk_count']} 块" if info["loaded"] else "向量库未加载"
            st.markdown(f'<div style="margin:8px 0"><span class="badge badge-ok">'
                        f'<span class="dot dot-ok"></span>{txt}</span></div>', unsafe_allow_html=True)
            st.divider()

            if self.page == self.PAGES[0]:
                st.markdown("#### 💬 对话列表")
                if st.button("➕ 新建对话", use_container_width=True):
                    self.new_conversation()
                    st.rerun()
                st.write("")
                for sid, sess in self.ss.sessions.items():
                    is_active = sid == self.ss.current_sid
                    label = sess["title"] or "新对话"
                    prefix = "▶  " if is_active else "　　"
                    cols = st.columns([5, 1])
                    if cols[0].button(f"{prefix}{label}", key=f"sel_{sid}", use_container_width=True, help="切换到该对话"):
                        self.ss.current_sid = sid
                        st.rerun()
                    if cols[1].button("🗑", key=f"del_{sid}", help="删除对话"):
                        del self.ss.sessions[sid]
                        if self.ss.current_sid == sid:
                            if self.ss.sessions:
                                self.ss.current_sid = list(self.ss.sessions.keys())[-1]
                            else:
                                self.new_conversation()
                        st.rerun()
                st.divider()
                st.caption("点击会话名切换；🗑 删除；➕ 新建。")

    # ---- 卡片小工具 ----
    @staticmethod
    def _metric(label, value, hint, small=False, value_as_name=False):
        vstyle = "font-size:15px" if small else ""
        v = label if value_as_name else value
        return (f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value" style="{vstyle}">{v}</div>'
                f'<div class="metric-hint">{hint}</div></div>')

    # ---- 入口分发 ----
    def run(self):
        self.render_sidebar()
        {self.PAGES[0]: self.render_chat, self.PAGES[1]: self.render_knowledge,
         self.PAGES[2]: self.render_settings, self.PAGES[3]: self.render_about
         }.get(self.page, self.render_chat)()
