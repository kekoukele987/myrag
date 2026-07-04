# HuggingFace 国内镜像加速
import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"      # 使用国内镜像下载模型
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"       # 关闭软链接警告

from dotenv import load_dotenv
load_dotenv()

import requests
from PIL import Image
from io import BytesIO
from transformers import BlipProcessor, BlipForConditionalGeneration
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ---- Part I 初始化图像字幕生成模型 ----
hf_model = "Salesforce/blip-image-captioning-base"

print("正在加载图像描述模型（从国内镜像下载）...")
processor = BlipProcessor.from_pretrained(hf_model)
model = BlipForConditionalGeneration.from_pretrained(hf_model)
print("模型加载完成")

# ---- Part II 图像字幕生成函数 ----
def generate_caption(url: str) -> str:
    """下载图片并用BLIP生成英文描述"""
    print(f"\n正在下载图片: {url}")
    response = requests.get(url, timeout=15)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    caption = processor.decode(out[0], skip_special_tokens=True)
    print(f"图片描述: {caption}")
    return caption

# ---- Part III 调用 DeepSeek 生成推广文案 ----
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("请先在 .env 文件中设置 DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.7,
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
)

# 使用一张可用的图片（Pexels免费图库）
img_url = "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg"

# 1) 生成图片描述
caption = generate_caption(img_url)

# 2) 让 DeepSeek 根据描述创作推广文案
messages = [
    SystemMessage(content="你是一个创意广告文案撰写专家。"),
    HumanMessage(content=f"以下是一张图片的描述：\n{caption}\n\n请根据这个图片场景，创作一段适合的中文推广文案。")
]
print("\n正在生成推广文案...")
result = llm.invoke(messages)
print("\n===== 推广文案 =====")
print(result.content)