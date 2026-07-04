from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

prompt_text = "您是一位专业的鲜花店文案撰写员。对于售价为{}元的{}，您能提供一个吸引人的简短描述吗？"

flowers = ["玫瑰", "百合", "康乃馨"]
prices = ["50", "30", "20"]

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

for flower, price in zip(flowers, prices):
    prompt = prompt_text.format(price, flower)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    print(response.choices[0].message.content)
    print()


"""
本示例演示：使用原生 openai SDK 循环调用 DeepSeek Chat API

与 02 的区别：
02_模型IO_循环调用.py：用 langchain 的 ChatOpenAI 封装，通过 PromptTemplate + model.invoke 调用
03_OpenAI_IO.py：用原生 openai SDK，手动构造 messages 列表，通过 client.chat.completions.create 调用

与 01 的区别：
01_模型IO.py：用 langchain + PromptTemplate + 单次调用
02_模型IO_循环调用.py：用 langchain + PromptTemplate + 循环调用
03_OpenAI_IO.py：用原生 SDK（不用 langchain）+ 循环调用
"""