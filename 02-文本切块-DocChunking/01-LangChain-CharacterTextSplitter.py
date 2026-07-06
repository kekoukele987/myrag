from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# 加载文档
loader = TextLoader("90-文档-Data/山西文旅/云冈石窟.txt", encoding="utf-8")
documents = loader.load()

# 设置分块器：chunk_size=100 字符，chunk_overlap=10 字符重叠
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=100,
    chunk_overlap=10,
)

# 执行分块
chunks = text_splitter.split_documents(documents)

# 输出分块结果
print("\n=== 文档分块结果 ===")
for i, chunk in enumerate(chunks, 1):
    print(f"\n--- 第 {i} 个文档块 ---")
    print(f"内容: {chunk.page_content}")
    print(f"元数据: {chunk.metadata}")
    print("-" * 50)


# ============================================================================
# 文件说明
# ============================================================================
#
# 功能：演示 CharacterTextSplitter 按字符数切分文档的基本用法
#
# 涉及知识点
# ----------------------------------------------------------------------------
#   1. 文档加载：TextLoader — 从本地文本文件加载文档
#   2. 文本分块：CharacterTextSplitter — 按字符数切分文本
#   3. chunk_size：每个文本块的最大字符数（此处 100）
#   4. chunk_overlap：相邻文本块之间的重叠字符数（此处 10）
#   5. split_documents()：对 Document 对象列表执行分块
#   6. Document 结构：page_content（文本内容）+ metadata（元数据）
# ============================================================================