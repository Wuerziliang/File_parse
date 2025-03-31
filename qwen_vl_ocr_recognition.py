import os
import dashscope
import base64
from dashscope import MultiModalConversation


# 从环境变量获取API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', '')
if not dashscope.api_key:
    raise ValueError("请设置DASHSCOPE_API_KEY环境变量")


def perform_ocr(image_path):
    try:
        # 读取本地图片并转换为 Base64 编码
        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 创建 MultiModalConversation 实例
        response = MultiModalConversation.call(
            model='qwen-vl-ocr',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'image': f'data:image/jpeg;base64,{encoded_image}'
                        }
                    ]
                }
            ]
        )

        if response.status_code == 200:
            # 仅提取识别文本内容
            result_text = response.output.choices[0].message.content
            print("识别的文本内容:")
            print(result_text)
            return result_text
        else:
            print(f"请求失败，状态码: {response.status_code}，错误信息: {response.message}")
            return None
    except Exception as e:
        print(f"发生异常: {e}")
        return None


if __name__ == "__main__":
    image_path = "C:\\Users\\19706\\Desktop\\papers\\deepseek_paper\\DeepSeek_R1\\R1文献图片\\DeepSeek_R1_02.png"
    text_result = perform_ocr(image_path)
    if text_result:
        print("OCR识别成功")
    else:
        print("OCR识别失败")


print("当前API_KEY:", os.getenv('DASHSCOPE_API_KEY'))
    