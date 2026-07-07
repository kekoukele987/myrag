"""

功能：演示 LlamaIndex 中分块大小对 RAG 问答准确性的影响

与 01-LangChain-CharacterTextSplitter 和 02-LangChain-RecursiveharacterTextSplitter 不同，
本文件使用 LlamaIndex 框架，以 PDF 为数据源构建向量索引并提问，通过调整 chunk_size
观察不同分块粒度对检索结果的影响。

对比：
  - 01/02 仅展示分块本身（打印文本块）
  - 本文件展示分块 → 向量化 → 检索 → 回答的完整 RAG 链路
"""

import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PDFReader
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.fastembed import FastEmbedEmbedding


# ============================================================================
# 步骤一：加载环境变量
# ============================================================================
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")


# ============================================================================
# 步骤二：配置全局模型（LLM + Embedding）
# ============================================================================

# --- LLM：使用 DeepSeek（需要 API Key）---
llm = DeepSeek(
    model="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    temperature=0.0,
)

# --- Embedding：使用 FastEmbed（本地运行，无需联网下载模型文件）---
# BAAI/bge-small-zh-v1.5 是一个轻量级中文嵌入模型
# FastEmbed 内部从 HuggingFace 镜像或 ModelScope 缓存获取模型，
# 相比直接使用 HuggingFaceEmbedding 更易通过国内网络访问
embed_model = FastEmbedEmbedding(
    model_name="BAAI/bge-small-zh-v1.5",
    max_length=512,
)

# 将 LLM 和 Embedding 注入全局配置
Settings.llm = llm
Settings.embed_model = embed_model


# ============================================================================
# 步骤三：测试不同 chunk_size 的对比函数
# ============================================================================

def build_index_and_query(
    file_path: str,
    chunk_size: int,
    chunk_overlap: int = 20,
    query: str = "how much is the Loss from operations for 2022?",
    similarity_top_k: int = 3,
) -> dict:
    """使用指定 chunk_size 构建索引 → 检索 → 回答

    Args:
        file_path:      PDF 文件路径
        chunk_size:     文本块大小（字符数）
        chunk_overlap:  块间重叠字符数
        query:          用户提问
        similarity_top_k: 检索时返回的最相似块数

    Returns:
        dict: { "response": 回答文本, "chunks": [原始块内容列表] }
    """
    # 1. 设置当前分块器
    Settings.node_parser = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # 2. 加载 PDF
    loader = PDFReader()
    documents = loader.load_data(file=file_path)

    # 3. 构建向量索引（此过程会自动对文档分块 + 向量化）
    #    注意：此时 Settings.node_parser 已指定分块器
    index = VectorStoreIndex.from_documents(documents)

    # 4. 创建查询引擎
    query_engine = index.as_query_engine(
        similarity_top_k=similarity_top_k,
        verbose=False,
    )

    # 5. 执行查询
    response = query_engine.query(query)

    # 6. 收集检索到的原始文本块
    chunks = []
    for source_node in response.source_nodes:
        chunks.append(source_node.text)

    return {"response": str(response), "chunks": chunks}


def run_comparison():
    """运行多个 chunk_size 并对比结果"""
    file_path = "90-文档-Data/复杂PDF/uber_10q_march_2022_page26.pdf"
    query = "how much is the Loss from operations for 2022?"
    chunk_sizes = [50, 100, 250]

    for cs in chunk_sizes:
        print("\n" + "=" * 70)
        print(f"  chunk_size = {cs}")
        print("=" * 70)

        result = build_index_and_query(
            file_path=file_path,
            chunk_size=cs,
            chunk_overlap=20,
            query=query,
            similarity_top_k=3,
        )

        print(f"\n>> 回答: {result['response']}")

        print(f"\n>> 检索到的文本块（共 {len(result['chunks'])} 块）:")
        for i, chunk_text in enumerate(result["chunks"]):
            print(f"\n  --- 第 {i + 1} 块 (长度 {len(chunk_text)} 字符) ---")
            print(f"  {chunk_text[:200]}{'...' if len(chunk_text) > 200 else ''}")

    print("\n" + "=" * 70)
    print("  总结：chunk_size 越大，语义越完整但可能引入噪声")
    print("        chunk_size 越小，粒度越细但可能截断关键上下文")
    print("        chunk_overlap 可缓解边界截断问题")
    print("=" * 70)


# ============================================================================
# 步骤四：单次运行入口（默认 chunk_size=250）
# ============================================================================

def run_single():
    """单次执行，便于快速测试"""
    file_path = "90-文档-Data/复杂PDF/uber_10q_march_2022_page26.pdf"
    query = "how much is the Loss from operations for 2022?"

    Settings.node_parser = SentenceSplitter(chunk_size=250, chunk_overlap=20)

    loader = PDFReader()
    documents = loader.load_data(file=file_path)

    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine(
        similarity_top_k=3,
        verbose=False,
    )

    response = query_engine.query(query)

    print("\n************ LlamaIndex Query Response ************")
    print(response)

    print("\n************ Retrieved Text Chunks ************")
    for i, source_node in enumerate(response.source_nodes):
        print(f"\nChunk {i + 1}:")
        print("Text content:")
        print(source_node.text)
        print("-" * 50)


if __name__ == "__main__":
    # 两种模式任选其一：
    # run_single()       — 单次执行（快速）
    run_comparison()  # 对比多种 chunk_size（推荐）


# ============================================================================
# 文件说明
# ============================================================================
#
# 功能：演示 LlamaIndex 框架下 chunk_size 对 RAG 问答准确性的影响
#
# 涉及知识点
# ----------------------------------------------------------------------------
#   1. 文档加载：PDFReader — LlamaIndex 内置的 PDF 读取器
#   2. 文本分块：SentenceSplitter — LlamaIndex 的句子级分割器
#       - chunk_size：      每个文本块的目标字符数
#       - chunk_overlap：   相邻块之间的重叠字符数，缓解边界信息丢失
#   3. 全局配置：Settings — LlamaIndex 的全局配置单例
#       - Settings.llm：        设置全局 LLM
#       - Settings.embed_model：设置全局 Embedding 模型
#       - Settings.node_parser：设置全局分块器
#   4. 向量索引：VectorStoreIndex — 将文档分块 + 向量化后构建索引
#   5. 查询引擎：as_query_engine() — 从索引创建查询引擎
#       - similarity_top_k：检索返回的最相似文本块数
#   6. LLM 接入：DeepSeek (llama-index-llms-deepseek)
#       - 通过 API Key 调用 deepseek-chat 模型
#   7. Embedding 模型：FastEmbedEmbedding (llama-index-embeddings-fastembed)
#       - BAAI/bge-small-zh-v1.5：轻量中文嵌入模型，本地运行
#       - FastEmbed 底层使用 onnxruntime 推理，速度比 PyTorch 版本更快
#       - 模型文件从国内可访问的 CDN 下载，下载后自动缓存
#   8. RAG 完整链路：PDF → 分块 → 向量化 → 索引 → 检索 → LLM 回答
#
# == 与 LangChain 分块方式的对比 ==========================================
#
#   LangChain (01/02 示例)                  | LlamaIndex (本文件)
#   ----------------------------------------|-------------------------------
#   1. TextLoader + TextSplitter            | 1. PDFReader + SentenceSplitter
#   2. 只执行分块，不涉及向量化/检索         | 2. 分块后自动向量化并构建索引
#   3. 输出原始文本块供下游使用              | 3. 基于检索结果用 LLM 生成答案
#   4. 需自行串联后续步骤                    | 4. 端到端 RAG 链路
#   5. CharacterTextSplitter 按字符数切分    | 5. SentenceSplitter 按句子边界切分
#   6. RecursiveCharacterTextSplitter        |    对中文也友好
#      按分隔符优先级递归切分                |
# ============================================================================