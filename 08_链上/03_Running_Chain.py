import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

# 设置提示模板（多变量）
prompt = PromptTemplate(
    input_variables=["flower", "season"],
    template="{flower}在{season}的花语是?"
)

# 初始化大模型
model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0,
)

# LCEL 链
chain = prompt | model

# ---- 1. invoke — 替代 __call__ 和 run ----
print("=" * 60)
print("1. chain.invoke() — 替代 __call__ 和 run")
print("=" * 60)
response = chain.invoke({
    'flower': "玫瑰",
    'season': "夏季"
})
print(response.content)
print()

# ---- 2. batch — 替代 apply 和 generate ----
print("=" * 60)
print("2. chain.batch() — 替代 apply 和 generate")
print("=" * 60)
input_list = [
    {"flower": "玫瑰", 'season': "夏季"},
    {"flower": "百合", 'season': "春季"},
    {"flower": "郁金香", 'season': "秋季"}
]
results = chain.batch(input_list)
for r in results:
    print(r.content)
print()

# ---- 3. stream — 流式输出（LCEL 新增功能）----
print("=" * 60)
print("3. chain.stream() — 流式输出（原 LLMChain 无此功能）")
print("=" * 60)
for chunk in chain.stream({"flower": "玫瑰", "season": "夏季"}):
    print(chunk.content, end="", flush=True)
print("\n")

# ---- 4. 单变量 prompt + model — 与 02 类似 ----
print("=" * 60)
print("4. 单变量 prompt（示意 LCEL 灵活性）")
print("=" * 60)
single_prompt = PromptTemplate.from_template("{flower}的花语是?")
single_chain = single_prompt | model
result = single_chain.invoke({"flower": "玫瑰"})
print(result.content)