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

print(query_engine.query("黑神话悟空的故事有哪些人物?"))

print(query_engine.query("黑神话悟空的故事有哪些地理环境?"))


"""

2026-07-03 19:06:34,594 - INFO - HTTP Request: POST https://api.deepseek.com/v1/chat/completions "HTTP/1.1 200 OK"         
《黑神话：悟空》的故事共有六个章节，分别是“火照黑云”、“风起黄昏”、“夜生白露”、“曲度紫鸳”、“日落红尘”和“未竟”。
2026-07-03 19:06:35,840 - INFO - HTTP Request: POST https://api.deepseek.com/v1/chat/completions "HTTP/1.1 200 OK"
根据提供的信息，无法确定《黑神话：悟空》故事中具体有哪些人物。
2026-07-03 19:06:36,889 - INFO - HTTP Request: POST https://api.deepseek.com/v1/chat/completions "HTTP/1.1 200 OK"
《黑神话：悟空》的故事中包含了重庆的大足石刻、山西省的小西天、南禅寺、铁佛寺、广胜寺和鹳雀楼等地理环境。


BAAI/bge-small-zh-v1.5 是本地向量嵌入模型（Embedding），负责本地私有文档语义检索；
https://api.deepseek.com/v1 是云端大语言模型（LLM），负责理解检索到的内容、生成最终回答；

三、为什么不能只用其中一个？
只调用 DeepSeek API，不用本地 bge
私有知识库必须全部上传云端，数据泄露风险极高；
大模型训练知识截止时间固定，无法读取你本地新增业务文档；
海量文档全丢进 prompt 会超长、高额 token 费用、触发上下文限制；
容易出现幻觉，不知道你的私有业务资料。
只本地跑 bge，不用 DeepSeek API
bge 只会算相似度、找文档，没有生成文本能力，不能总结、回答、推理，只能返回原文片段，无法交付自然语言回复。
"""