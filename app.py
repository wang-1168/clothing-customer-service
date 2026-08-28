"""服装电商智能客服 RAG 系统 - 入口文件"""
import streamlit as st

from config import API_KEY
from chat_app import ChatApp


def main():
    st.set_page_config(page_title="服装智能客服", page_icon="👕",
                       layout="wide", initial_sidebar_state="expanded")
    st.markdown(ChatApp.CSS, unsafe_allow_html=True)
    if not API_KEY:
        st.error("未检测到 DashScope API Key，请设置环境变量 OPEN_AI_API_KEY 后重试。")
        st.stop()
    ChatApp.init_state()
    ChatApp().run()


if __name__ == "__main__":
    main()
