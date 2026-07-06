import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

# 初始化模型
model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.5,
)

# 创建对话提示模板（含历史消息占位符）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个乐于助人的助手，用中文回答用户的问题。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

# 打印对话的模板
print("=" * 60)
print("对话提示模板")
print("=" * 60)
print(prompt.pretty_repr())
print()

# 构建链
chain = prompt | model

# 用 RunnableWithMessageHistory 包装，自动管理历史消息
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 演示两轮对话（记忆效果）
print("=" * 60)
print("对话演示（带记忆）")
print("=" * 60)

response1 = conversation.invoke(
    {"input": "你好！我叫小明。"},
    config={"configurable": {"session_id": "demo"}},
)
print(f"用户: 你好！我叫小明。")
print(f"助手: {response1.content}")
print()

response2 = conversation.invoke(
    {"input": "我叫什么名字？"},
    config={"configurable": {"session_id": "demo"}},
)
print(f"用户: 我叫什么名字？")
print(f"助手: {response2.content}")