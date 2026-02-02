import os
import shutil
import json
import io
import pdfplumber  # 👈 新增：PDF 解析神器
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

# ================= 配置区域 =================
API_KEY = os.getenv("API_KEY") 
if not API_KEY:
    print("⚠️ 警告: 未找到 API_KEY，请检查 .env 文件！")

BASE_URL = "https://api.siliconflow.cn/v1"
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"
ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
DB_PATH = "chroma_db"
# ===========================================

app = FastAPI(title="LogicCoach RAG API", version="2.3.0") # 版本号升级

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 知识库初始化 ---
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

# 前端目录定位
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# --- 🛠️ 新增工具函数：PDF 转文字 ---
def extract_pdf_content(file_bytes: bytes) -> str:
    """接收文件二进制流，使用 pdfplumber 提取纯文本"""
    text_content = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        return text_content
    except Exception as e:
        print(f"❌ PDF 解析失败: {e}")
        return ""

@app.post("/analyze_audio")
async def analyze_audio(
    file: UploadFile = File(...),         # 必须：录音文件
    jd_text: str = Form(None),            # 可选：粘贴的 JD 文本
    resume_text: str = Form(None),        # 可选：粘贴的简历文本
    # 👇 新增：支持直接上传 PDF 文件
    resume_file: UploadFile = File(None), 
    jd_file: UploadFile = File(None)      
):
    if not client:
        return {"status": "error", "message": "API Key 未配置"}

    # --- Step 0: 处理 PDF 上传 (如果有) ---
    # 逻辑：如果上传了 PDF，就把它解析出来的文字追加到 text 变量里
    
    # 处理简历 PDF
    if resume_file:
        print(f"📂 正在解析简历 PDF: {resume_file.filename}...")
        pdf_bytes = await resume_file.read()
        pdf_text = extract_pdf_content(pdf_bytes)
        if pdf_text:
            # 如果之前有粘贴文本，换行追加；否则直接赋值
            resume_text = (resume_text or "") + f"\n\n[简历PDF附件内容]:\n{pdf_text}"
            print("✅ 简历 PDF 解析完成")

    # 处理 JD PDF
    if jd_file:
        print(f"📂 正在解析 JD PDF: {jd_file.filename}...")
        pdf_bytes = await jd_file.read()
        pdf_text = extract_pdf_content(pdf_bytes)
        if pdf_text:
            jd_text = (jd_text or "") + f"\n\n[JD PDF附件内容]:\n{pdf_text}"
            print("✅ JD PDF 解析完成")

    # --- Step 1: 保存音频 ---
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        file.seek(0) # 确保从头读取
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

    # --- Step 3.5: 构建上下文 (现在包含了 PDF 的内容) ---
    job_context = ""
    if jd_text and len(jd_text) > 5:
        job_context += f"\n【目标职位JD】:\n{jd_text}\n"
    
    real_resume_context = ""
    if resume_text and len(resume_text) > 5:
        real_resume_context += f"\n【候选人简历背景】:\n{resume_text}\n"

    # --- Step 4: 构建 Prompt (Link 知识助理 V2.0 - 增强版) ---
    system_prompt = f"""
    # Role
    你是由李尚奎训练的“Link知识助理”，一位拥有丰富实战经验的资深产品经理面试官（P9级别）。
    你的核心能力背靠“李尚奎的个人知识库”和“哇哦产品播客”。
    
    # Context (知识库)
    {retrieved_context}
    
    # Interview Context (JD & 简历)
    {job_context}
    {real_resume_context}

    # Task: 逐字稿分析与纠错
    你收到的 `user_text` 可能是一段包含面试官提问和候选人回答的对话，也可能只是候选人的独白。
    1. **智能聚焦**：请忽略面试官的提问，**只针对【候选人】的回答表现进行评分和纠错**。
    2. **微观纠错**：寻找逻辑漏洞、废话堆砌、或使用了“赋能/闭环”等黑话但无实证的片段。

    # Critical Rule for Highlights (绝对重要!!)
    在输出 `transcript_correction` 的 `quote` 字段时，**必须直接复制 `user_text` 中的原始字符串，严禁任何修改！**

    # Output Format (JSON ONLY - Strict)
    你必须输出符合以下结构的 JSON，**不要包含 markdown 标记**：
    {{
      "total_score": <0-100的整数>,
      "level_assessment": "<简短评级，如：P6-资深产品经理 / P7-专家>",
      "dimensions": {{
        "业务感": <int>, "产品力": <int>, "逻辑思维": <int>, 
        "沟通能力": <int>, "项目管理": <int>, "抗压能力": <int>, "软技能": <int>
      }},
      "transcript_correction": [
        {{
            "quote": "<必须完全等于原文的片段>",
            "type": "critical", 
            "reason": "<犀利点评>"
        }},
        {{
            "quote": "<必须完全等于原文的片段>",
            "type": "warning",
            "reason": "<改进建议>"
        }}
      ],
      "improvement_suggestions": [
        "🔥 [致命追问]: <基于回答生成一个极度具体的业务追问>",
        "💡 [知识库引用]: <引用相关方法论>",
        "✨ [优化建议]: <具体的修改方向>"
      ]
    }}
    """

    # --- Step 5: 呼叫 AI (参数已调优) ---
    print("🤖 [4/4] DeepSeek 正在思考...")
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.4,
            top_p=1,
            presence_penalty=0.5,
            frequency_penalty=1,
            response_format={ "type": "json_object" }
        )
        ai_result = json.loads(response.choices[0].message.content)
        print("✅ 分析完成")
    except Exception as e:
        print(f"❌ AI 分析出错: {e}")
        ai_result = {
            "total_score": 0, 
            "level_assessment": "Error",
            "dimensions": {}, 
            "transcript_correction": [],
            "improvement_suggestions": [f"分析服务暂时不可用: {str(e)}"]
        }

    return {
        "status": "success",
        "transcription": user_text,
        "ai_analysis": ai_result
    }

# 挂载前端页面
@app.get("/")
async def read_index():
    if os.path.exists(os.path.join(FRONTEND_DIR, "app.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "app.html"))
    return {"error": "Frontend not found"}

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")