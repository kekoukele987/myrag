from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import FewShotPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import (
    ChatMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

"""
本文件仅演示各种 PromptTemplate 的导入方式，不涉及模型调用。

与旧版区别：
langchain.prompts.prompt → langchain_core.prompts
langchain.prompts.few_shot → langchain_core.prompts
langchain.prompts.pipeline → 已废弃（未导入）
"""

if __name__ == "__main__":
    print("所有模板类导入成功")
    print(f"PromptTemplate: {PromptTemplate}")
    print(f"ChatPromptTemplate: {ChatPromptTemplate}")
    print(f"FewShotPromptTemplate: {FewShotPromptTemplate}")