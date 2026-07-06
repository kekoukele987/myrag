import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
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

# 自定义带窗口截断的 History 类（相当于 ConversationBufferWindowMemory(k=1)）
class WindowedChatMessageHistory(ChatMessageHistory):
    """仅保留最近 K 轮对话的 History"""

    k: int = 1

    def add_message(self, message: BaseMessage) -> None:
        super().add_message(message)
        # 每次添加消息后，只保留最近 k 轮对话（每轮 human + AI = 2 条）
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[-(self.k * 2):]

K = 1
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = WindowedChatMessageHistory(k=K)
    return store[session_id]

conversation = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# 第一天的对话
# 回合1
result = conversation.invoke(
    {"input": "我姐姐明天要过生日，我需要一束生日花束。"},
    config={"configurable": {"session_id": "demo"}},
)
print("回合1:", result.content)
print()

# 回合2
result = conversation.invoke(
    {"input": "她喜欢粉色玫瑰，颜色是粉色的。"},
    config={"configurable": {"session_id": "demo"}},
)
print("回合2:", result.content)
print()

# 第二天的对话
# 回合3 — 由于 k=1，只保留最近 1 轮对话（回合2），应该忘记回合1
result = conversation.invoke(
    {"input": "我又来了，还记得我昨天为什么要来买花吗？"},
    config={"configurable": {"session_id": "demo"}},
)
print("回合3:", result.content)
print()

# 打印当前记忆中的消息数量，验证窗口截断
print(f"当前记忆中的消息数: {len(store['demo'].messages)}")
print("（k=1 最多保留 2 条消息，即最近 1 轮对话）")