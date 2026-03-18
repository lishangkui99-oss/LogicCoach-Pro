# LogicCoach Pro - 招聘方速览

## 项目定位
LogicCoach Pro 是一个面向产品经理面试复盘的 AI Agent 系统，核心目标是把“主观面试感觉”转化为“可解释、可量化、可追踪”的能力评估结果。

## 解决的真实问题
- 通用大模型反馈过于笼统，难以指导下一次面试改进。
- 候选人难以定位失分点，不知道是业务认知、产品方法还是表达结构问题。
- 面试复盘结果不可量化，无法做长期成长追踪。

## 当前已落地能力
- 音频转写：使用 SenseVoiceSmall 完成面试录音识别。
- 双模型协同：
  - Scout（DeepSeek-V3）负责侦察、切片与重点批注。
  - Coach（Qwen3.5-122B）负责最终深度分析与评分输出。
- Agentic RAG：
  - 本地知识库检索（ChromaDB）。
  - 批量反思整合与缺口补全。
  - 可选联网补充检索（开关控制）。
- 结构化输出：总分、7维能力评分、逐字稿问题标注、改进建议。
- 健康与运维：提供 /healthz 健康检查和 self_test.py 一键自检脚本。

## 技术亮点
- 将“长提示词 + RAG + 双模型流水线”组合为稳定可运行的后端服务。
- 通过模块化拆分（document_processing / rag_pipeline / scout_coach）降低主流程耦合。
- 在真实工程环境中处理了文档解析降级、知识库连接、联网开关与服务可观测性问题。

## 工程栈
- Backend: Python, FastAPI, Uvicorn
- LLM Gateway: OpenAI compatible API (SiliconFlow)
- Models: DeepSeek-V3, Qwen3.5-122B, SenseVoiceSmall
- RAG: ChromaDB + SentenceTransformer embeddings
- Frontend: HTML + React/Vite

## 运行与验证
- 启动后端：
  - uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
- 健康检查：
  - GET http://127.0.0.1:8000/healthz
- 环境自检：
  - python backend/scripts/self_test.py

## 候选人能力侧证明点
- 具备 AI 原生产品的架构抽象能力（从单模型到分层多智能体协同）。
- 具备后端工程落地能力（模块化、可观测性、容错与运维脚本）。
- 具备“问题诊断 -> 方案落地 -> 线上验证”的完整闭环能力。
