from dotenv import load_dotenv  # 用于加载环境变量
load_dotenv()  # 加载 .env 文件中的环境变量

import os
from langchain_openai import ChatOpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

# 使用 DeepSeek Chat API（兼容 OpenAI 格式）
llm = ChatOpenAI(
    model="deepseek-chat",        # DeepSeek 对话模型
    max_tokens=200,
    temperature=0.7,
    base_url="https://api.deepseek.com/v1",  # DeepSeek API 端点
    api_key=api_key,
)

text = llm.invoke("请给我写一句情人节红玫瑰的中文宣传语")
print(text.content)


"""
依然属于大模型应用，只是最简基础调用版本，去掉了 RAG、向量库、本地 BGE 等检索增强逻辑，只保留最核心的「调用云端大模型生成文本」能力。

三、这段代码的优缺点
优点
结构极简，上手门槛低，只需要 API 密钥就能跑通；
不需要本地下载 BGE 向量模型、不用维护向量库，无本地模型下载卡顿问题；
适合通用闲聊、文案生成、简单问答等不需要私有知识库的场景。
缺点（对比 RAG 版本）
模型只能使用训练截止前的公共知识，无法读取你本地自定义文档；
会产生幻觉，不能基于你的业务资料精准回答；
大量私有背景信息只能全部塞进 prompt，token 消耗高、上下文容易超限。
"""