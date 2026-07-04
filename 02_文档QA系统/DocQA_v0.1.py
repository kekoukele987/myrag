'''
DocQA v0.1 — 本地文档问答系统

流程：Load（加载文档）→ Split（切分）→ Store（向量存储）→ Retrieval（检索）→ Output（Web界面）
'''

import os
from dotenv import load_dotenv
load_dotenv()

import logging

# ==================== 1. Load 导入 Document Loaders ====================
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader

# 加载 Documents
base_dir = os.path.join(os.path.dirname(__file__), 'OneFlower')
documents = []
for file in os.listdir(base_dir):
    file_path = os.path.join(base_dir, file)
    try:
        if file.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        elif file.endswith('.txt'):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            continue
        documents.extend(loader.load())
        print(f"  ✓ {file}")
    except Exception as e:
        print(f"  ✗ {file}: {e}")

print(f"共加载 {len(documents)} 个文档片段")

# ==================== 2. Split 切分文档 ====================
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=10)
chunked_documents = text_splitter.split_documents(documents)
print(f"切分为 {len(chunked_documents)} 个块")

# ==================== 3. Store 向量存储（FastEmbed 内置模型，无需联网下载）====================
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

embedding_model = FastEmbedEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

vectorstore = Chroma.from_documents(
    documents=chunked_documents,
    embedding=embedding_model,
    persist_directory=os.path.join(os.path.dirname(__file__), 'chroma_db')
)
print(f"向量库构建完成，共 {vectorstore._collection.count()} 条向量")

# ==================== 4. Retrieval 检索链（LCEL 方式）====================
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 读取 DeepSeek API 密钥
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

# 实例化 DeepSeek 大模型
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
)

# 使用普通检索器（search_kwargs={"k": 4} 表示检索 4 个最相关文档块）
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

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

# 用 LCEL 构建 RAG 链
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

print("QA 系统已就绪，启动 Web 界面...")

# ==================== 5. Output Web 界面 ====================
from flask import Flask, request, render_template

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@app.route('/', methods=['GET', 'POST'])
def home():
    answer = None
    if request.method == 'POST':
        question = request.form.get('question')
        if question:
            answer = qa_chain.invoke(question)
    return render_template('index.html', answer=answer)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5000)


"""
本示例讲解：完整 RAG 文档问答系统

一、5 个核心阶段
1. Load — 从 OneFlower/ 目录自动加载 PDF / DOCX / TXT 三种格式文档
2. Split — 将长文档切分为 200 字符的小块（chunk_size=200）
3. Store — 用 FastEmbed（BGE模型）做向量化 → 存入 Chroma 向量数据库
4. Retrieval — 从向量库检索最相关的 4 个文档块作为上下文
5. Output — Flask Web 界面，用户输入问题，返回 AI 答案

二、用到的核心技术
- 文档加载：PyPDFLoader / Docx2txtLoader / TextLoader
- 文本切分：RecursiveCharacterTextSplitter
- 向量化：FastEmbed（BAAI/bge-small-zh-v1.5 内置模型，无需联网下载）
- 向量检索：Chroma（本地文件存储）
- 大模型：DeepSeek Chat（deepseek-chat），从 .env 读取密钥
- 问答链：LCEL（LangChain Expression Language）构建

三、与前面示例的区别
01-04 都是单步骤演示（纯文本生成 / Chat 调用）
本示例是完整的 RAG 流水线，包含文档加载→向量化→检索→生成的全流程 + Web 界面
"""
