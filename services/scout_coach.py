import json

from openai import OpenAI


INTENT_LABELS = ["HR通用面", "产品专业面", "AI技术面", "未识别"]


def _normalize_intent_label(raw_label: str) -> str:
    text = (raw_label or "").strip()
    if text in INTENT_LABELS:
        return text

    low = text.lower()
    if "hr" in low or "招聘" in text or "价值观" in text or "沟通" in text:
        return "HR通用面"
    if "产品" in text or "需求" in text or "生命周期" in text or "商业模式" in text:
        return "产品专业面"
    if "ai" in low or "aigc" in low or "大模型" in text or "agent" in low or "prompt" in low:
        return "AI技术面"
    return "未识别"


def scan_interview_intent(ai_client: OpenAI, scout_model: str, transcript: str) -> str:
    """Lightweight intent scanner before main coach analysis."""
    if not transcript or len(transcript.strip()) < 30:
        return "未识别"

    system_prompt = """
你是面试场景意图识别器。
只允许输出以下四个标签之一，且必须完全一致：
- HR通用面
- 产品专业面
- AI技术面
- 未识别

判定规则：
1) 软素质、沟通协作、动机价值观为主 -> HR通用面
2) 需求分析、用户生命周期、敏捷迭代、商业模式、指标体系为主 -> 产品专业面
3) 大模型边界、Prompt策略、路由逻辑、Agent架构、AIGC评估为主 -> AI技术面
4) 多意图混杂或信息不足 -> 未识别
""".strip()

    try:
        response = ai_client.chat.completions.create(
            model=scout_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript[:6000]},
            ],
            temperature=0.0,
            max_tokens=16,
        )
        label = response.choices[0].message.content.strip()
        return _normalize_intent_label(label)
    except Exception as e:
        print(f"[scout_coach] Intent scanner failed: {e}")
        return "未识别"


def build_dynamic_evaluation_criteria(intent_label: str, rag_reference: str = "") -> str:
    """Build dynamic criteria to inject into system prompt template."""
    label = _normalize_intent_label(intent_label)
    ref = (rag_reference or "").strip()
    ref_line = f"参考红线: {ref}" if ref else "参考红线: 暂无检索补充，优先依据逐字稿证据。"

    if label == "产品专业面":
        return (
            "场景: 产品专业面\n"
            "评分权重建议:\n"
            "- 主权重 65%: 用户同理心、业务落地能力、结构化表达\n"
            "- 次权重 35%: 数据指标意识、协作推进、复盘能力\n"
            "评估锚点:\n"
            "- 需求分析完整性、生命周期思维、商业闭环意识\n"
            f"- {ref_line}"
        )

    if label == "AI技术面":
        return (
            "场景: AI技术面\n"
            "评分权重建议:\n"
            "- 主权重 65%: AI场景应用能力、系统边界认知、方案取舍\n"
            "- 次权重 35%: 产品化表达、跨团队协同、风险意识\n"
            "评估锚点:\n"
            "- 大模型能力边界、Prompt策略、意图路由、Agent架构、评估标准\n"
            f"- {ref_line}"
        )

    if label == "HR通用面":
        return (
            "场景: HR通用面\n"
            "评分权重建议:\n"
            "- 主权重 60%: 沟通表达、抗压能力、软技能\n"
            "- 次权重 40%: 逻辑性、项目复盘质量\n"
            f"- {ref_line}"
        )

    return (
        "场景: 未识别\n"
        "评分权重建议:\n"
        "- 均衡权重: 逻辑/沟通/产品/业务综合评估\n"
        f"- {ref_line}"
    )


def run_scout_agent(ai_client: OpenAI, scout_model: str, transcript: str, resume_json: dict, jd_json: dict) -> dict:
    """Split transcript and extract focus points before final coach scoring."""
    if not transcript or len(transcript) < 50:
        return {"global_focus": [], "segments": []}

    resume_str = json.dumps(resume_json, ensure_ascii=False) if resume_json else "未提供简历结构化数据"
    jd_str = json.dumps(jd_json, ensure_ascii=False) if jd_json else "未提供JD结构化数据"

    system_prompt = f"""
    你是一个极其敏锐的面试复盘军师（Scout Agent）。
    你的任务不是给候选人打分，而是为接下来的“主审官”整理出一份【作战地图】。

    你需要交叉比对以下三份信息：
    1. 【岗位JD】: {jd_str}
    2. 【候选人简历】: {resume_str}
    3. 用户上传的【面试逐字稿】（包含在User输入中）

    请执行以下动作：
    1. 宏观扫描：找出简历和JD之间的核心差异，或者简历与逐字稿中回答的潜在矛盾。
    2. 逻辑切块：将长篇的面试逐字稿，按照“讨论的话题”或“问答对”切分为 3-6 个独立区块（Sub-texts）。
    3. 提取焦点：针对每个切块，指出主审官需要重点关注的破绽（Red Flags），并生成 1-2 个用于检索本地知识库的高质量关键词（RAG Queries）。

    你必须严格输出以下 JSON 格式（不要有任何 Markdown 标记或多余废话）：
    {{
      "global_focus": ["全局注意点1", "全局注意点2"],
      "segments": [
        {{
          "id": 1,
          "topic": "自我介绍与过往履历",
          "dialogue_chunk": "[逐字稿连续切片原文]",
          "scout_notes": "军师批注",
          "rag_queries": ["关键词1", "关键词2"]
        }}
      ]
    }}
    """

    try:
        response = ai_client.chat.completions.create(
            model=scout_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"以下是本次面试的逐字稿，请开始切片和侦察：\n\n{transcript}"},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[scout_coach] Scout failed: {e}")
        return {
            "global_focus": ["军师节点解析失败，请主审官全局审视。"],
            "segments": [
                {
                    "id": 1,
                    "topic": "完整面试录音",
                    "dialogue_chunk": transcript,
                    "scout_notes": "无批注",
                    "rag_queries": ["产品经理面试高频题"],
                }
            ],
        }
