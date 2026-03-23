import os
import google.generativeai as genai
import sys

# 1. 配置 API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("错误: 请先配置环境变量 GEMINI_API_KEY")
    sys.exit(1)

genai.configure(api_key=api_key)

# 2. 初始化模型 (推荐使用 gemini-1.5-flash，速度快且免费额度高)
model = genai.GenerativeModel('gemini-1.5-flash')


def start_chat():
    print("--- 已连接至 Gemini (输入 'exit' 退出) ---")
    chat = model.start_chat(history=[])

    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break

        # 使用流式传输，增加实时感
        response = chat.send_message(user_input, stream=True)
        print("Gemini: ", end="")
        for chunk in response:
            print(chunk.text, end="", flush=True)
        print()


if __name__ == "__main__":
    start_chat()