from dotenv import load_dotenv
load_dotenv()

import os

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# 模板的构建
template = "你是一位专业顾问，负责为专注于{product}的公司起名。"
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "公司主打产品是{product_detail}。"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt_template = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

# 格式化提示消息生成提示
prompt = chat_prompt_template.format_prompt(
    product="鲜花装饰",
    product_detail="创新的鲜花设计。"
).to_messages()

# 调用模型
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

from langchain_openai import ChatOpenAI

chat = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0.7,
)

result = chat.invoke(prompt)
print(result.content)


"""
本示例演示 ChatPromptTemplate 的使用 —— 用 SystemMessage 和 HumanMessage 构建对话模板。

核心步骤：
1. 创建 SystemMessagePromptTemplate + HumanMessagePromptTemplate
2. ChatPromptTemplate.from_messages 组合成聊天模板
3. format_prompt 填充变量 → to_messages 转为消息列表
4. chat.invoke 调用模型

与旧版区别：
langchain.prompts → langchain_core.prompts
langchain.chat_models.ChatOpenAI → langchain_openai.ChatOpenAI
chat(prompt) → chat.invoke(prompt)
"""