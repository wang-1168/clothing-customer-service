"""向量库服务模块 - 负责文本切分、向量化、持久化与检索"""
import os
import shutil

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config import CHROMA_DIR, COLLECTION, DATA_FILE, API_KEY


class VectorStoreService:
    SEPARATORS = ["\n\n", "\n", "。", "！", "？", " ", ""]

    def __init__(self, chunk_size=300, chunk_overlap=30):
        self.embeddings = DashScopeEmbeddings(model="text-embedding-v2", dashscope_api_key=API_KEY)
        self.vector_store = None
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.last_chunk_count = 0

    def _splitter(self):
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap, separators=self.SEPARATORS)

    def _persist(self, chunks):
        self.vector_store = Chroma.from_documents(
            chunks, self.embeddings, persist_directory=CHROMA_DIR, collection_name=COLLECTION)
        self.last_chunk_count = len(chunks)
        return len(chunks)

    def build_from_file(self, file_path):
        docs = TextLoader(file_path, encoding="utf-8").load()
        n = self._persist(self._splitter().split_documents(docs))
        print(f"向量库构建完成，共{n}个块")
        return self.vector_store

    def add_text(self, text, source="user_upload"):
        chunks = self._splitter().split_documents([Document(page_content=text, metadata={"source": source})])
        if self.vector_store is None:
            self._persist(chunks)
        else:
            self.vector_store.add_documents(chunks)
            self.last_chunk_count += len(chunks)
        return len(chunks)

    def load(self):
        if not os.path.exists(CHROMA_DIR):
            return None
        self.vector_store = Chroma(persist_directory=CHROMA_DIR,
                                   embedding_function=self.embeddings, collection_name=COLLECTION)
        try:
            self.last_chunk_count = self.vector_store._collection.count()
        except Exception:
            self.last_chunk_count = 0
        return self.vector_store

    def rebuild(self, file_path=DATA_FILE):
        if os.path.exists(CHROMA_DIR):
            shutil.rmtree(CHROMA_DIR)
        self.vector_store = None
        self.last_chunk_count = 0
        return self.build_from_file(file_path)

    def get_retriever(self, k=3):
        return self.vector_store.as_retriever(search_kwargs={"k": k}) if self.vector_store else None

    def status(self):
        return {
            "persist_dir": CHROMA_DIR, "collection": COLLECTION,
            "loaded": self.vector_store is not None, "chunk_count": self.last_chunk_count,
            "data_file_exists": os.path.exists(DATA_FILE),
            "data_file_size": os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0,
        }
