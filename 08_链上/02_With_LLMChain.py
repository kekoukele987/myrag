import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

template = "{flower}的花语是?"
prompt = PromptTemplate.from_template(template)

model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0,
)

# LCEL 链：prompt | model
chain = prompt | model
result = chain.invoke({"flower": "玫瑰"})
print(result.content)