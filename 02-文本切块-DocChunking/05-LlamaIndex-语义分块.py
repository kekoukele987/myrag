import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# 加载 .env 中的环境变量
load_dotenv()

# 使用 FastEmbed 本地嵌入模型（无需联网 API，与 03 文件一致）
# BAAI/bge-small-zh-v1.5：轻量级中文嵌入模型，onnxruntime 推理，速度快
embed_model = FastEmbedEmbedding(
    model_name="BAAI/bge-small-zh-v1.5",
    max_length=512,
)

documents = SimpleDirectoryReader(
    input_files=["90-文档-Data/黑悟空/黑悟空wiki.txt"]
).load_data()

# 创建语义分块器
splitter = SemanticSplitterNodeParser(
    buffer_size=3,                        # 缓冲区大小
    breakpoint_percentile_threshold=90,   # 断点百分位阈值
    embed_model=embed_model               # FastEmbed 本地嵌入模型
)

# 创建基础句子分块器（作为对照）
base_splitter = SentenceSplitter(
    # chunk_size=512
)

'''
参数说明：
buffer_size：
默认值为1
这个参数控制评估语义相似度时，将多少个句子组合在一起当设置为1时，每个句子会被单独考虑
当设置大于1时，会将多个句子组合在一起进行评估例如，如果设置为3，就会将每3个句子作为一个组来评估语义相似度

breakpoint_percentile_threshold：
默认值为95
这个参数控制何时在句子组之间创建分割点,它表示余弦不相似度的百分位数阈值,当句子组之间的不相似度超过这个阈值时，就会创建一个新的节点
数值越小，生成的节点就越多（因为更容易达到分割阈值）
数值越大，生成的节点就越少（因为需要更大的不相似度才会分割）

这两个参数共同影响文本的分割效果：
buffer_size 决定了评估语义相似度的粒度
breakpoint_percentile_threshold 决定了分割的严格程度
例如：
如果 buffer_size=2 且 breakpoint_percentile_threshold=90：每2个句子会被组合在一起,当组合之间的不相似度超过90%时就会分割,这会产生相对较多的节点
如果 buffer_size=3 且 breakpoint_percentile_threshold=98：每3个句子会被组合在一起,需要更大的不相似度才会分割,这会产生相对较少的节点
'''

# 使用语义分块器对文档进行分块
semantic_nodes = splitter.get_nodes_from_documents(documents)
print("\n=== 语义分块结果 ===")
print(f"语义分块器生成的块数：{len(semantic_nodes)}")
for i, node in enumerate(semantic_nodes, 1):
    print(f"\n--- 第 {i} 个语义块 ---")
    print(f"内容:\n{node.text}")
    print("-" * 50)

# 使用基础句子分块器对文档进行分块
base_nodes = base_splitter.get_nodes_from_documents(documents)
print("\n=== 基础句子分块结果 ===")
print(f"基础句子分块器生成的块数：{len(base_nodes)}")
for i, node in enumerate(base_nodes, 1):
    print(f"\n--- 第 {i} 个句子块 ---")
    print(f"内容:\n{node.text}")
    print("-" * 50)


# =============================================================================
# 知识点总结
# =============================================================================
#
# 1. 语义分块 vs 普通分块
#    - 普通分块（SentenceSplitter/CharacterTextSplitter）：按固定规则（字符数、
#      分隔符）机械切分，不考虑文本语义。
#    - 语义分块（SemanticSplitterNodeParser）：利用嵌入模型计算相邻句子的语义
#      相似度，在"语义变化剧烈"的位置切分，保证每个块内部主题连贯。
#
# 2. 核心流程
#    (1) 嵌入模型将每个句子（或句子组）转为向量
#    (2) 计算相邻句子组之间的余弦相似度
#    (3) 当不相似度超过阈值（breakpoint_percentile_threshold 百分位）时，创建
#        分块边界
#    (4) 那些不相似度最高的 N% 位置成为分割点
#
# 3. 关键参数
#    · buffer_size（默认 1）：
#      - 将几个连续句子合并为一个"评估单元"
#      - buffer_size=1：每个句子独立的语义单元
#      - buffer_size=3：每 3 句一起计算，降低噪音，提高稳定性
#
#    · breakpoint_percentile_threshold（默认 95）：
#      - 不相似度的百分位阈值
#      - 值越小 → 更多位置被判定为分割点 → 块数更多、块更小
#      - 值越大 → 只有语义差异极大的位置才分割 → 块数更少、块更大
#
# 4. SemanticSplitterNodeParser 工作原理
#    - LlamaIndex 提供的语义分块节点解析器
#    - 需要传入 embed_model 来计算句子向量
#    - get_nodes_from_documents(documents) 返回 TextNode 列表
#
# 5. FastEmbedEmbedding — 本地嵌入模型
#    - 来自 llama_index.embeddings.fastembed，与同目录 03 文件一致
#    - model_name="BAAI/bge-small-zh-v1.5"：轻量级中文向量模型
#    - 底层使用 onnxruntime 推理，速度比 PyTorch 版本更快
#    - 模型文件从 HuggingFace/ModelScope 自动下载并缓存，无需 API Key
#    - 优势：完全本地运行、无网络依赖、零费用、中文效果好
#    - max_length=512：输入文本最大长度（超出部分截断）
#
# 6. python-dotenv 的使用
#    - from dotenv import load_dotenv
#    - load_dotenv() 自动读取项目根目录 .env 文件，注入到 os.environ
#    - 好处：API Key 不硬编码在代码中，避免泄露
#
# 7. SentenceSplitter（对照分块器）
#    - 基于句子边界（标点符号如 。！？\n）进行切分
#    - 支持 chunk_size 参数控制块大小
#    - 作为语义分块的对照实验，对比两种策略产生的块数和块质量
#
# 8. 应用场景
#    - 知识库/文档的 RAG 系统：语义分块能更好地保持段落主题完整性
#    - 长文档问答：用户问题能更精准地匹配到语义相关的块
#    - 对比实验：同一文档用不同分块策略，评估检索准确率差异
#    - 最适合"叙述性文本"（如 Wiki、小说、新闻），而非结构化代码
# =============================================================================