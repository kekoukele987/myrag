from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_document(file_path: str, encoding: str = "utf-8") -> list:
    """加载本地文本文件，返回 Document 对象列表"""
    loader = TextLoader(file_path, encoding=encoding)
    return loader.load()


def create_recursive_splitter(
    chunk_size: int = 100,
    chunk_overlap: int = 10,
    separators: list = None,
) -> RecursiveCharacterTextSplitter:
    """创建递归字符文本分割器"""
    if separators is None:
        # 默认分隔符优先级：段落 > 句号 > 逗号 > 空格 > 字符
        separators = ["\n\n", ".", "，", " "]
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )


def split_documents(
    text_splitter: RecursiveCharacterTextSplitter, documents: list
) -> list:
    """执行文档分块"""
    return text_splitter.split_documents(documents)


def print_chunks(chunks: list) -> None:
    """打印分块结果"""
    print("\n=== 文档分块结果 ===")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- 第 {i} 个文档块 ---")
        print(f"内容: {chunk.page_content}")
        print(f"元数据: {chunk.metadata}")
        print("-" * 50)


def main():
    # 1. 加载文档
    file_path = "90-文档-Data/山西文旅/云冈石窟.txt"
    documents = load_document(file_path)

    # 2. 定义分隔符列表（按优先级从高到低）
    separators = ["\n\n", ".", "，", " "]

    # 3. 创建递归分块器
    text_splitter = create_recursive_splitter(
        chunk_size=100, chunk_overlap=10, separators=separators
    )

    # 4. 执行分块
    chunks = split_documents(text_splitter, documents)

    # 5. 输出结果
    print_chunks(chunks)


if __name__ == "__main__":
    main()


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
#   5. separators：自定义分隔符优先级列表，按顺序依次尝试分割
#   6. split_documents()：对 Document 对象列表执行分块
#   7. Document 结构：page_content（文本内容）+ metadata（元数据）
#   8. main() 入口 + if __name__ == "__main__" 保护，模块可被导入而不自动执行
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