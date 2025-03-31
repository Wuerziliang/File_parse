import requests
import json
import base64
from PIL import Image
import io
import datetime
import re
import os

url = "https://api.siliconflow.cn/v1/chat/completions"
url_image = "https://api.siliconflow.cn/v1/images/generations"
model = "deepseek-ai/DeepSeek-R1"
model_image = "Kwai-Kolors/Kolors"

# 初始化系统角色
messages = [
    {"role": "system", "content": "你是一个智能助手，可以回答用户的各种问题。当用户要求画图时，请详细描述要画的内容。"}
]

def chat_with_api(messages):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": 16384,
        "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }

    headers = {
        "Authorization": "Bearer sk-jelifbfcfupdddnoqzgunzehavucvjzcpsmqmwoirqbacehl",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)
    assistant_response = ""

    if response.status_code == 200:
        first_reasoning_content_output = True
        first_content_output = True
        should_generate_image = False
        image_prompt = ""
        
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').strip()
                try:
                    if chunk_str.startswith('data:'):
                        chunk_str = chunk_str[6:].strip()
                    if chunk_str == "[DONE]":
                        print("\n\n============[DONE]============\n")
                        # 检查回答中是否包含需要生成图片的关键词
                        keywords = ["画一张", "生成一张", "绘制一张", "帮我画", "帮我生成"]
                        for keyword in keywords:
                            if keyword in assistant_response:
                                should_generate_image = True
                                # 提取图片描述
                                image_prompt = assistant_response
                                break
                        break
                    
                    chunk_json = json.loads(chunk_str)
                    if 'choices' in chunk_json and isinstance(chunk_json['choices'], list) and len(chunk_json['choices']) > 0:
                        choice = chunk_json['choices'][0]
                        delta = choice.get('delta', {})
                        reasoning_content = delta.get('reasoning_content')
                        content = delta.get('content')
                        
                        if reasoning_content is not None:
                            if first_reasoning_content_output:
                                print("思考过程:")
                                first_reasoning_content_output = False
                            print(reasoning_content, end='', flush=True)
                        
                        if content is not None:
                            if first_content_output:
                                print("\n\n==============================\n回答:")
                                first_content_output = False
                            print(content, end='', flush=True)
                            assistant_response += content

                except json.JSONDecodeError as e:
                    print(f"JSON解码错误: {e}", flush=True)
        
        # 如果需要生成图片
        if should_generate_image:
            print("\n\n正在根据回答生成相关图片...")
            generate_image(image_prompt)
    else:
        print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
    
    return assistant_response

def generate_image(prompt, size="1024x1024", n=1):
    """
    调用图像生成API
    """
    payload = {
        "model": model_image,
        "prompt": prompt,
        "n": n,
        "size": size,
        "response_format": "url"
    }
    
    headers = {
        "Authorization": "Bearer sk-jelifbfcfupdddnoqzgunzehavucvjzcpsmqmwoirqbacehl",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url_image, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = re.sub(r'[\\/:*?"<>|]', '_', prompt)[:50]
            
            save_dir = "generated_images"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            for i, image_data in enumerate(result.get("data", [])):
                image_url = image_data.get("url")
                if image_url:
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        filename = f"{timestamp}_{safe_prompt}_{i+1}.png"
                        filepath = os.path.join(save_dir, filename)
                        image = Image.open(io.BytesIO(img_response.content))
                        image.save(filepath)
                        print(f"图片已保存为: {filename}")
                    else:
                        print(f"图片下载失败: {img_response.status_code}")
        else:
            print(f"图片生成失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"图片生成出错: {str(e)}")

def process_command(user_input):
    """
    处理用户命令，判断是否需要生成图片
    """
    if user_input.startswith("/draw "):
        prompt = user_input[6:].strip()
        print(f"\n正在生成图片，提示词: {prompt}")
        generate_image(prompt)
        return True
    return False

# 修改主对话循环
print("欢迎使用DeepSeek AI多模态对话系统！")
print("支持的命令：")
print("1. /draw [提示词] - 直接生成图片")
print("2. 输入问题 - 进行对话，如果回答中包含画图相关描述，将自动生成图片")
print("3. 输入'退出'结束对话")

while True:
    user_input = input("\n\n请输入您的问题或命令: ")
    if user_input.lower() in ['退出', 'quit', 'exit']:
        print("感谢使用，再见！")
        break
    
    # 检查是否是直接绘图命令
    if process_command(user_input):
        continue
    
    # 普通对话流程
    messages.append({"role": "user", "content": user_input})
    assistant_response = chat_with_api(messages)
    messages.append({"role": "assistant", "content": assistant_response})