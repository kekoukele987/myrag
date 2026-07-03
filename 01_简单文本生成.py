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