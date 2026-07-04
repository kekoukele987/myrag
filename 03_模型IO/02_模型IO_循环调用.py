from dotenv import load_dotenv
load_dotenv()

import os

from langchain_core.prompts import PromptTemplate

template = """您是一位专业的鲜花店文案撰写员。
对于售价为 {price} 元的 {flower_name} ，您能提供一个吸引人的简短描述吗？
"""

prompt = PromptTemplate.from_template(template)
print("=== PromptTemplate ===")
print(prompt)
print()

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

flowers = ["玫瑰", "百合", "康乃馨"]
prices = ["50", "30", "20"]

for flower, price in zip(flowers, prices):
    input_prompt = prompt.format(flower_name=flower, price=price)
    output = model.invoke(input_prompt)
    print(f"【{flower}】{price}元")
    print(output.content)
    print()


"""
本示例演示：模型 IO —— 循环调用，对多种花批量生成文案

与 01 的区别：
01_模型IO.py：单次调用，只生成一种花的描述
02_模型IO_循环调用.py：在 for 循环中多次调用，批量生成不同花的描述

核心概念不变：
PromptTemplate 定义模板 → format 填充变量 → model.invoke 调用大模型
"""