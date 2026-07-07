from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
loader = TextLoader("90-文档-Data/山西文旅/云冈石窟.txt", encoding='utf-8')
documents = loader.load()
# 定义分割符列表，按优先级依次使用
separators = ["\n\n", ".", "，", " "] # . 是句号，， 是逗号， 是空格
# 创建递归分块器，并传入分割符列表
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
    separators=separators
)
chunks = text_splitter.split_documents(documents)
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
# 功能：演示 RecursiveCharacterTextSplitter 递归字符文本分割器的基本用法
#
# 涉及知识点
# ----------------------------------------------------------------------------
#   1. 文档加载：TextLoader — 从本地文本文件加载文档（需指定 encoding='utf-8' 避免 gbk 解码报错）
#   2. 文本分块：RecursiveCharacterTextSplitter — 递归字符文本分割器
#   3. chunk_size：每个文本块的最大字符数（此处 100）
#   4. chunk_overlap：相邻文本块之间的重叠字符数（此处 10）
#   5. separators：自定义分割符优先级列表，按顺序依次尝试分割
#   6. split_documents()：对 Document 对象列表执行分块
#   7. Document 结构：page_content（文本内容）+ metadata（元数据）
#
# == 与 CharacterTextSplitter（01-示例）的对比 ============================
#
#   CharacterTextSplitter                    | RecursiveCharacterTextSplitter
#   -----------------------------------------|--------------------------------
#   1. 只按一个固定的 separator 切分         | 1. 按 separators 列表中的多个分隔符
#                                            |    按优先级依次尝试切分
#   2. 遇到超长块不会进一步拆分               | 2. 递归尝试下一个分隔符继续拆分，
#                                            |    直到块大小 <= chunk_size
#   3. 适合结构简单、分隔符单一的文本         | 3. 适合层级结构复杂的文本
#                                            |    （如代码、文章等混合内容）
#   4. 默认 separator = "\n\n"               | 4. 默认 separators = ["\n\n", "\n",
#                                            |    " ", ""] 逐级递减
# ============================================================================
