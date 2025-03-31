import requests
import json

def chat_with_model(question):
    url = "http://10.83.1.5:8090/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [
            {"role": "system", "content": "你是一个乐于助人的AI助手。"},
            {"role": "user", "content": question}
        ],
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"请求出错: {str(e)}"

def main():
    print("欢迎使用AI助手，输入'退出'结束对话")
    
    while True:
        question = input("\n请输入您的问题: ").strip()
        
        if question.lower() in ['退出', 'quit', 'exit']:
            print("感谢使用，再见！")
            break
            
        if not question:
            continue
            
        answer = chat_with_model(question)
        print("\nAI助手:", answer)

if __name__ == "__main__":
    main()