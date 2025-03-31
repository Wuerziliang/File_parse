from sglang import function, system, user, assistant, gen, set_default_backend, RuntimeEndpoint

@function
def chat_with_model(question):
    # 初始化对话
    s = system("你是一个乐于助人的AI助手。")
    s += user(question)
    s += assistant(gen("answer", max_tokens=4096))
    return s

# 设置模型后端地址
set_default_backend(RuntimeEndpoint("http://10.83.1.5:8090"))

def main():
    print("欢迎使用AI助手，输入'退出'结束对话")
    
    while True:
        # 获取用户输入
        question = input("\n请输入您的问题: ").strip()
        
        # 检查是否退出
        if question.lower() in ['退出', 'quit', 'exit']:
            print("感谢使用，再见！")
            break
            
        # 如果输入为空，继续下一轮
        if not question:
            continue
            
        # 运行对话
        state = chat_with_model.run(question=question)
        
        # 打印AI回答
        print("\nAI助手:", state["answer"])

if __name__ == "__main__":
    main()