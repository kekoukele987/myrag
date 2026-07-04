"""


重构说明：使用 Ollama 本地服务替代 llama.cpp 调用模型

本文件提供了两种方式使用本地模型：
  方式一：直接使用 ChatOllama（推荐，更简洁）
  方式二：自定义 CustomLLM 类（继承 LLM 基类，适合需要统一接口的场景）
"""
from typing import Optional, List, Mapping, Any
from langchain_ollama import ChatOllama
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import ChatPromptTemplate

# ============================================================================
# 方式一：直接使用 ChatOllama（推荐）
# ============================================================================
def call_with_chatollama(prompt: str, model_name: str = "qwen:1.8b") -> str:
    """使用 ChatOllama 直接调用本地模型

    这是最简洁的方式，无需自定义 LLM 类。

    Args:
        prompt: 用户输入的问题
        model_name: Ollama 模型名称，默认 qwen:1.8b

    Returns:
        模型生成的回复文本
    """
    llm = ChatOllama(
        model=model_name,
        temperature=0.7,
        base_url="http://localhost:11434",
    )

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业友好的客服人员，请用中文回答用户的问题。"),
        ("user", "{user_input}"),
    ])

    messages = prompt_template.format_messages(user_input=prompt)
    response = llm.invoke(messages)
    return response.content


# ============================================================================
# 方式二：自定义 LLM 类（继承 LLM 基类）
# ============================================================================
class CustomLLM(LLM):
    """自定义LLM，使用Ollama本地服务调用模型

    继承自 langchain_core.language_models.llms.LLM 基类，
    实现 _call 抽象方法，使该类的使用方式与 LangChain 生态统一。
    适用于需要替换为其他 LLM 后端的场景。
    """

    model_name: str = "qwen:1.8b"              # Ollama 模型名称
    temperature: float = 0.7                   # 生成温度
    base_url: str = "http://localhost:11434"    # Ollama 服务地址

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """使用 ChatOllama 调用本地模型生成回复

        注意：_call 是 LLM 基类的抽象方法，接收纯文本 prompt，
        返回纯文本 response。由 invoke() 方法自动调用。
        """
        llm = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url,
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业友好的客服人员，请用中文回答用户的问题。"),
            ("user", "{user_input}"),
        ])

        messages = prompt_template.format_messages(user_input=prompt)
        response = llm.invoke(messages)
        return response.content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """返回模型的标识参数，用于日志和调试"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "base_url": self.base_url,
        }

    @property
    def _llm_type(self) -> str:
        """返回模型的类型标识"""
        return "custom_ollama"


# ============================================================================
# 使用示例
# ============================================================================
if __name__ == "__main__":
    user_question = (
        "昨天有一个客户抱怨他买了花给女朋友之后，两天花就枯了，"
        "你说作为客服我应该怎么解释？"
    )

    # 方式一：直接使用 ChatOllama
    print("=" * 60)
    print("方式一：ChatOllama 直接调用")
    print("=" * 60)
    result1 = call_with_chatollama(user_question, model_name="qwen:1.8b")
    print(f"客服回答：{result1}")
    print()

    # 方式二：使用自定义 LLM 类
    print("=" * 60)
    print("方式二：CustomLLM 自定义类调用")
    print("=" * 60)
    llm = CustomLLM(model_name="qwen:1.8b")
    result2 = llm.invoke(user_question)
    print(f"客服回答：{result2}")


# ============================================================================
# 附录：重构前后对比说明
# ============================================================================
#
# 一、主要用到的模型
# ----------------------------------------------------------------------------
#   重构前: llama-2-7b-chat.ggmlv3.q4_K_S.bin
#           (通过 llama_cpp 直接加载本地 GGUF 文件)
#   重构后: qwen:1.8b
#           (通过 Ollama 服务调用，也可切换为 deepseek-coder-v2:16b)
#
#   Ollama 是一个本地模型运行框架，支持 Qwen / Llama / DeepSeek 等多种模型，
#   提供兼容 OpenAI 的 REST API 接口 (http://localhost:11434)。
#
# 二、主要使用的方法
# ----------------------------------------------------------------------------
#   1. ChatOllama  (langchain-ollama 包)
#      - 通过 Ollama 服务 API 调用本地模型的 LLM 封装类
#      - 支持 Chat 格式的对话接口 (invoke 传 messages 列表)
#
#   2. ChatPromptTemplate  (langchain-core 包)
#      - 结构化对话提示模板，支持 system / user / assistant 角色
#      - from_messages() 创建模板  ->  format_messages() 填充变量
#
#   3. LLM._call() 抽象方法
#      - 继承自 langchain_core.language_models.llms.LLM 基类
#      - 必须实现，接收 prompt 字符串，返回模型生成的文本
#      - 在调用 llm.invoke(prompt) 时被底层自动调用
#
#   4. invoke() 方法
#      - LangChain 1.0+ 推荐的统一调用接口
#      - 替代旧版 __call__() 直接调用对象的方式
#      - LLM.invoke(prompt) -> 内部调用 _call(prompt) -> 返回 str
#      - ChatOllama.invoke(messages) -> 返回 AIMessage 对象
#
# 三、核心用法示例
# ----------------------------------------------------------------------------
#   方式一（函数式）:
#     result = call_with_chatollama("用户问题", model_name="qwen:1.8b")
#
#   方式二（面向对象）:
#     llm = CustomLLM(model_name="qwen:1.8b")
#     result = llm.invoke("用户问题")
#
#   可配置项:
#     - model_name:   Ollama 中的模型名称
#     - temperature:  生成温度 (0~1)，越高越有创造性
#     - base_url:     Ollama 服务地址，默认 http://localhost:11434
#
# 四、与原版 (llama_cpp) 的对比
# ----------------------------------------------------------------------------
#   +--------------------+---------------------------+----------------------------+
#   |      维度          |        重构前             |          重构后             |
#   +--------------------+---------------------------+----------------------------+
#   | 模型加载方式       | Llama() 直接加载本地      | ChatOllama 通过 API 调用   |
#   |                    | GGUF 文件                | Ollama 管理模型生命周期     |
#   | 模型路径           | 硬编码 Linux 路径         | 只需模型名称，Ollama 管理  |
#   |                    | 不可移植                 |                            |
#   | 提示格式           | 手动拼接 f"Q:...A:"      | ChatPromptTemplate 结构化  |
#   |                    | 字符串操作               | 支持 system/user 角色      |
#   | 调用方式           | 旧版 llm(prompt)         | invoke() 统一接口          |
#   |                    |                           | llm.invoke(prompt)         |
#   | 平台兼容性         | Linux only               | 跨平台 (Win/Mac/Linux)     |
#   | 模型切换           | 需下载不同 GGUF 文件     | 改一行模型名即可           |
#   |                    | 并修改路径               | ollama pull 新模型名       |
#   | 依赖包             | llama-cpp-python         | langchain-ollama           |
#   |                    | (需 C++ 编译环境)        | ollama (Python 客户端)     |
#   +--------------------+---------------------------+----------------------------+
#
# 五、本地可用的 Ollama 模型
# ----------------------------------------------------------------------------
#   1. qwen:1.8b              - 轻量级模型，响应快，适合日常对话
#   2. deepseek-coder-v2:16b  - 更强的编程和推理能力，但需要更多资源
#
#   安装新模型:  ollama pull <模型名>
#   查看已安装:  ollama list
# ============================================================================