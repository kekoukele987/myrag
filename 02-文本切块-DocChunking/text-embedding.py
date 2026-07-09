from fastembed import TextEmbedding
import numpy as np


import os
from dotenv import load_dotenv
from openai import OpenAI



# 1. 加载本地BGE中文向量模型（和你代码一致，离线无需API）
embedding_model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# 2. 准备测试文本
sentence_a = "黑神话悟空是一款国产开放世界单机游戏"
sentence_b = "黑悟空是由游戏科学开发的3A大作"
sentence_c = "今天中午吃番茄牛肉面"

# 3. 生成向量（embedding）
vec_a = list(embedding_model.embed([sentence_a]))[0]
vec_b = list(embedding_model.embed([sentence_b]))[0]
vec_c = list(embedding_model.embed([sentence_c]))[0]

# 4. 余弦相似度计算函数（衡量语义相近程度）
def cos_sim(v1: np.ndarray, v2: np.ndarray) -> float:
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    return dot / (norm1 * norm2)

# 5. 输出结果
sim_ab = cos_sim(vec_a, vec_b)
sim_ac = cos_sim(vec_a, vec_c)
print(f"句子A与句子B相似度：{sim_ab:.4f}")
print(f"句子A与句子C相似度：{sim_ac:.4f}")


# =============================================================================
# 下面演示：如果使用远程 API 做向量化（如 DeepSeek / OpenAI）
# =============================================================================
#
# 注意：DeepSeek 目前只提供 Chat Completions（对话）API，
#       不提供 /v1/embeddings（向量化）端点。
#       以下代码会报错：openai.NotFoundError: 404
#
# 解决方案（三选一）：
#   方案A：继续用上面的本地 FastEmbed（推荐，零费用、离线可用）
#   方案B：换用 OpenAI 的 text-embedding-3-small（需 OpenAI API Key）
#   方案C：换用其他国产模型厂的 embeddings API
#          如智谱 GLM、百度千帆、阿里通义等
#
# 以下是方案B（OpenAI）的示例代码（需 pip install openai + API Key）：
# =============================================================================

load_dotenv()

# ---- 方案B：OpenAI Embedding（取消下面注释即可使用）----
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),          # 需要 .env 中设 OPENAI_API_KEY
#     base_url="https://api.openai.com/v1"
# )
#
# def get_openai_embedding(text: str):
#     resp = client.embeddings.create(input=text, model="text-embedding-3-small")
#     return np.array(resp.data[0].embedding)
#
# vec1 = get_openai_embedding("黑神话悟空是国产游戏")
# vec2 = get_openai_embedding("游戏科学出品黑悟空")
# print(f"OpenAI Embedding 相似度：{cos_sim(vec1, vec2):.4f}")



client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

def get_zhipu_embedding(text: str):
    resp = client.embeddings.create(
        input=text,
        model="embedding-3"  # 智谱官方向量模型
    )
    return np.array(resp.data[0].embedding)

vec1 = get_zhipu_embedding(sentence_a)
vec2 = get_zhipu_embedding(sentence_b)
vec3 = get_zhipu_embedding(sentence_c)
print(f"智谱 Embedding 相似度：{cos_sim(vec1, vec2):.4f}"   )
print(f"智谱 Embedding 相似度：{cos_sim(vec1, vec3):.4f}"   )



"""
句子A与句子B相似度：0.7699
句子A与句子C相似度：0.2689
智谱 Embedding 相似度：0.7144
智谱 Embedding 相似度：0.2860
"""