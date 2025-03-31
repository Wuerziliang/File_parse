import requests

# 服务器IP和端口
SERVER_IP = "10.83.1.5"
PORT = 8090

# 定义多轮问答函数
def multi_turn_dialogue():
    # 构造初始消息列表，包含系统提示
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."}
    ]
    url = f"http://{SERVER_IP}:{PORT}/generate"

    while True:
        question = input("请输入你的问题（输入 '退出' 结束对话）：")
        if question == "退出":
            break
        # 将用户问题添加到消息列表
        messages.append({"role": "user", "content": question})
        # 构造请求体
        payload = {
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.5
        }
        try:
            with requests.post(url, json=payload, stream=True) as r:
                r.raise_for_status()
                answer = ""
                print("回答: ", end="", flush=True)
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        chunk_text = chunk.decode("utf-8")
                        print(chunk_text, end="", flush=True)
                        answer += chunk_text
                print()
            # 将回答添加到消息列表，用于后续多轮对话
            messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.RequestException as e:
            print(f"请求失败：{e}")


if __name__ == "__main__":
    multi_turn_dialogue()
    