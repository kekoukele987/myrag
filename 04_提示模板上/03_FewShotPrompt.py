from dotenv import load_dotenv
load_dotenv()

import os

# 1. 创建一些示例
samples = [
    {
        "flower_type": "玫瑰",
        "occasion": "爱情",
        "ad_copy": "玫瑰，浪漫的象征，是你向心爱的人表达爱意的最佳选择。"
    },
    {
        "flower_type": "康乃馨",
        "occasion": "母亲节",
        "ad_copy": "康乃馨代表着母爱的纯洁与伟大，是母亲节赠送给母亲的完美礼物。"
    },
    {
        "flower_type": "百合",
        "occasion": "庆祝",
        "ad_copy": "百合象征着纯洁与高雅，是你庆祝特殊时刻的理想选择。"
    },
    {
        "flower_type": "向日葵",
        "occasion": "鼓励",
        "ad_copy": "向日葵象征着坚韧和乐观，是你鼓励亲朋好友的最好方式。"
    }
]

# 2. 创建一个提示模板
from langchain_core.prompts import PromptTemplate

prompt_sample = PromptTemplate(
    input_variables=["flower_type", "occasion", "ad_copy"],
    template="鲜花类型: {flower_type}\n场合: {occasion}\n文案: {ad_copy}"
)
print("=== 示例模板 ===")
print(prompt_sample.format(**samples[0]))
print()

# 3. 创建一个 FewShotPromptTemplate 对象
from langchain_core.prompts import FewShotPromptTemplate

prompt = FewShotPromptTemplate(
    examples=samples,
    example_prompt=prompt_sample,
    suffix="鲜花类型: {flower_type}\n场合: {occasion}",
    input_variables=["flower_type", "occasion"]
)
print("=== FewShotPrompt（直接使用示例）===")
print(prompt.format(flower_type="野玫瑰", occasion="爱情"))
print()

# 4. 把提示传递给大模型
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="deepseek-chat",
    max_tokens=200,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0.7,
)
result = model.invoke(prompt.format(flower_type="野玫瑰", occasion="爱情"))
print("=== 模型输出（FewShotPrompt）===")
print(result.content)
print()

# 5. 使用示例选择器（SemanticSimilarityExampleSelector）
# 使用 FastEmbed 替代 OpenAIEmbeddings，用 Chroma 替代 Qdrant
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

example_selector = SemanticSimilarityExampleSelector.from_examples(
    samples,
    embeddings,
    Chroma,
    k=1
)

prompt_with_selector = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=prompt_sample,
    suffix="鲜花类型: {flower_type}\n场合: {occasion}",
    input_variables=["flower_type", "occasion"]
)
print("=== FewShotPrompt（使用示例选择器）===")
query = prompt_with_selector.format(flower_type="红玫瑰", occasion="爱情")
print(query)
print()

result2 = model.invoke(query)
print("=== 模型输出（示例选择器）===")
print(result2.content)


"""
本示例演示 FewShotPromptTemplate —— 少样本提示模板

核心功能：
1. 定义示例数据（samples），包含 flower_type / occasion / ad_copy
2. 用 FewShotPromptTemplate 将示例拼接到 prompt 中
3. 两种方式提供示例：
   - 直接指定 examples= 列表
   - 使用 SemanticSimilarityExampleSelector 自动选择最相似的示例
4. 将完整 prompt 传给大模型生成文案

与旧版区别：
langchain.prompts.few_shot → langchain_core.prompts
langchain.llms.OpenAI → langchain_openai.ChatOpenAI
langchain.vectorstores.Qdrant → langchain_community.vectorstores.Chroma
langchain.embeddings.OpenAIEmbeddings → FastEmbedEmbeddings
langchain.prompts.example_selector → langchain_core.example_selectors
"""