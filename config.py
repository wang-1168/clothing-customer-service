"""服装电商智能客服 RAG 系统 - 配置模块"""
import os
from urllib.parse import quote

# 路径与集合配置
CHROMA_DIR = "./chroma_db"
COLLECTION = "clothing_knowledge"
DATA_FILE = "data/clothing_knowledge.txt"

# API Key
API_KEY = os.getenv("OPEN_AI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

# 胡桃主题背景图（text_to_image 生成，带浅色遮罩保证内容可读）
_BG_PROMPT = ("Hu Tao from Genshin Impact, twin braids with red ribbons, plum blossom pupils, "
              "red and black funeral parlor outfit, fire elemental magic, cute ghost companion, "
              "dark elegant atmospheric background, anime key visual, high quality")
BG_URL = (f"https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"
          f"?prompt={quote(_BG_PROMPT)}&image_size=landscape_16_9")

# 提示词模板
PROMPT_TEMPLATE = """你是一个专业的服装电商客服。根据参考资料回答顾客问题。
要求：
1. 只根据参考资料回答，不要编造
2. 回答亲切友好，像真人客服
3. 涉及尺码时给出具体建议
4. 如果资料中没有，礼貌告知并建议联系人工客服

参考资料：
{context}

顾客问题：{question}

客服回答："""
