from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import Language
separators = RecursiveCharacterTextSplitter.get_separators_for_language(Language.JS)
print(separators)

from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
GAME_CODE = """
class CombatSystem:
   def __init__(self):
       self.health = 100
       self.stamina = 100
       self.state = "IDLE"
       self.attack_patterns = {
           "NORMAL": 10,
           "SPECIAL": 30,
           "ULTIMATE": 50
       }
   def update(self, delta_time):
       self._update_stats(delta_time)
       self._handle_combat()
   def _update_stats(self, delta_time):
       self.stamina = min(100, self.stamina + 5 * delta_time)
   def _handle_combat(self):
       if self.state == "ATTACKING":
           self._execute_attack()
   def _execute_attack(self):
       if self.stamina >= self.attack_patterns["SPECIAL"]:
           damage = 50
           self.stamina -= self.attack_patterns["SPECIAL"]
           return damage
       return self.attack_patterns["NORMAL"]
class InventorySystem:
   def __init__(self):
       self.items = {}
       self.capacity = 20
       self.gold = 0
   def add_item(self, item_id, quantity):
       if len(self.items) < self.capacity:
           if item_id in self.items:
               self.items[item_id] += quantity
           else:
               self.items[item_id] = quantity
   def remove_item(self, item_id, quantity):
       if item_id in self.items:
           self.items[item_id] -= quantity
           if self.items[item_id] <= 0:
               del self.items[item_id]
   def get_item_count(self, item_id):
       return self.items.get(item_id, 0)
class QuestSystem:
   def __init__(self):
       self.active_quests = {}
       self.completed_quests = set()
       self.quest_log = []
   def add_quest(self, quest_id, quest_data):
       if quest_id not in self.active_quests:
           self.active_quests[quest_id] = quest_data
           self.quest_log.append(f"Started quest: {quest_data['name']}")
   def complete_quest(self, quest_id):
       if quest_id in self.active_quests:
           self.completed_quests.add(quest_id)
           del self.active_quests[quest_id]
   def get_active_quests(self):
       return list(self.active_quests.keys())
"""
python_splitter = RecursiveCharacterTextSplitter.from_language(
   language=Language.PYTHON,  # 指定编程语言为Python
   chunk_size=1000,
   chunk_overlap=0
)

python_docs = python_splitter.create_documents([GAME_CODE])
print("\n=== 代码分块结果 ===")
for i, chunk in enumerate(python_docs, 1):
    print(f"\n--- 第 {i} 个代码块 ---")
    print(f"内容:\n{chunk.page_content}")
    print(f"元数据: {chunk.metadata}")
    print("-" * 50)


# =============================================================================
# 知识点总结
# =============================================================================
#
# 1. 代码分块的核心目的
#    - 普通文本分块器（如 CharacterTextSplitter）按固定分隔符（\n、。等）切分，
#      对代码不友好，容易在函数/类中间截断，破坏代码语义。
#    - LangChain 提供了语言感知（Language-aware）的代码分块器，能识别不同
#      编程语言的语法结构（函数、类、方法等），在合适的边界处切分。
#
# 2. Language 枚举
#    - from langchain_text_splitters import Language
#    - 支持大量编程语言：PYTHON、JS、CPP、GO、RUST、JAVA、TYPESCRIPT 等
#    - 每种语言有自己的一套分隔符（separators），定义了什么位置可以切分
#
# 3. get_separators_for_language(language)
#    - 静态方法，返回指定语言的分隔符列表
#    - 例如 Language.JS 的 separators 可能包含：
#      ["\nfunction ", "\nconst ", "\nlet ", "\nclass ", ...]
#    - 这些分隔符对应代码中的"自然边界"——函数定义、变量声明、类定义等
#
# 4. RecursiveCharacterTextSplitter.from_language()
#    - 类方法，快速创建针对特定语言优化的分块器
#    - 参数：
#      · language:  指定编程语言（Language 枚举值）
#      · chunk_size: 每个分块的最大字符数
#      · chunk_overlap: 相邻分块之间的重叠字符数
#    - 内部自动使用该语言专属的 separators 进行递归切分
#
# 5. 递归分块的原理
#    - RecursiveCharacterTextSplitter 按 separators 列表的优先级顺序递归切分：
#      先尝试用优先级最高的分隔符（如 "\nclass "）切，
#      如果切出来的块仍然超过 chunk_size，再用下一个分隔符（如 "\ndef "）继续切，
#      以此类推，直到所有块都满足大小限制或无法再切。
#    - 这样保证代码尽量在"大边界"（类）处断开，语义更完整。
#
# 6. create_documents([text])
#    - 将文本列表转换为 LangChain Document 对象列表
#    - 每个 Document 包含：
#      · page_content: 分块后的文本内容
#      · metadata: 元数据（如 chunk 序号、起始位置等）
#
# 7. 注意事项 / 代码中的潜在问题
#    - 第70行 language=Language.CPP，但注释写"指定编程语言为Python"，
#      实际分割的代码也是 Python 代码 —— Language 与代码语言不匹配！
#    - 正确做法：分割 Python 代码应使用 Language.PYTHON
#    - 使用错误的 Language 会导致分隔符不匹配，分块位置不合理，
#      降低后续检索/问答的准确性
#
# 8. 应用场景
#    - 代码库的 RAG（检索增强生成）：将大型代码仓库智能分块，建立向量索引
#    - 代码问答系统：用户询问"这段代码怎么用"时，能检索到语义完整的代码片段
#    - 代码审查辅助：按函数/类粒度拆分代码，便于逐段分析
#    - IDE 智能提示：将代码分块后嵌入向量，实现语义级代码搜索
# =============================================================================
