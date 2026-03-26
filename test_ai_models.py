"""
LogicCoach 全链路测试工具
模拟前端完整流程: 音频上传 → ASR识别 → RAG检索 → 大模型分析 → JSON输出

用法:
  1. 先启动后端: uvicorn main:app --host 0.0.0.0 --port 8000
  2. 运行本脚本: python test_ai_models.py
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv("API_KEY", "")
BASE_URL = "https://api.siliconflow.cn/v1"
ASR_MODEL = "FunAudioLLM/SenseVoiceSmall"
CHAT_MODEL = "deepseek-ai/DeepSeek-V3"
SERVER_URL = "http://localhost:8000"


def print_separator(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")


# ==========================================
# 测试 1: API 连通性快速检查
# ==========================================
def test_api_connectivity():
    """仅测试 SiliconFlow API 是否可达"""
    print_separator("测试 1: API 连通性检查")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    print(f"🔌 正在连接 {BASE_URL} ...")
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": "你好，请用一句话回复确认连通。"}],
            max_tokens=50,
        )
        reply = response.choices[0].message.content.strip()
        print(f"✅ 大模型连通成功！回复: {reply}")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


# ==========================================
# 测试 2: ASR 语音识别 (单独测试)
# ==========================================
def test_asr(audio_path):
    """单独测试 SiliconFlow SenseVoice ASR，与 main.py 同一模型"""
    print_separator("测试 2: ASR 语音识别 (SenseVoice)")
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None

    file_size = os.path.getsize(audio_path) / 1024
    print(f"🎙️ 文件: {audio_path} ({file_size:.1f} KB)")
    print(f"🔄 正在调用 {ASR_MODEL} ...")

    start = time.time()
    try:
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(model=ASR_MODEL, file=f)
        elapsed = time.time() - start
        text = transcription.text
        print(f"✅ 识别完成！耗时 {elapsed:.1f}s，文本长度 {len(text)} 字")
        print(f"📝 识别结果:\n{text}")
        return text
    except Exception as e:
        print(f"❌ ASR 失败: {e}")
        return None


# ==========================================
# 测试 3: 全链路 E2E (模拟前端调 /analyze_audio)
# ==========================================
def test_full_pipeline(audio_path, jd_text=None, resume_text=None,
                       jd_file_path=None, resume_file_path=None):
    """
    模拟前端上传行为，POST 到后端 /analyze_audio 接口。
    这是最关键的测试——走的是和前端完全一样的链路。
    """
    print_separator("测试 3: 全链路 E2E (前端 → 后端)")

    url = f"{SERVER_URL}/analyze_audio"

    # 先检查后端是否在运行
    print(f"🔌 检查后端服务 {SERVER_URL} ...")
    try:
        requests.get(SERVER_URL, timeout=3)
        print("✅ 后端服务在线")
    except requests.ConnectionError:
        print(f"❌ 无法连接到 {SERVER_URL}")
        print("   请先启动后端: uvicorn main:app --host 0.0.0.0 --port 8000")
        return None

    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None

    # 构建 multipart/form-data 请求 (与前端 FormData 完全一致)
    files = {
        "file": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/wav"),
    }

    if resume_file_path and os.path.exists(resume_file_path):
        files["resume_file"] = (
            os.path.basename(resume_file_path),
            open(resume_file_path, "rb"),
            "application/pdf",
        )
        print(f"📄 附带简历 PDF: {resume_file_path}")

    if jd_file_path and os.path.exists(jd_file_path):
        files["jd_file"] = (
            os.path.basename(jd_file_path),
            open(jd_file_path, "rb"),
            "application/pdf",
        )
        print(f"📄 附带 JD PDF: {jd_file_path}")

    data = {}
    if jd_text:
        data["jd_text"] = jd_text
        print(f"📋 附带 JD 文本 ({len(jd_text)} 字)")
    if resume_text:
        data["resume_text"] = resume_text
        print(f"📋 附带简历文本 ({len(resume_text)} 字)")

    file_size = os.path.getsize(audio_path) / 1024
    print(f"🎙️ 上传音频: {audio_path} ({file_size:.1f} KB)")
    print(f"🚀 POST {url}  (全链路: ASR → RAG → DeepSeek → JSON)")
    print("⏳ 请耐心等待，全流程可能需要 30-120 秒...\n")

    start = time.time()
    try:
        response = requests.post(url, files=files, data=data, timeout=300)
        elapsed = time.time() - start
    except requests.Timeout:
        print("❌ 请求超时 (>300s)，后端可能卡住了")
        return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None
    finally:
        for f_tuple in files.values():
            f_tuple[1].close()

    print(f"📡 响应状态码: {response.status_code}  耗时: {elapsed:.1f}s\n")

    if response.status_code != 200:
        print(f"❌ 服务端错误:\n{response.text}")
        return None

    result = response.json()
    display_analysis_result(result)
    return result


def display_analysis_result(result):
    """格式化展示后端返回的完整分析结果"""
    status = result.get("status")
    if status != "success":
        print(f"❌ 分析失败: {result.get('message', '未知错误')}")
        return

    transcription = result.get("transcription", "")
    analysis = result.get("ai_analysis", {})

    print("─" * 50)
    print("📝 语音识别结果:")
    print("─" * 50)
    print(transcription)

    print(f"\n{'─'*50}")
    print("🎯 AI 分析报告:")
    print("─" * 50)

    score = analysis.get("total_score", "N/A")
    level = analysis.get("level_assessment", "N/A")
    print(f"\n  总分: {score}/100")
    print(f"  定级: {level}")

    dims = analysis.get("dimensions", {})
    if dims:
        print(f"\n  七维能力雷达:")
        for dim_name, dim_score in dims.items():
            bar = "█" * (dim_score // 5) + "░" * (20 - dim_score // 5)
            print(f"    {dim_name:　<5} {bar} {dim_score}")

    corrections = analysis.get("transcript_correction", [])
    if corrections:
        print(f"\n  逐字稿标注 ({len(corrections)} 处):")
        for i, c in enumerate(corrections, 1):
            icon = "🔴" if c.get("type") == "critical" else "🟡"
            print(f"    {icon} [{c.get('type', '?').upper()}] \"{c.get('quote', '')[:60]}...\"")
            print(f"       → {c.get('reason', '')[:100]}...")

    suggestions = analysis.get("improvement_suggestions", [])
    if suggestions:
        print(f"\n  改进建议 ({len(suggestions)} 条):")
        for s in suggestions:
            print(f"    {s[:120]}")

    print(f"\n{'─'*50}")
    print("✅ 全链路测试完成！")

    # 保存完整 JSON 到文件，方便前端联调
    output_path = os.path.join("uploads", "last_test_result.json")
    os.makedirs("uploads", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 完整 JSON 已保存: {output_path}")


# ==========================================
# 主入口：交互式菜单
# ==========================================
if __name__ == "__main__":
    if not API_KEY:
        print("⚠️ 未找到 API_KEY，请检查 .env 文件！")
        sys.exit(1)

    print_separator("LogicCoach 全链路测试工具 v2.0")
    print("选择测试模式:\n")
    print("  1. API 连通性检查        (无需音频/无需后端)")
    print("  2. ASR 识别测试           (无需后端，直接调 SiliconFlow)")
    print("  3. 🔥 全链路 E2E 测试     (模拟前端，需要后端运行中)")
    print("  4. 全链路 + JD/简历上下文  (完整生产场景)")
    print()

    choice = input("请输入选项 (1/2/3/4): ").strip()

    if choice == "1":
        test_api_connectivity()

    elif choice == "2":
        path = input("音频文件路径 (回车使用默认 uploads/input.wav): ").strip()
        if not path:
            path = "uploads/input.wav"
        test_asr(path)

    elif choice == "3":
        path = input("音频文件路径 (回车使用默认 uploads/input.wav): ").strip()
        if not path:
            path = "uploads/input.wav"
        test_full_pipeline(path)

    elif choice == "4":
        path = input("音频文件路径 (回车使用默认 uploads/input.wav): ").strip()
        if not path:
            path = "uploads/input.wav"

        print("\n[可选] 提供额外上下文以获得更精准的分析:")
        jd = input("JD 文本 (直接粘贴或回车跳过): ").strip() or None
        resume = input("简历文本 (直接粘贴或回车跳过): ").strip() or None
        jd_pdf = input("JD PDF 路径 (回车跳过): ").strip() or None
        resume_pdf = input("简历 PDF 路径 (回车跳过): ").strip() or None

        test_full_pipeline(
            path,
            jd_text=jd,
            resume_text=resume,
            jd_file_path=jd_pdf,
            resume_file_path=resume_pdf,
        )

    else:
        print("无效选项，退出。")
