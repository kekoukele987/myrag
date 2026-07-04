import os
from dotenv import load_dotenv

# 从 .env 文件加载 API 密钥
load_dotenv()

# HuggingFace国内镜像
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 关闭软链接警告
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ====================== 1. 本地加载 BAAI/bge-small-zh-v1.5 向量化模型 ======================
# 使用本地已缓存的模型（避免联网下载超时）
embedding_model = HuggingFaceEmbeddings(
    model_name="C:\\Users\\22948\\.cache\\huggingface\\hub\\models--BAAI--bge-small-zh\\snapshots\\1d2363c5de6ce9ba9c890c8e23a4c72dce540ca8",
    model_kwargs={"device": "cpu"},  # 有GPU改为 cuda
    encode_kwargs={"normalize_embeddings": True}  # BGE必须开启归一化
)

# ====================== 2. 构建本地向量库（示例知识库） ======================
# 你的私有文档文本，全程本地处理不上传云端
raw_docs = [
    "DeepSeek API 接口地址为 https://api.deepseek.com/v1，兼容OpenAI接口格式",
    "BGE系列模型是专门做中文语义向量的轻量模型，适合本地私有知识库检索",
    "RAG架构中，向量模型负责找资料，大模型负责结合资料生成答案",
    "bge-small-zh-v1.5参数量很小，普通电脑CPU就能流畅运行"
]

# 文本切片
text_splitter = RecursiveCharacterTextSplitter(chunk_size=128, chunk_overlap=20)
split_texts = text_splitter.create_documents(raw_docs)

# 存入本地Chroma向量数据库（文件存在本地，不上网）
vector_db = Chroma.from_documents(
    documents=split_texts,
    embedding=embedding_model,
    persist_directory="./chroma_db"  # 向量持久化本地文件夹
)

# 构建检索器：查询时用BGE本地向量化，本地相似度匹配
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# ====================== 3. 对接云端 DeepSeek LLM API ======================
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
    temperature=0.1
)

# ====================== 4. 串联RAG链路：本地检索 → 联网生成回答 ======================
# 提示词模板
prompt_template = PromptTemplate.from_template(
    """根据以下上下文内容回答问题。

上下文：
{context}

问题：{question}

回答："""
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 使用 LCEL (LangChain Expression Language) 构建 RAG 链
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

# ====================== 5. 执行问答 ======================
if __name__ == "__main__":
    query = "bge模型和deepseek api分别承担什么作用？"
    result = qa_chain.invoke(query)
    
    # 获取检索到的源文档
    source_docs = retriever.invoke(query)

    print("===== AI回答 =====")
    print(result)
    print("\n===== 本地检索到的原文（由BGE匹配） =====")
    for idx, doc in enumerate(source_docs):
        print(f"{idx+1}. {doc.page_content}")



"""
===== AI回答 =====
根据上下文内容，BGE模型负责**找资料**（即向量模型的作用），DeepSeek API负责**结合资料生成答案**（即大模型的作用）。

===== 本地检索到的原文（由BGE匹配） =====
1. RAG架构中，向量模型负责找资料，大模型负责结合资料生成答案
2. RAG架构中，向量模型负责找资料，大模型负责结合资料生成答案
3. BGE系列模型是专门做中文语义向量的轻量模型，适合本地私有知识库检索
"""