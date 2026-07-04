

from dotenv import load_dotenv
load_dotenv()

import os

# 导入 LangChain 中的提示模板
from langchain_core.prompts import PromptTemplate

# 创建原始模板
template = """您是一位专业的鲜花店文案撰写员。
对于售价为 {price} 元的 {flower_name} ，您能提供一个吸引人的简短描述吗？
"""

# 根据原始模板创建 LangChain 提示模板
prompt = PromptTemplate.from_template(template)
# 打印 LangChain 提示模板的内容
print("=== PromptTemplate ===")
print(prompt)
print()

# 读取密钥
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

# 导入 LangChain 中的 ChatOpenAI 模型接口
# 用 Chat 模型替代 Text 模型，因为 DeepSeek 对 /v1/chat/completions 支持更好
from langchain_openai import ChatOpenAI

# 创建模型实例
model = ChatOpenAI(
    model="deepseek-chat",
    max_tokens=200,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0.7,
)

# 输入提示
input_text = prompt.format(flower_name="玫瑰", price=50)

# 得到模型的输出
output = model.invoke(input_text)

# 打印输出内容
print("=== 模型输出 ===")
print(output.content)


"""
本示例讲解：模型 IO（Input / Output）的最简结构

一、核心概念
- PromptTemplate：将模板字符串与变量绑定，生成最终的输入文本
- LLM（大语言模型）：接收输入文本，返回生成的文本
- 两者组合即构成最简的大模型调用流程

二、代码结构
1. 定义模板 template（含 {price} 和 {flower_name} 两个变量）
2. 用 PromptTemplate.from_template 创建模板对象
3. 用 prompt.format(...) 填充变量，生成最终输入
4. 用 model.invoke(input) 调用大模型，得到输出

三、与前面示例的区别
01_简单文本生成.py：直接用字符串 invoke，没有用 PromptTemplate
02_ChatModel.py：使用 Chat 模型 + messages 列表
本示例：使用 ChatOpenAI（Chat 模型）+ PromptTemplate 构造输入
"""