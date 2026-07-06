import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 初始化模型
model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.7,
)

# ---- 链1：生成鲜花介绍（依赖原始输入 name, color）----
intro_prompt = PromptTemplate.from_template(
    "你是一个植物学家。给定花的名称和类型，你需要为这种花写一个200字左右的介绍。\n"
    "花名: {name}\n"
    "颜色: {color}\n"
    "植物学家: 这是关于上述花的介绍:"
)
intro_chain = intro_prompt | model

# ---- 链2：根据介绍写评论（依赖链1的输出 introduction）----
review_prompt = PromptTemplate.from_template(
    "你是一位鲜花评论家。给定一种花的介绍，你需要为这种花写一篇200字左右的评论。\n"
    "鲜花介绍:\n{introduction}\n"
    "花评人对上述花的评论:"
)
review_chain = RunnablePassthrough.assign(
    introduction=lambda x: x["introduction"]  # 从上游取 introduction
) | review_prompt | model

# ---- 链3：根据介绍和评论写社交媒体帖（依赖链1+链2的输出）----
social_prompt = PromptTemplate.from_template(
    "你是一家花店的社交媒体经理。给定一种花的介绍和评论，你需要为这种花写一篇社交媒体的帖子，300字左右。\n"
    "鲜花介绍:\n{introduction}\n"
    "花评人对上述花的评论:\n{review}\n"
    "社交媒体帖子:"
)
social_chain = RunnablePassthrough.assign(
    introduction=lambda x: x["introduction"],
    review=lambda x: x["review"],
) | social_prompt | model

# ---- 三步串联 ----
# 步骤1：根据 name + color 生成 introduction
step1 = (
    RunnablePassthrough.assign(
        introduction=lambda x: intro_chain.invoke({
            "name": x["name"],
            "color": x["color"]
        }).content
    )
)

# 步骤2：根据 introduction 生成 review
step2 = (
    RunnablePassthrough.assign(
        review=lambda x: review_chain.invoke({
            "introduction": x["introduction"]
        }).content
    )
)

# 步骤3：根据 introduction + review 生成 social_post_text
step3 = (
    RunnablePassthrough.assign(
        social_post_text=lambda x: social_chain.invoke({
            "introduction": x["introduction"],
            "review": x["review"]
        }).content
    )
)

# 合并为完整链（相当于原 SequentialChain）
overall_chain = step1 | step2 | step3

# 运行并打印结果
result = overall_chain.invoke({
    "name": "玫瑰",
    "color": "黑色"
})

print("=" * 60)
print("鲜花介绍")
print("=" * 60)
print(result["introduction"])
print()

print("=" * 60)
print("花评")
print("=" * 60)
print(result["review"])
print()

print("=" * 60)
print("社交媒体帖子")
print("=" * 60)
print(result["social_post_text"])


# ============================================================================
# 文件说明
# ============================================================================
#
# 功能：使用 SequentialChain 的方式，通过三步串联完成一个完整的花卉营销内容生成：
#       步骤1：根据花名和颜色生成植物学介绍
#       步骤2：根据介绍生成花评
#       步骤3：根据介绍和花评生成社交媒体帖子
#
# 与原文件的对比（重构说明）
# ----------------------------------------------------------------------------
#   +-----------------------------+----------------------------+----------------------------+
#   |           维度              |          重构前             |          重构后             |
#   +-----------------------------+----------------------------+----------------------------+
#   | API Key                     | 硬编码 'Your Key'          | .env 加载 DEEPSEEK_API_KEY |
#   | 模型                        | langchain.llms.OpenAI      | langchain_openai.ChatOpenAI|
#   | 链实现                      | LLMChain + SequentialChain | LCEL: RunnablePassthrough   |
#   |                             |                            |  + assign + invoke          |
#   | 链串联                      | SequentialChain(chains=[]) | step1 | step2 | step3      |
#   | 链间传参                    | output_key 自动映射        | x["introduction"] 手动传递 |
#   | 输出格式                    | 单个 dict 打印             | 分 section 打印更清晰      |
#   +-----------------------------+----------------------------+----------------------------+
#
# 涉及知识点
# ----------------------------------------------------------------------------
#   1. 环境变量管理：python-dotenv / load_dotenv() / os.getenv()
#   2. 提示模板：PromptTemplate.from_template() 多变量模板
#   3. LLM 封装：ChatOpenAI（DeepSeek 兼容 OpenAI 接口）
#   4. RunnablePassthrough.assign()：在链中传递并新增字段
#   5. LCEL 管道运算符 | ：将 prompt → model → 处理步骤串联
#   6. 多步串联：step1 | step2 | step3 实现顺序执行
#   7. 链间数据传递：通过 lambda 从上一个步骤的结果中提取字段
#   8. 响应处理：result.content 提取 AIMessage 文本
#   9. 设计模式：函数式链式组合替代面向对象的 SequentialChain
#  10. invoke 统一接口：多次 invoke 组合成完整流程
# ============================================================================