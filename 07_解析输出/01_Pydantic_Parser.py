from dotenv import load_dotenv
load_dotenv()

import os

# 创建模型实例（使用 DeepSeek Chat API）
from langchain_openai import ChatOpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

model = ChatOpenAI(
    model="deepseek-chat",
    max_tokens=500,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    temperature=0.7,
)

# 创建一个空的 DataFrame 用于存储结果
import pandas as pd
df = pd.DataFrame(columns=["flower_type", "price", "description", "reason"])

# 数据准备
flowers = ["玫瑰", "百合", "康乃馨"]
prices = ["50", "30", "20"]

# 定义我们想要接收的数据格式
from pydantic import BaseModel, Field


class FlowerDescription(BaseModel):
    flower_type: str = Field(description="鲜花的种类")
    price: int = Field(description="鲜花的价格")
    description: str = Field(description="鲜花的描述文案")
    reason: str = Field(description="为什么要这样写这个文案")


# 创建输出解析器
from langchain_core.output_parsers import PydanticOutputParser

output_parser = PydanticOutputParser(pydantic_object=FlowerDescription)

# 获取输出格式指示
format_instructions = output_parser.get_format_instructions()
print("=== 输出格式 ===")
print(format_instructions)
print()

# 创建提示模板
from langchain_core.prompts import PromptTemplate

prompt_template = """您是一位专业的鲜花店文案撰写员。
对于售价为 {price} 元的 {flower} ，您能提供一个吸引人的简短中文描述吗？
{format_instructions}"""

# 根据模板创建提示，同时在提示中加入输出解析器的说明
prompt = PromptTemplate.from_template(
    prompt_template,
    partial_variables={"format_instructions": format_instructions},
)

# 循环处理每种花
for flower, price in zip(flowers, prices):
    # 根据提示准备模型的输入
    input_prompt = prompt.format(flower=flower, price=price)
    print(f"=== 输入（{flower} {price}元）===")
    print(input_prompt)
    print()

    # 获取模型的输出
    output = model.invoke(input_prompt)

    # 解析模型的输出
    parsed_output = output_parser.parse(output.content)
    parsed_output_dict = parsed_output.model_dump()  # Pydantic v2: .model_dump() 替代 .dict()

    # 将解析后的输出添加到 DataFrame 中
    df.loc[len(df)] = parsed_output.model_dump()

# 打印结果
print("=== 输出数据 ===")
print(df.to_dict(orient="records"))


"""
本示例演示：Pydantic 输出解析器（PydanticOutputParser）—— 结构化数据输出

一、涉及的知识点（RAG 链路中的"Output"环节）
    RAG 完整链路：Load（加载文档）→ Split（切分）→ Embedding（向量化）→ Store（存储）
    → Retrieval（检索）→ Augment（增强，即 Prompt 拼接）→ Generation（生成）→ Output（输出解析）

    本文件聚焦在"Output（输出解析）"环节：
    - 模型生成的是非结构化文本，但下游业务（数据库写入、API 返回、前端渲染）需要结构化数据
    - PydanticOutputParser 将模型输出强制解析成预定义的结构（Pydantic 模型），
      实现"非结构化文本 → 结构化数据"的转换，让 LLM 输出能直接对接业务系统

二、核心用法
    1. 定义 Pydantic 模型（继承 BaseModel），用 Field 指定每个字段的描述和类型
    2. 创建 PydanticOutputParser，传入模型类
    3. parser.get_format_instructions() 自动生成 JSON Schema 格式说明
    4. 将格式说明注入到 Prompt 中（通过 partial_variables 绑定到 {format_instructions}）
    5. 模型输出的 JSON 文本 → parser.parse(output) → 得到 Pydantic 对象
    6. parsed.model_dump() 转为字典，可写入 DataFrame / 数据库 / API 返回

三、与项目中其他文件的区别与联系

    03_模型IO/05_模型IO_输出解析.py            — JsonOutputParser（输出 JSON 字典，无类型校验）
    07_解析输出/01_Pydantic_Parser.py（本文件）— PydanticOutputParser（基于 Pydantic 模型，有字段类型/描述校验）

    区别：
    - JsonOutputParser：输出是普通的 dict，不校验字段类型，不提供字段描述
    - PydanticOutputParser：继承 BaseModel，字段有类型约束（int/str/float）和描述，
      解析时会做类型转换和校验（比如 price 字段自动转 int），更适合生产环境

    进阶联系：
    - 当 RAG 系统需要将检索结果 + LLM 生成结果以结构化形式存入数据库时，
      PydanticOutputParser 是最佳选择（类型安全、可序列化、自带文档）
    - 可与 02_文档QA系统/DocQA_v0.1.py 结合：问答系统的输出先经过 Pydantic 解析，
      再格式化为 JSON API 返回给前端
"""

"""
=== 输出数据 ===
[
{'flower_type': '玫瑰', 'price': 50, 'description': '只需50元，把一整天的浪漫捧在手里。这朵玫瑰，是怦然心动的颜色，也是无需多言的告白。', 
'reason': '用‘只需’强调价格亲民，同时将玫瑰与浪漫、告白等情感价值关联，让顾客觉得物超所值，激发购买冲动。'}, 
{'flower_type': '百合', 'price': 30, 'description': '30元就能拥有的纯洁与高贵，让这一束百合为你的家注入宁静的芬芳。', 
'reason': '强调价格亲民与百合象征的纯洁、高贵气质，同时用‘宁静的芬芳’唤起情感共鸣，适合日常购买或送礼场景。'},
{'flower_type': '康乃馨', 'price': 20, 'description': '二十元，把整个春天的温柔带回家。', 
'reason': '用数字与意象结合，突出价格亲民的同时，赋予康乃馨温暖、柔美的情感价值，容易打动顾客。”\n}'}
]
"""