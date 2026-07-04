from dotenv import load_dotenv
load_dotenv()

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

chat = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.8,
    max_tokens=60,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
)

messages = [
    SystemMessage(content="你是一个很棒的智能助手"),
    HumanMessage(content="请给我的花店起个名")
]

response = chat.invoke(messages)
print(response.content)


"""
本示例使用的大模型：DeepSeek Chat（deepseek-chat）

一、与大模型交互方式
通过 langchain 的 ChatOpenAI 封装，使用 SystemMessage + HumanMessage 构造对话消息，再调用 invoke 获取回复。

二、核心参数说明
- model: "deepseek-chat" — DeepSeek 对话模型
- temperature: 0.8 — 控制随机性
- max_tokens: 60 — 最大输出长度
- messages 使用 langchain 的 Message 对象构造（SystemMessage / HumanMessage）

三、与前面示例的区别
01_简单文本生成.py — langchain ChatOpenAI，单条 prompt 字符串直接 invoke
02_ChatModel.py — 原生 openai SDK，手动构造 dict 格式 messages 列表
03_TextLangChain_v0.2.py — 使用 OpenAI 的 Text 模型（/completions 端点），纯文本补全
本示例 04 — langchain ChatOpenAI，使用 Message 对象（SystemMessage + HumanMessage）结构化构造对话

核心差异：
- 03 使用 Text 模型（补全式），04 使用 Chat 模型（对话式）
- 02 用原生 SDK，01/04 用 langchain 封装
- 01 单条 prompt，04 支持 system/user 多角色消息


消息类型	     作用	                               对应 OpenAI role
SystemMessage	全局人设、规则、约束（永久生效）	     system
HumanMessage	用户提问、人类输入	                    user
AIMessage	    AI 历史回复，用于多轮对话记忆	         assistant


"""