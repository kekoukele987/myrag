from dotenv import load_dotenv
load_dotenv()

import os

from langchain_core.prompts import PromptTemplate

template = """You are a flower shop assistant.
For {price} of {flower_name} , can you write something for me？
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

input_text = prompt.format(flower_name="玫瑰", price=50)
output = model.invoke(input_text)
print("=== 模型输出 ===")
print(output.content)


"""
本示例演示：模型 IO —— 使用 ChatOpenAI 替代 HuggingFaceHub

原代码使用 HuggingFaceHub(repo_id="google/flan-t5-large")，需要联网且依赖 HuggingFace 服务。
由于网络环境限制，已替换为 DeepSeek Chat API（与 01_模型IO.py 相同的调用方式）。

与其他文件的区别：
01_模型IO.py：单次调用，PromptTemplate + ChatOpenAI
02_模型IO_循环调用.py：循环调用，对多种花批量生成
03_OpenAI_IO.py：用原生 openai SDK（不用 langchain）
04_模型IO_HuggingFace.py：原为 HuggingFaceHub 模型，现改为 DeepSeek Chat（结构同 01）
"""