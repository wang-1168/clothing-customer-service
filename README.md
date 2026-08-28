# 服装电商智能客服 RAG 系统

> 基于 RAG（检索增强生成）的服装电商智能客服，Streamlit 毛玻璃界面 + 通义千问大模型问答。  
> 从知识库检索相关片段，交由大模型生成自然流畅的客服回答，并标注引用来源。

---

## 功能特性

- **智能问答**：基于知识库的 RAG 检索 + 大模型生成，回答准确可溯源
- **流式输出**：回答逐字呈现，体验流畅
- **引用来源**：每条回答可展开查看命中的知识片段与来源
- **多会话管理**：独立对话新建 / 切换 / 删除，自动以首问命名
- **知识库管理**：状态卡片、重建索引、上传补充知识、检索测试
- **胡桃主题毛玻璃 UI**：渐变标题、消息进入动画、按钮 / 卡片 hover 微交互、在线状态脉冲

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Streamlit |
| 向量化 | DashScope Embeddings |
| 向量库 | Chroma |
| 大模型 | ChatTongyi / 通义千问 |
| 框架 | LangChain |

## 项目结构

```
服装智能客服/
├── app.py                       # 入口文件
├── chat_app.py                  # 前端应用（Streamlit 界面与交互）
├── config.py                   # 配置常量（路径、API Key、提示词模板）
├── vector_store.py              # 向量库服务（切分、向量化、检索）
├── rag_service.py               # RAG 服务（检索 + 大模型生成）
├── data/
│   └── clothing_knowledge.txt   # 知识库源文件（尺码/退换货/物流/洗护）
├── requirements.txt             # 依赖清单
├── .gitignore
└── README.md
```

## 快速开始

```bash
# 1. 克隆
git clone https://github.com/wang-1168/clothing-customer-service.git
cd clothing-customer-service

# 2. 创建虚拟环境并安装依赖
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# 3. 配置 DashScope API Key
# Windows
set OPEN_AI_API_KEY=你的DashScope-Key
# macOS / Linux
export OPEN_AI_API_KEY=你的DashScope-Key

# 4. 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，首次启动会自动从 `data/clothing_knowledge.txt` 构建向量库。

## 使用说明

- 在输入框输入问题，或点击下方快捷问题一键提问
- 回答下方可展开「📖 参考来源」查看命中的知识片段
- 侧边栏切换页面：智能客服 / 知识库 / 设置 / 关于
- 知识库页可查看状态、重建索引、上传补充知识、检索测试

## 知识库内容

`data/clothing_knowledge.txt` 包含尺码建议、退换货政策、物流配送、面料洗护等服装电商常见问答。

## License

MIT
