import json

from openai import OpenAI


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
