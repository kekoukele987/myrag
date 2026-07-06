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

# 第一天的对话
# 回合1
response1 = conversation.invoke(
    {"input": "我姐姐明天要过生日，我需要一束生日花束。"},
    config={"configurable": {"session_id": "demo"}},
)
print("第一次对话后的记忆:", store["demo"].messages)
print()

# 回合2
response2 = conversation.invoke(
    {"input": "她喜欢粉色玫瑰，颜色是粉色的。"},
    config={"configurable": {"session_id": "demo"}},
)
print("第二次对话后的记忆:", store["demo"].messages)
print()

# 回合3（第二天的对话）
response3 = conversation.invoke(
    {"input": "我又来了，还记得我昨天为什么要来买花吗？"},
    config={"configurable": {"session_id": "demo"}},
)
print("第三次对话后的记忆:", store["demo"].messages)
print()

print("助手第三次回答:", response3.content)