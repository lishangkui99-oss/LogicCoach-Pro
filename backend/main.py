import os
import shutil
import json
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, UploadFile, File, Form # 👈 新增了 Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# ================= 配置区域 =================
API_KEY = "sk-remddviayxzphvfqnwrukkwyvvyvrobxnpicetaoczztxttb" # 👈 记得换回你的 Key
BASE_URL = "https://api.siliconflow.cn/v1"

CHAT_MODEL = "deepseek-ai/DeepSeek-V3"
ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
DB_PATH = "chroma_db"
# ===========================================

app = FastAPI(title="LogicCoach RAG API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化知识库
print("📚 正在连接本地知识库...")
try:
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    db_client = chromadb.PersistentClient(path=DB_PATH)
    knowledge_collection = db_client.get_collection(
        name="product_manager_knowledge",
        embedding_function=emb_fn
    )
    print("✅ 知识库连接成功！")
except Exception as e:
    print(f"⚠️ 知识库连接失败: {e}")
    knowledge_collection = None

@app.post("/analyze_audio")
async def analyze_audio(
    file: UploadFile = File(...),
    jd_text: str = Form(None),      # 👈 新增：接收职位描述
    resume_text: str = Form(None)   # 👈 新增：接收简历内容
):
    # --- Step 1: 保存音频 ---
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"🎧 [1/4] 收到文件，正在听写...")

    # --- Step 2: 语音转文字 ---
    try:
        audio_file = open(file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model=ASR_MODEL,
            file=audio_file
        )
        user_text = transcription.text
        print(f"📝 [2/4] 识别内容: {user_text}")
    except Exception as e:
        return {"status": "error", "message": f"听写失败: {str(e)}"}

    # --- Step 3: RAG 检索 ---
    retrieved_context = ""
    if knowledge_collection:
        print(f"🔍 [3/4] 正在检索知识库...")
        try:
            results = knowledge_collection.query(query_texts=[user_text], n_results=3)
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    source = results['metadatas'][0][i].get('source', '未知')
                    retrieved_context += f"\n[参考资料-{source}]:\n{doc[:500]}...\n"
        except Exception as e:
            print(f"检索出错: {e}")

    # --- Step 3.5: 构建背景信息 (JD & Resume) ---
    job_context = ""
    if jd_text and len(jd_text) > 10:
        job_context += f"\n【目标职位JD】:\n{jd_text}\n"
    
    resume_context = ""
    if resume_text and len(resume_text) > 10:
        resume_context += f"\n【候选人简历背景】:\n{resume_text}\n"

    # --- Step 4: 构建 Prompt ---
system_prompt = """
# Role
你是由 LogicCoach 开发的资深 AI 产品专家（P9级别），正在对候选人进行一场高压力的 AI 产品经理面试。
你的目标是通过深度逻辑推理（Chain of Thought），对候选人的语音回答进行“逐字稿级别的微观纠错”。

# Context (ASR Error Handling)
用户输入是【语音转文字 (STT)】的结果，可能包含同音错别字（如"闭环"识别为"壁画"，"ToB"识别为"图B"）。
**指令**：请先在思维链中自动修正这些错误，基于修正后的语意进行分析，不要纠结于由 STT 导致的字面错误。

# Evaluation Dimensions (7-Dimension Radar)
请严格基于以下 7 个维度进行 0-100 分的量化打分：
1. **Business (业务洞察)**：商业模式、市场规模、竞品分析能力。
2. **Product (产品设计)**：需求挖掘、功能定义、MVP 规划能力。
3. **Logic (逻辑思维)**：分析问题的结构化程度、归因准确性。
4. **Communication (沟通表达)**：回答是否清晰、简练、有重点。
5. **Project (项目管理)**：落地执行、风险控制、资源协调能力。
6. **Stress (抗压能力)**：面对追问和质疑时的反应（需结合上下文判断）。
7. **SoftSkills (软素质)**：同理心、领导力、价值观。

# Task: Micro-Correction (The Highlighter)
不要只给长篇大论的总结。你必须找出用户回答中具体的**逻辑漏洞**或**无效废话**，进行“红笔批改”。
批改标准：
- **逻辑跳跃**：结论缺乏论据支撑。
- **缺乏数据**：使用了"很多"、"大幅提升"等模糊词汇，而没有具体指标。
- **大词堆砌**：使用了"赋能"、"抓手"等词汇但没有落地场景。
- **偏题**：回答没有针对问题核心。

# Output Format (JSON ONLY)
为了让前端生成雷达图和高亮文本，**你必须严格输出合法的 JSON 格式**，不要包含 markdown 标记（如 ```json）。结构如下：

{
  "total_score": <0-100>,
  "dimensions": {
    "business": <score>,
    "product": <score>,
    "logic": <score>,
    "communication": <score>,
    "project": <score>,
    "stress": <score>,
    "soft_skills": <score>
  },
  "feedback_summary": "<一段简练的总评，像 P9 对下属的点评，语气犀利>",
  "annotations": [
    {
      "quote": "<用户原话片段，必须能与 transcript 模糊匹配>",
      "type": "critical",  // 或 "warning"
      "comment": "<5-10个字的简短评语，用于 Tooltip 显示，例如：缺乏数据支撑>"
    },
    {
      "quote": "<另一段原话>",
      "type": "warning",
      "comment": "<逻辑跳跃，未解释原因>"
    }
  ]
}
"""

# 3. 呼叫 AI 大脑进行分析
    print("🤖 正在请求 DeepSeek 分析...")
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt}, # 使用上面更新的 Prompt
                {"role": "user", "content": user_text}
            ],
            temperature=0.4, # 稍微调低一点，保证 JSON 格式稳定
            response_format={ "type": "json_object" } # 👈 关键！强制输出 JSON
        )
        ai_advice_json = response.choices[0].message.content
        print("✅ 分析完成")
        
        # 尝试解析一下，确保是合法 JSON (可选，为了 log 好看)
        import json
        parsed_advice = json.loads(ai_advice_json)
        
    except Exception as e:
        print(f"❌ AI 分析出错: {e}")
        # 兜底数据，防止前端白屏
        parsed_advice = {
            "total_score": 0,
            "feedback_summary": f"AI 大脑暂时短路了: {str(e)}",
            "dimensions": {},
            "annotations": []
        }

    # 4. 返回完整结果
    return {
        "filename": file.filename,
        "status": "success",
        "transcription": user_text,
        "ai_analysis": parsed_advice  # 👈 这里直接返回对象，FastAPI 会自动转 JSON
    }import os
import shutil
import json
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv  # 👈 新增：用于加载环境变量

# 加载 .env 文件
load_dotenv()

# ================= 配置区域 =================
# 🚨 重点：从环境变量获取 Key，不要写死！
API_KEY = os.getenv("API_KEY") 
if not API_KEY:
    raise ValueError("❌ 错误：未找到 API_KEY，请检查 .env 文件！")

BASE_URL = "https://api.siliconflow.cn/v1"
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"
ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
DB_PATH = "chroma_db"
# ===========================================

app = FastAPI(title="LogicCoach RAG API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 知识库连接
print("📚 正在连接本地知识库...")
try:
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    db_client = chromadb.PersistentClient(path=DB_PATH)
    knowledge_collection = db_client.get_collection(
        name="product_manager_knowledge",
        embedding_function=emb_fn
    )
    print("✅ 知识库连接成功！")
except Exception as e:
    print(f"⚠️ 知识库连接失败: {e}")
    knowledge_collection = None

# 前端文件路径配置
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.post("/analyze_audio")
async def analyze_audio(
    file: UploadFile = File(...),
    jd_text: str = Form(None),
    resume_text: str = Form(None)
):
    # --- Step 1: 保存音频 ---
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print(f"🎧 [1/4] 收到文件，正在听写...")

    # --- Step 2: 语音转文字 ---
    try:
        audio_file = open(file_path, "rb")
        transcription = client.audio.transcriptions.create(
            model=ASR_MODEL,
            file=audio_file
        )
        user_text = transcription.text
        print(f"📝 [2/4] 识别内容: {user_text}")
    except Exception as e:
        return {"status": "error", "message": f"听写失败: {str(e)}"}

    # --- Step 3: RAG 检索 ---
    retrieved_context = ""
    if knowledge_collection:
        print(f"🔍 [3/4] 正在检索知识库...")
        try:
            results = knowledge_collection.query(query_texts=[user_text], n_results=3)
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    source = results['metadatas'][0][i].get('source', '未知')
                    retrieved_context += f"\n[参考资料-{source}]:\n{doc[:500]}...\n"
        except Exception as e:
            print(f"检索出错: {e}")

    # --- Step 3.5: 构建背景信息 ---
    job_context = ""
    if jd_text and len(jd_text) > 10:
        job_context += f"\n【目标职位JD】:\n{jd_text}\n"
    
    resume_context = ""
    if resume_text and len(resume_text) > 10:
        resume_context += f"\n【候选人简历背景】:\n{resume_text}\n"

    # --- Step 4: 构建 Prompt ---
    system_prompt = f"""
    # Role
    你是由 LogicCoach 开发的资深 AI 产品专家（P9级别）。
    
    # Context (外部大脑)
    {retrieved_context}
    
    # Interview Context
    {job_context}
    {resume_context}

    # Task
    请对候选人的语音回答进行“逐字稿级别的微观纠错”。
    
    # Output Format (JSON ONLY)
    {{
      "total_score": <int>,
      "dimensions": {{
        "business": <int>, "product": <int>, "logic": <int>, 
        "communication": <int>, "project": <int>, "stress": <int>, "soft_skills": <int>
      }},
      "feedback_summary": "<点评>",
      "annotations": [
        {{ "quote": "<原话>", "type": "critical", "comment": "<评语>" }}
      ]
    }}
    """

    # --- Step 5: 呼叫 AI ---
    print("🤖 [4/4] DeepSeek 正在思考...")
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.4,
            response_format={ "type": "json_object" }
        )
        ai_result = json.loads(response.choices[0].message.content)
        print("✅ 分析完成")
    except Exception as e:
        print(f"❌ AI 分析出错: {e}")
        ai_result = {"total_score": 0, "feedback_summary": str(e), "dimensions": {}, "annotations": []}

    return {
        "status": "success",
        "transcription": user_text,
        "ai_analysis": ai_result
    }

# 挂载前端页面 (放在最后)
@app.get("/")
async def read_index():
    if os.path.exists(os.path.join(FRONTEND_DIR, "app.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "app.html"))
    return {"error": "Frontend not found"}

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")