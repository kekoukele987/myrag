import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量（密钥不要硬编码在代码中）
load_dotenv()

import openai
from typing import Optional, List, Sequence
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.base.llms.types import (
    ChatMessage, ChatResponse, CompletionResponse, MessageRole,
    LLMMetadata,
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.fastembed import FastEmbedEmbedding

# ==== 自定义 DeepSeek LLM 包装类，强制使用 chat 端点 ====
class DeepSeekLLM(OpenAI):
    """强制使用 chat completions 端点的 DeepSeek 包装类"""
    
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=65536,
            num_output=self.max_tokens or 4096,
            is_chat_model=True,
            is_function_calling_model=True,
            model_name=self.model,
        )
    
    def complete(self, prompt: str, formatted: bool = False, **kwargs) -> CompletionResponse:
        # 将 complete 请求转为 chat 请求（DeepSeek 不支持 /completions 端点）
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        chat_response = self.chat(messages, **kwargs)
        return CompletionResponse(
            text=chat_response.message.content or "",
            additional_kwargs=chat_response.additional_kwargs,
        )

# ===========================================================

# ========== 替换为DeepSeek配置 ==========
# 从环境变量读取 API 密钥（已在 .env 中配置 DEEPSEEK_API_KEY）
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

# 1. 配置DeepSeek API客户端（指向DeepSeek的/v1端点，使用chat completions）
deepseek_client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

# 2. 配置DeepSeek LLM（对话大模型）
Settings.llm = DeepSeekLLM(
    model="deepseek-chat",       # DeepSeek 对话模型
    temperature=0.0,
    context_window=65536,        # DeepSeek 上下文长度 64K
    openai_client=deepseek_client,  # 使用自定义客户端指向DeepSeek
)

# 3. 配置本地Embedding模型（FastEmbed内置模型，已下载缓存）
Settings.embed_model = FastEmbedEmbedding(
    model_name="BAAI/bge-small-zh-v1.5"
)
# =======================================

# 下面原有代码完全不用改
documents = SimpleDirectoryReader(input_files=["设定.txt"]).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
print(query_engine.query("黑神话悟空的故事有哪些章节?"))