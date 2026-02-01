import os
from openai import OpenAI

# ================= 配置区域 (在此处切换模型) =================

# 🏆 选手 1: DeepSeek-V3 (推荐首选，逻辑强，硅基流动提供)
API_KEY = "sk-remddviayxzphvfqnwrukkwyvvyvrobxnpicetaoczztxttb"
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# 🧪 选手 2: QwQ-32B (推理特化，硅基流动提供)
# API_KEY = "你的_硅基流动_KEY_sk-xxxxxx"
# BASE_URL = "https://api.siliconflow.cn/v1"
# MODEL_NAME = "Qwen/QwQ-32B" 

# ⚡ 选手 3: Gemini 1.5 Flash (Google免费版，注意需要梯子)
# API_KEY = "你的_GOOGLE_AI_STUDIO_KEY"
# BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# MODEL_NAME = "gemini-1.5-flash"

# 💰 选手 4: GPT-4o-mini (OpenAI官方，需付费)
#API_KEY = "你的_OPENAI_KEY_sk-xxxxxx"
#BASE_URL = "https://api.openai.com/v1"
#MODEL_NAME = "gpt-4o-mini"

# ==========================================================

def test_model():
    print(f"🤖 正在呼叫模型: {MODEL_NAME} ...")
    
    # 初始化客户端
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个严厉的面试官。"},
                {"role": "user", "content": "我没有什么项目经验，怎么回答‘你的优势是什么’？请简短回答。"}
            ],
            temperature=0.7,
            stream=True  # 开启流式输出，体验像打字机一样
        )

        print("\n💬 模型回答:")
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n\n✅ 测试成功！")

    except Exception as e:
        print(f"\n❌ 出错了: {e}")

if __name__ == "__main__":
    # 简单的安全检查
    if "你的" in API_KEY:
        print("⚠️ 请先在代码中填入真正的 API Key！")
    else:
        test_model()