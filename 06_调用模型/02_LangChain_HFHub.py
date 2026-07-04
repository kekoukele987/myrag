from dotenv import load_dotenv
load_dotenv()

import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

# 创建简单的 question-answering 提示模板
template = """Question: {question}
Answer: """

prompt = PromptTemplate(template=template, input_variables=["question"])

# 使用 LCEL 构建链（等价于旧版的 LLMChain，新版推荐方式）
chain = prompt | llm | StrOutputParser()

question = "Rose is which type of flower?"
print("=== 链式调用（LCEL）===")
result = chain.invoke({"question": question})
print(result)


"""
本示例演示：用 LCEL 替代 LLMChain

核心结论：
- DeepSeek 没有自己的 LLMChain —— LLMChain 是 langchain 的概念
- langchain 1.x 的 LLMChain 在新版中已废弃，改为 LCEL（LangChain Expression Language）
- LCEL 更简洁：prompt | llm | parser 就能完成链式调用
- 本质上就是 PromptTemplate + LLM + 输出解析的组合


与旧版区别：
langchain.llms.HuggingFaceHub → langchain_openai.ChatOpenAI
langchain.LLMChain → LCEL（prompt | llm | parser）

旧版 LLMChain 方式（等价的示意代码）：
llm_chain = LLMChain(prompt=prompt, llm=llm)
result = llm_chain.run(question)



 管道语法，| 是管道操作符，作用和 Linux shell 的 | 一样：把前一步输出，传给后一步当输入，串联成完整执行链路。


"""