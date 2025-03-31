from openai import OpenAI
import base64
from PIL import Image
import os
from PIL.ExifTags import TAGS
import io

def get_image_metadata(image_path):
    """获取图片的元数据"""
    image = Image.open(image_path)
    metadata = {}
    
    # 基础信息
    metadata['format'] = image.format
    metadata['size'] = image.size
    metadata['mode'] = image.mode
    
    # EXIF信息
    if hasattr(image, '_getexif') and image._getexif():
        exif = image._getexif()
        for tag_id in exif:
            tag = TAGS.get(tag_id, tag_id)
            metadata[tag] = exif[tag_id]
    
    return metadata

def encode_image(image_path):
    """将图片转换为base64编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = OpenAI(
    base_url='https://api-inference.modelscope.cn/v1/',
    api_key='010243e5-16c5-46c3-8c37-5ab8f37f09b5',  # ModelScope Token
)

# 处理本地图片
image_path = "C:\\Users\\19706\\Desktop\\papers\\deepseek_paper\\DeepSeek_R1\\R1文献图片\\DeepSeek_R1_06.png"  # 替换为你的本地图片路径
metadata = get_image_metadata(image_path)
base64_image = encode_image(image_path)

# 构建请求
response = client.chat.completions.create(
    model='Qwen/Qwen2.5-VL-32B-Instruct',  # ModelScope Model-Id
    messages=[{
        'role': 'user',
        'content': [{
            'type': 'text',
            'text': f'描述这幅图，并分析图片的以下元数据信息：{metadata}',
        }, {
            'type': 'image_url',
            'image_url': {
                'url': f"data:image/jpeg;base64,{base64_image}"
            },
        }],
    }],
    stream=True
)

print("图片元数据：")
for key, value in metadata.items():
    print(f"{key}: {value}")

print("\n图片内容分析：")
for chunk in response:
    print(chunk.choices[0].delta.content, end='', flush=True)
