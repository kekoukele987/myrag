# MyRAG - 从零构建 RAG 系统学习项目

一个系统化的 RAG (Retrieval-Augmented Generation) 技术学习项目，从基础概念逐步深入到实际应用，涵盖了文本生成、对话模型、文档问答系统、模型 I/O、提示工程和自定义模型调用等核心主题。

## 📂 项目结构

```
myrag/
├── 01/                              # 基础入门
│   ├── 01_简单文本生成.py            # 基础文本生成示例
│   ├── 02_看图说话.py                # 多模态（图片理解）
│   ├── 02_ChatModel.py              # ChatModel 基础使用
│   ├── 03_TextLangChain_v0.2.py     # TextLangChain 链式调用 v0.2
│   ├── 04_ChatLongChain.py          # 长链对话处理
│   ├── lang.py                      # LangChain 基础封装
│   ├── rag.py                       # RAG 基础实现
│   └── 设定.txt                     # 基础配置说明
│
├── 02_文档QA系统/                   # 文档问答系统
│   ├── DocQA_v0.1.py                # 文档问答系统 v0.1（Flask Web 应用）
│   ├── OneFlower/                   # 知识库文档（关于"一枝花"的介绍）
│   ├── static/                      # 静态资源（CSS/JS/图片）
│   └── templates/                   # HTML 模板
│
├── 03_模型IO/                       # 模型输入输出
│   ├── 01_模型IO.py                 # 模型 I/O 基础
│   ├── 02_模型IO_循环调用.py        # 循环调用与批量处理
│   ├── 03_OpenAI_IO.py              # OpenAI 模型 I/O
│   ├── 04_模型IO_HuggingFace.py     # HuggingFace 模型 I/O
│   ├── 05_模型IO_输出解析.py        # 输出解析器
│   └── flowers_with_descriptions.csv
│
├── 04_提示模板上/                   # 提示工程（上）
│   ├── 00_ImportTemplates.py        # 模板导入示例
│   ├── 01_PromptTemplate.py         # PromptTemplate 基础
│   ├── 02_ChatPromptTemplate.py     # ChatPromptTemplate 使用
│   └── 03_FewShotPrompt.py          # Few-Shot 提示模板
│
├── 05_提示模板下/                   # 提示工程（下）
│   └── CoT.py                       # 思维链（Chain-of-Thought）
│
├── 06_调用模型/                     # 模型调用方法
│   ├── 01_HugggingFace_Llama.py     # 本地 Llama 模型调用
│   ├── 02_LangChain_HFHub.py        # HuggingFace Hub 模型调用
│   └── 04_LangChain_CustomizeModel.py # 自定义模型封装
│
├── .env                             # 环境变量（API Key 等）
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip（Python 包管理器）

### 安装依赖

```bash
# 克隆项目
git clone https://github.com/kekoukele987/myrag.git
cd myrag

# 安装核心依赖
pip install langchain langchain-community langchain-openai
pip install openai huggingface-hub sentence-transformers
pip install flask  # 用于文档问答系统 Web 界面
```

### 配置环境变量

复制并编辑 `.env` 文件，填入你的 API Key：

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# HuggingFace
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

### 运行示例

```bash
# 1. 基础文本生成
python 01/01_简单文本生成.py

# 2. 启动文档问答系统（Web 界面）
python 02_文档QA系统/DocQA_v0.1.py

# 3. HuggingFace 模型调用
python 06_调用模型/02_LangChain_HFHub.py
```

## 📖 学习路线

本项目的学习路径按数字编号排列，建议按以下顺序学习：

### 第一阶段：基础入门（01/）
- **01_简单文本生成.py** — 最基础的 LLM 文本生成
- **02_看图说话.py** — 多模态输入（图片理解）
- **02_ChatModel.py** — Chat 模型的使用方式
- **03_TextLangChain_v0.2.py** — LangChain 链式调用
- **04_ChatLongChain.py** — 长对话链处理
- **lang.py & rag.py** — LangChain 和 RAG 的核心封装

### 第二阶段：文档问答系统（02_文档QA系统/）
- **DocQA_v0.1.py** — 基于 Flask 的 Web 文档问答系统
  - 📄 支持本地文档作为知识库
  - 🔍 基于向量检索 + LLM 生成的问答
  - 🌐 提供友好的 Web 交互界面

### 第三阶段：模型 I/O（03_模型IO/）
- 学习不同模型的输入输出格式
- OpenAI vs HuggingFace 的差异
- 输出解析器的使用

### 第四阶段：提示工程（04_提示模板上/、05_提示模板下/）
- PromptTemplate 基础
- ChatPromptTemplate 多角色对话
- Few-Shot 提示模板
- Chain-of-Thought（思维链）推理

### 第五阶段：模型调用进阶（06_调用模型/）
- 本地模型调用（Llama）
- HuggingFace Hub 模型
- 自定义 LangChain 模型封装

## 🛠️ 核心技术

| 技术 | 说明 |
|------|------|
| **LangChain** | 核心框架，提供链式调用、模型 I/O、提示模板等 |
| **OpenAI API** | GPT 系列模型调用 |
| **HuggingFace** | 开源模型调用与推理 |
| **Flask** | Web 服务框架，用于构建问答系统 UI |
| **RAG** | 检索增强生成，结合向量检索与 LLM |
| **Prompt Engineering** | 提示工程，包括 Few-Shot、CoT 等技术 |

## 📦 依赖清单

```
langchain
langchain-community
langchain-openai
openai
huggingface-hub
sentence-transformers
flask
python-dotenv
```

## 🤝 贡献指南

欢迎通过 Issue 和 Pull Request 贡献代码或提出建议！

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) — LLM 应用开发框架
- [OpenAI](https://openai.com/) — GPT 模型 API
- [Hugging Face](https://huggingface.co/) — 开源模型社区