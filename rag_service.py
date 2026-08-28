"""RAG 服务模块 - 负责检索与大模型生成编排"""
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import PROMPT_TEMPLATE, API_KEY


class RagService:
    def __init__(self, retriever, model_name="qwen-plus", temperature=0.3):
        self.retriever = retriever
        self.chain = (
            {"context": lambda x: x["context"], "question": lambda x: x["question"]}
            | ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            | ChatTongyi(model=model_name, temperature=temperature, dashscope_api_key=API_KEY)
            | StrOutputParser()
        )

    def retrieve(self, question):
        if not self.retriever:
            return []
        try:
            return self.retriever.invoke(question)
        except Exception as e:
            print(f"检索失败: {e}")
            return []

    @staticmethod
    def _fmt(docs):
        return "\n\n".join(d.page_content for d in docs)

    def answer(self, question, docs):
        return self.chain.invoke({"context": self._fmt(docs), "question": question})

    def stream_answer(self, question, docs):
        yield from self.chain.stream({"context": self._fmt(docs), "question": question})
