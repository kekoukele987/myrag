from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a creative AI."},
        {"role": "user", "content": "请给我的花店起个名"},
    ],
    temperature=0.8,
    max_tokens=60
)

print(response.choices[0].message.content)


"""
本示例使用的大模型：DeepSeek Chat（deepseek-chat）

一、与大模型交互方式
调用 DeepSeek Chat API（兼容 OpenAI 格式），通过 openai 库的 chat.completions.create 接口完成对话。
相比 01_简单文本生成.py 用 langchain 的 ChatOpenAI 封装，本示例使用更底层的 openai SDK 直接调用，更贴近原生 API 用法。

二、核心参数说明
- model: "deepseek-chat" — DeepSeek 对话模型，上下文 64K tokens
- temperature: 0.8 — 控制生成随机性，值越大越有创意（0.0-2.0）
- max_tokens: 60 — 限制回复最大 token 数，控制输出长度
- messages — 对话消息列表，支持 system（系统设定）和 user（用户输入）两种角色

三、本示例与 01 示例的区别
01_简单文本生成.py：使用 langchain 的 ChatOpenAI 高层封装，invoke 即可调用
02_ChatModel.py：使用原生 openai SDK，手动构造 messages 列表，更灵活但代码稍多

两者底层都走 DeepSeek /v1/chat/completions 接口，效果一致。
"""
