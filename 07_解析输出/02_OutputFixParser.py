from dotenv import load_dotenv
load_dotenv()

import os

from pydantic import BaseModel, Field
from typing import List

# 使用 Pydantic 创建一个数据格式，表示花
class Flower(BaseModel):
    name: str = Field(description="name of a flower")
    colors: List[str] = Field(description="the colors of this flower")


# 定义一个格式不正确的输出（注意：Python dict 格式而非 JSON）
misformatted = "{'name': '康乃馨', 'colors': ['粉红色','白色','红色','紫色','黄色']}"

# 创建 Pydantic 输出解析器，目标解析为 Flower 格式
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=Flower)

# 直接解析会出错（单引号不符合 JSON 规范）：
# parser.parse(misformatted)  # JSONDecodeError

# 使用 OutputFixingParser 自动修正格式错误的输出
from langchain_classic.output_parsers import OutputFixingParser

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    max_tokens=200,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0,
)

# 创建 OutputFixingParser：用 LLM 自动纠正格式错误的输出
new_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)

# 解析格式不正确的输出（自动修正）
result = new_parser.parse(misformatted)
print("=== 修正后的输出 ===")
print(result)
# 输出: name='康乃馨' colors=['粉红色', '白色', '红色', '紫色', '黄色']


"""
本示例演示：OutputFixingParser —— 自动修正格式错误的 LLM 输出

一、核心知识点
    LLM 输出的 JSON 格式偶尔会出错（例如用单引号代替双引号、缺少逗号、字段名拼写错误等），
    直接使用 PydanticOutputParser.parse() 会抛出 JSONDecodeError。
    
    OutputFixingParser 的工作原理：
    1. 先用 PydanticOutputParser 尝试解析
    2. 如果解析失败，将错误信息 + 错误输出一起发给 LLM，请其修正
    3. LLM 返回修正后的 JSON，再重新解析
    
    本质：用 LLM 帮 LLM 纠错 —— 用一次额外的 LLM 调用换取解析健壮性。

二、核心用法
    1. 定义 Pydantic 模型（Flower）
    2. 创建 PydanticOutputParser
    3. OutputFixingParser.from_llm(parser=parser, llm=llm) —— 用 LLM 包装
    4. 调用 new_parser.parse(misformatted) —— 自动修正并解析

三、与项目中其他文件的区别与联系

    07_解析输出/01_Pydantic_Parser.py    — PydanticOutputParser：输出格式正确时直接解析
    07_解析输出/02_OutputFixParser.py（本文件）— OutputFixingParser：输出格式错误时自动修正

    区别：
    - PydanticOutputParser：要求 LLM 输出必须严格符合 JSON 格式，否则报错
    - OutputFixingParser：包容输出格式错误，多花一次 LLM 调用自动修正，更健壮

    使用建议：
    - 如果 LLM 输出质量稳定（如 GPT-4），直接用 PydanticOutputParser 即可
    - 如果 LLM 输出容易出错（如小参数模型、高 temperature），建议用 OutputFixingParser
    - 注意：OutputFixingParser 多一次 LLM 调用，会增加延迟和 token 消耗
"""