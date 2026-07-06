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

# ============================================================================
# 与 01_Without_Chain.py 的异同点对比
# ============================================================================
#
# 一、相同点
# ----------------------------------------------------------------------------
#   1. 依赖相同：dotenv / ChatOpenAI(DeepSeek) / PromptTemplate
#   2. 模型配置相同：deepseek-chat / temperature=0 / 同一组 API Key
#   3. 模板相同："{flower}的花语是?"，填充 flower='玫瑰'
#   4. 底层调用相同：实际都调用了 model.invoke()
#   5. 使用相同的 LangChain 1.0+ 现代化接口
#
# 二、不同点
# ----------------------------------------------------------------------------
#   +-----------------------------+----------------------------+----------------------------+
#   |           维度              |     01_Without_Chain.py    |   02_With_LLMChain.py      |
#   +-----------------------------+----------------------------+----------------------------+
#   | 调用方式                    | 手动分两步：               | LCEL 链式语法：             |
#   |                             | ① prompt.format()         | ① prompt | model            |
#   |                             | ② model.invoke(prompt)    | ② chain.invoke({...})      |
#   | 传参方式                    | 传入预格式化好的字符串     | 传入字典 {"flower": "玫瑰"} |
#   | 代码行数                    | 30 行                      | 21 行                      |
#   | 链式组合                    | ❌ 无，手动串行            | ✅ 有，| 运算符自动组合     |
#   | 变量注入时机                | 调用前（format 时注入）    | 调用时（invoke 时注入）    |
#   | 可扩展性                    | 每增加组件需手动调整        | 链式管道，易插拔扩展        |
#   +-----------------------------+----------------------------+----------------------------+
#
# 三、涉及知识点
# ----------------------------------------------------------------------------
#   1. 环境变量管理：python-dotenv / load_dotenv() / os.getenv()
#   2. 提示模板：PromptTemplate.from_template() / format() 填充变量
#   3. LLM 封装：ChatOpenAI（兼容 OpenAI / DeepSeek / 通义千问等任意 OpenAI 兼容 API）
#   4. 模型配置：model / temperature / openai_api_key / openai_api_base
#   5. 模型调用：model.invoke() — LangChain 1.0+ 统一调用入口
#   6. LCEL 语法：| 管道运算符组合 prompt 和 model 形成链
#   7. 链式调用：chain.invoke({"flower": "玫瑰"}) — 自动填充模板 + 调用模型
#   8. 响应处理：result.content — ChatOpenAI 返回 AIMessage 对象
#   9. 设计思想：模块解耦（提示与模型分离）vs 链式组合（提示与模型组合）
# ============================================================================
