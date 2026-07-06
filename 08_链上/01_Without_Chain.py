import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 加载环境变量
load_dotenv()

# ----第一步 创建提示----
# 原始字符串模板
template = "{flower}的花语是?"
# 创建LangChain模板
prompt_temp = PromptTemplate.from_template(template)
# 根据模板创建提示
prompt = prompt_temp.format(flower='玫瑰')
# 打印提示的内容
print(prompt)

# ----第二步 创建并调用模型----
# 使用 DeepSeek API（兼容 OpenAI 接口）
model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0,
)

# 传入提示，调用模型，返回结果
result = model.invoke(prompt)
print(result.content)