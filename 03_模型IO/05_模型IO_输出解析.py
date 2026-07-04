from dotenv import load_dotenv
load_dotenv()

import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="deepseek-chat",
    max_tokens=500,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0.7,
)

output_parser = JsonOutputParser()

prompt_template = """您是一位专业的鲜花店文案撰写员。
对于售价为 {price} 元的 {flower_name} ，您能提供一个吸引人的简短描述吗？

请按以下 JSON 格式返回：
{{
    "description": "鲜花的描述文案",
    "reason": "为什么要这样写这个文案"
}}
"""

prompt = PromptTemplate.from_template(prompt_template)

flowers = ["玫瑰", "百合", "康乃馨"]
prices = ["50", "30", "20"]

import pandas as pd
df = pd.DataFrame(columns=["flower", "price", "description", "reason"])

for flower, price in zip(flowers, prices):
    inp = prompt.format(flower_name=flower, price=price)
    output = model.invoke(inp)
    parsed = output_parser.parse(output.content)
    df.loc[len(df)] = {
        "flower": flower,
        "price": price,
        "description": parsed["description"],
        "reason": parsed["reason"],
    }

print(df.to_dict(orient='records'))
df.to_csv("03_模型IO/flowers_with_descriptions.csv", index=False)


"""
本示例演示：模型 IO —— 结构化输出解析（JsonOutputParser）

核心功能：
在 prompt 中要求模型按指定 JSON 格式返回，
用 JsonOutputParser 解析输出 → 存入 DataFrame → 保存 CSV。

与前面示例的区别：
01_模型IO.py：单次调用，输出纯文本
02_模型IO_循环调用.py：循环调用，输出纯文本
03_OpenAI_IO.py：原生 SDK，输出纯文本
05_模型IO_输出解析.py：输出结构化数据（JSON），保存到 CSV
"""