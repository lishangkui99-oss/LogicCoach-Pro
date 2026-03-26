import json
import os
import subprocess

import requests
from openai import OpenAI

ENABLE_WEB_RAG = os.getenv("ENABLE_WEB_RAG", "false").lower() in {"1", "true", "yes", "on"}


def apply_intent_rag_routing(intent_label: str, segments: list, *, max_queries_per_segment: int = 4) -> list:
    """Apply broad-category routing hints to segment queries by interview intent."""
    if not isinstance(segments, list) or not segments:
        return []

    label = (intent_label or "").strip()
    if label not in {"产品专业面", "AI技术面"}:
        return segments

    if label == "产品专业面":
        route_seeds = [
            "需求分析框架",
            "用户生命周期与增长",
            "敏捷迭代与优先级",
            "商业模式闭环与指标体系",
        ]
    else:
        route_seeds = [
            "大模型能力边界",
            "Prompt工程策略",
            "意图识别与路由逻辑",
            "Agent架构与生成内容评估",
        ]

    routed_segments = []
    for seg in segments:
        if not isinstance(seg, dict):
            continue

        topic = (seg.get("topic") or "").strip()
        original_queries = seg.get("rag_queries", []) or []
        merged_queries = []
        seen = set()

        for q in original_queries:
            if isinstance(q, str) and q.strip():
                clean = q.strip()
                if clean not in seen:
                    seen.add(clean)
                    merged_queries.append(clean)

        for seed in route_seeds:
            enhanced = f"{topic} {seed}".strip() if topic else seed
            if enhanced not in seen:
                seen.add(enhanced)
                merged_queries.append(enhanced)
            if len(merged_queries) >= max_queries_per_segment:
                break

        routed = dict(seg)
        routed["rag_queries"] = merged_queries[:max_queries_per_segment]
        routed_segments.append(routed)

    return routed_segments


def call_agent_browser_skill(query: str) -> str:
    """Use agent-browser CLI to fetch web content for missing knowledge."""
    if not ENABLE_WEB_RAG:
        print("[rag_pipeline] Web RAG disabled by ENABLE_WEB_RAG.")
        return ""

    print(f"[rag_pipeline] Browser search: {query}")
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"

    try:
        subprocess.run(
            ["npx", "agent-browser", "open", search_url],
            capture_output=True,
            text=True,
            timeout=30,
            shell=True,
        )
        subprocess.run(
            ["npx", "agent-browser", "wait", "--load", "networkidle"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=True,
        )

        snap = subprocess.run(
            ["npx", "agent-browser", "snapshot", "-i", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=True,
        )
        snapshot_data = json.loads(snap.stdout) if snap.stdout.strip() else {}

        first_link_ref = None
        refs = snapshot_data.get("data", {}).get("refs", {})
        for ref_id, ref_info in refs.items():
            if ref_info.get("role") == "link" and ref_info.get("name", "").strip():
                name = ref_info["name"].lower()
                if "google" not in name and "sign" not in name and len(ref_info["name"]) > 5:
                    first_link_ref = f"@{ref_id}"
                    break

        if not first_link_ref:
            body_text = subprocess.run(
                ["npx", "agent-browser", "get", "text", "body"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
            )
            subprocess.run(
                ["npx", "agent-browser", "close"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
            )
            return body_text.stdout.strip()[:1500] if body_text.stdout.strip() else ""

        subprocess.run(
            ["npx", "agent-browser", "click", first_link_ref],
            capture_output=True,
            text=True,
            timeout=15,
            shell=True,
        )
        subprocess.run(
            ["npx", "agent-browser", "wait", "--load", "networkidle"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=True,
        )

        result = subprocess.run(
            ["npx", "agent-browser", "get", "text", "body"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True,
        )
        page_text = result.stdout.strip()

        subprocess.run(
            ["npx", "agent-browser", "close"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True,
        )

        return page_text[:2000] if page_text else ""

    except subprocess.TimeoutExpired:
        print("[rag_pipeline] Browser timed out.")
        subprocess.run(["npx", "agent-browser", "close"], capture_output=True, text=True, timeout=5, shell=True)
        return ""
    except Exception as e:
        print(f"[rag_pipeline] Browser fetch failed: {e}")
        subprocess.run(["npx", "agent-browser", "close"], capture_output=True, text=True, timeout=5, shell=True)
        return ""


def agentic_rag_search(ai_client: OpenAI, chat_model: str, queries: list, knowledge_collection) -> str:
    """Retrieve, reflect and optionally route to web search for missing local knowledge."""
    if not queries:
        return ""

    raw_docs = []
    if knowledge_collection:
        for q in queries:
            try:
                results = knowledge_collection.query(query_texts=[q], n_results=2)
                if results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        source = results["metadatas"][0][i].get("source", "本地知识库")
                        raw_docs.append(f"[来源: {source}] 内容: {doc[:300]}")
            except Exception as e:
                print(f"[rag_pipeline] Vector query failed: {e}")

    raw_docs = list(set(raw_docs))
    docs_str = "\n\n".join(raw_docs) if raw_docs else "本地知识库未找到任何相关文档。"
    query_str = "、".join(queries)

    system_prompt = f"""
    你是一个严谨的知识库审核与提炼引擎。
    你需要评估下方【本地检索到的文档】是否能解答或指导【目标问题】。

    【目标问题】: {query_str}

    【检索到的文档】:
    {docs_str}

    任务与要求：
    1. 评估：判断文档内容是否与目标问题实质相关。
    2. 提纯：如果相关，请提取出最有用的干货。
    3. 拦截：如果文档内容与问题无关、答非所问，或者根本没有文档，请直接、仅输出：\"NO_LOCAL_INFO\"。
    """

    try:
        response = ai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请执行反思与提炼任务。"},
            ],
            temperature=0.0,
        )
        filtered_result = response.choices[0].message.content.strip()

        if "NO_LOCAL_INFO" in filtered_result or not filtered_result:
            main_query = queries[0] if queries else "最新大厂面试要求"
            browser_content = call_agent_browser_skill(main_query)
            if browser_content:
                return f"[外部全网抓取最新资料]:\n{browser_content[:1500]}..."
            return ""

        return f"[本地知识库权威参考]:\n{filtered_result}"
    except Exception as e:
        print(f"[rag_pipeline] Reflection routing failed: {e}")
        return ""


def retrieve_local_docs_for_segments(
    segments: list,
    knowledge_collection,
    *,
    per_query_results: int = 1,
    max_queries_per_segment: int = 2,
    max_docs_per_segment: int = 4,
    snippet_chars: int = 180,
) -> dict:
    """Aggregate local vector retrieval results by segment."""
    out_segments = []
    if not segments:
        return {"segments": []}

    for seg in segments:
        seg_id = seg.get("id")
        topic = seg.get("topic", "")
        queries = seg.get("rag_queries", []) or []
        queries = [q for q in queries if isinstance(q, str) and q.strip()][:max_queries_per_segment]

        docs = []
        seen = set()

        if knowledge_collection and queries:
            for q in queries:
                try:
                    results = knowledge_collection.query(query_texts=[q], n_results=per_query_results)
                    if not results.get("documents") or not results["documents"][0]:
                        continue

                    metadatas = (results.get("metadatas") or [[]])[0]
                    for i, doc in enumerate(results["documents"][0]):
                        if not isinstance(doc, str) or not doc.strip():
                            continue
                        source = "本地知识库"
                        if i < len(metadatas) and isinstance(metadatas[i], dict):
                            source = metadatas[i].get("source", source)
                        snippet = doc.strip().replace("\n", " ")
                        snippet = snippet[:snippet_chars]
                        key = (source, snippet)
                        if key in seen:
                            continue
                        seen.add(key)
                        docs.append({"source": source, "snippet": snippet})
                        if len(docs) >= max_docs_per_segment:
                            break
                    if len(docs) >= max_docs_per_segment:
                        break
                except Exception as e:
                    print(f"[rag_pipeline] batch retrieve error segment={seg_id}, q={q}: {e}")

        out_segments.append({"id": seg_id, "topic": topic, "queries": queries, "docs": docs})

    return {"segments": out_segments}


def reflect_distill_batch(ai_client: OpenAI, chat_model: str, segment_docs: dict) -> dict:
    """Single-call reflection and distillation over all segment docs."""
    segments = segment_docs.get("segments", []) if isinstance(segment_docs, dict) else []
    if not segments:
        return {"global_distilled": "", "segments": []}

    payload = []
    for seg in segments:
        payload.append(
            {
                "id": seg.get("id"),
                "topic": seg.get("topic", ""),
                "queries": seg.get("queries", []) or [],
                "docs": seg.get("docs", []) or [],
            }
        )

    system_prompt = """
你是一个严谨的“知识库审核与提炼引擎”。你将收到多个面试切片的检索 queries 和候选文档片段（含来源）。

你的任务是：对每个切片分别判断这些文档是否能有效支撑该切片的分析，并提炼为可直接注入系统Prompt的“干货上下文”。

规则：
1) 对每个切片，若候选 docs 与 queries 实质相关：status="local"，distilled 输出 3-6 条要点（中文，信息密度高，避免废话）。
2) 若 docs 为空或明显无关：status="no_local"，distilled 置空字符串，并给出 missing_queries（1-3 个更具体的检索词）。
3) used_sources：列出你实际引用的 source（去重）；no_local 时可为空数组。
4) global_distilled：把所有切片里有价值的 distilled 合并成一段短上下文（<= 800 中文字符），用于“知识储备”章节；若没有则输出空字符串。

必须输出严格 JSON（不要 Markdown/不要额外字段），格式：
{
  "global_distilled": "...",
  "segments": [
    {"id": 1, "status": "local", "distilled": "...", "missing_queries": [], "used_sources": ["a.pdf"]},
    {"id": 2, "status": "no_local", "distilled": "", "missing_queries": ["..."], "used_sources": []}
  ]
}
""".strip()

    try:
        response = ai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps({"segments": payload}, ensure_ascii=False)},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[rag_pipeline] Batch reflection failed: {e}")
        fallback_segments = []
        for seg in payload:
            fallback_segments.append(
                {
                    "id": seg.get("id"),
                    "status": "no_local",
                    "distilled": "",
                    "missing_queries": (seg.get("queries") or [])[:2],
                    "used_sources": [],
                }
            )
        return {"global_distilled": "", "segments": fallback_segments}


def integrate_web_batch(ai_client: OpenAI, chat_model: str, batch_result: dict, web_text: str) -> dict:
    """Integrate web text into no_local segments with one LLM call."""
    if not batch_result or not isinstance(batch_result, dict):
        return batch_result
    if not web_text or not isinstance(web_text, str) or len(web_text.strip()) < 50:
        return batch_result

    system_prompt = """
你是“联网资料整合器”。你将收到：
1) 批量反思的 JSON 结果（包含 segments）
2) 一段联网抓取到的网页正文（可能很长）

任务：
- 仅针对 status="no_local" 的 segments，基于 web_text 生成 distilled（3-6 条要点，中文，高信息密度）。
- 尽量贴合该 segment 的 missing_queries/原 queries 语义，不要编造无法从 web_text 推断的事实。
- 对 status="local" 的 segments 保持不变。
- global_distilled：在原 global_distilled 基础上补充 200-400 字以内的“外部资料增量”，合并后仍 <= 1000 中文字符。

输出必须是严格 JSON，结构与输入 batch_result 相同（字段：global_distilled, segments[].id/status/distilled/missing_queries/used_sources）。
其中：对被填充的 no_local segment，把 status 改为 \"web\"，used_sources 设为 [\"web\"]。
""".strip()

    try:
        response = ai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps({"batch_result": batch_result, "web_text": web_text[:4000]}, ensure_ascii=False),
                },
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[rag_pipeline] Web integration failed: {e}")
        return batch_result
