# LogicCoach Pro - 垂直领域的 AI 产品经理面试复盘 Agent 🤖

> **"通用大模型给的是‘建议’，LogicCoach 给的是‘判决’。"**
> 一个基于 RAG 架构、拒绝笼统废话、专注于**微观逻辑纠错**与**能力量化评估**的面试复盘助手。

![Dashboard Screenshot](这里放你的结果页截图路径.png)

## 💡 为什么做这个项目？(The "Why")

作为一名从建筑学转型 AI 产品经理的求职者，我在面试复盘中发现了两个核心痛点：

1.  **通用大模型的“失忆”与“笼统”**：
    直接把面试录音丢给 ChatGPT，它往往只能给出“逻辑清晰、表达流畅”等**万金油式的评价**。它不知道 AI 产品岗位的具体考核标准，也无法根据我过往学习过的（但可能遗忘的）具体知识点进行针对性纠错。

2.  **复盘颗粒度不够**：
    大多数人不知道自己“挂”在哪里。是**商业思维**不够？还是**技术理解**（如 RAG/Agent 原理）有偏差？

**LogicCoach Pro 的核心使命**：利用 **RAG（私有知识库）** 将通用的推理能力“锚定”在具体的 **AI 产品经理能力模型**上，把模糊的“感觉”变成精确的“红黄线”标注。

## ✨ 核心解决方案 (Core Solutions)

### 1. 🎯 7维能力雷达图 (Competency Radar)
> *解决问题：面试评价标准不透明、无法量化。*

我梳理了过往学习的 **100+ 篇 AI 产品方法论与大厂 JD**，提炼出 AI 产品经理必考的 **7 大核心素质**（如业务感、技术理解力、逻辑思维等）。
* **功能实现**：每次回答后，Agent 不会只给总分，而是基于这 7 个维度生成雷达图与强弱排序，让你一眼看出今天的回答是“由于技术理解偏差导致失分”还是“沟通结构混乱”。

### 2. 📝 基于知识库的“红黄线”精准批改 (Precision Highlighting)
> *解决问题：大模型反馈过于温和，缺乏针对性。*

利用 **DeepSeek-V3** 结合本地向量数据库（ChromaDB），对你的语音逐字稿进行微观扫描：
* **🔴 红线（Critical）**：**逻辑硬伤或知识盲区**。
    * *示例*：当你提到“大模型幻觉”却没能说出“RAG”或“微调”等具体解法时，系统会直接标红，并引用知识库中的标准答案指出缺失。
* **🟡 黄线（Warning）**：**表达缺陷或黑话堆砌**。
    * *示例*：当你空谈“赋能、闭环”却无 Case 支撑时，系统会高亮预警，提示补充数据或落地细节。
* **💡 解决方案输出**：不只是指出错误，还会根据你的失分点，直接从知识库中检索并输出对应的**改进方案**。

## 📅 产品规划 (Roadmap)

LogicCoach Pro 致力于打造面试全流程的闭环体验：

- [x] **MVP 阶段 (已完成)**：
    - [x] 支持音频/PDF简历多模态输入。
    - [x] 实现 RAG 检索与 7 维能力打分。
    - [x] 逐字稿红黄线高亮与致命追问生成。
- [ ] **2.0 阶段 (开发中)**：
    - [ ] **面试前 - 模拟沙盘**：根据上传的 JD，利用 Agent 自动生成 3 组高频模拟题（含压力面场景）。
    - [ ] **面试后 - 长期追踪**：建立用户能力成长曲线，追踪 7 维能力的长期变化趋势。

## 🛠 技术架构 (Tech Stack)

这是一个 **Full-Stack** 的 LLM 原生应用：

* **核心大脑（双模型协同）**:
  * **Scout**: DeepSeek-V3 (via SiliconFlow API) - *负责前置侦察、切片批注、RAG反思整合*
  * **Coach**: Qwen3.5-122B (via SiliconFlow API) - *负责最终深度评估与结构化评分输出*
* **知识中枢**: RAG (Retrieval-Augmented Generation) - *基于 ChromaDB 挂载 110+ 篇垂直领域干货*
* **听觉中枢**: FunAudioLLM/SenseVoiceSmall - *高精度语音转文字*
* **视觉交互**: HTML5 + TailwindCSS + Chart.js - *雷达图与交互式逐字稿渲染*
* **工程底座**: Python (FastAPI) + Uvicorn

## 🆕 最近更新 (2026-03)

- [x] Scout-Coach 双层架构：前置侦察与最终深度分析分层执行。
- [x] 批量 Agentic RAG：多切片本地检索后批量反思，并在缺口时触发一次联网补充。
- [x] 文档解析模块化：简历/JD 文件解析拆分至 `backend/services/document_processing.py`。
- [x] RAG 管线模块化：检索、反思、联网整合拆分至 `backend/services/rag_pipeline.py`。
- [x] 健康检查接口：新增 `GET /healthz`，可直接查看 API Key、知识库与联网开关状态。
- [x] 一键自检脚本：新增 `backend/scripts/self_test.py`，可快速检查环境与关键依赖。

## 🚀 如何运行 (Quick Start)

> 强烈建议：**所有命令都在仓库根目录执行**。本项目里 `chroma_db/`、`knowledge_base/` 等使用的是相对路径，换目录运行会导致“建库建在别处、后端找不到库”。

### 方式 A（推荐入门）：只跑后端 + 使用内置静态页

1) 安装依赖

\`\`\`bash
pip install -r requirements.txt
\`\`\`

2) 配置 `.env`（见下方）

3)（可选）首次建库（RAG）

\`\`\`bash
python backend/build_db.py
\`\`\`

4) 启动后端（从仓库根目录）

\`\`\`bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
\`\`\`

5) 打开页面

- 访问 `http://127.0.0.1:8000/`（后端会返回 `frontend/app.html`）
- 健康检查：访问 `http://127.0.0.1:8000/healthz`

### 方式 B（开发模式）：后端 + Vite 前端（用于改 React 页面）

1) 启动后端（同方式 A 第 4 步）

2) 启动前端（新开一个终端）

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

3) 打开 Vite 页面

- 访问 `http://127.0.0.1:3000/`

> 说明：静态页 `frontend/app.html` 会直连 `http://127.0.0.1:8000/analyze_audio` 调后端；如果你在 React 前端也采用直连 8000，需要确保跨域允许（后端已允许 `*` CORS）。

## 🔐 环境变量（.env）

在仓库根目录创建 `.env`：

\`\`\`text
# 必填：SiliconFlow OpenAI 兼容接口的 API Key（后端缺失会直接报错：API Key 未配置）
API_KEY=sk-xxxxx

# 可选：用于 LlamaParse 深度解析 PDF/Word/图片（不配会降级到本地 pdfplumber / python-docx）
LLAMA_CLOUD_API_KEY=llx-xxxxx

# 可选：是否启用联网补充检索（默认 false）
ENABLE_WEB_RAG=false
\`\`\`

## ✅ 一键自检

可在根目录运行：

\`\`\`bash
python backend/scripts/self_test.py
\`\`\`

脚本会检查：
- `API_KEY` 是否配置
- Chroma 集合 `product_manager_knowledge` 是否存在
- `frontend/app.html` 是否存在

## 📚 知识库（RAG）建库说明

1) 把资料放进 `knowledge_base/`（支持 `.pdf` / `.txt` / `.md`）

2) 运行建库脚本（从仓库根目录）

\`\`\`bash
python backend/build_db.py
\`\`\`

3) 产物

- 向量库会生成在 `chroma_db/`
- collection 名称为 `product_manager_knowledge`
- embedding 使用 `all-MiniLM-L6-v2`（首次运行会下载模型，时间较长属正常）

## 🧭 项目结构（关键目录/文件）

- `backend/main.py`: FastAPI 后端入口（提供 `POST /analyze_audio`，并托管前端静态页）
- `backend/build_db.py`: 知识库建库脚本（把 `knowledge_base/` 写入 `chroma_db/`）
- `frontend/app.html`: 静态单页 Demo
- `frontend/`: React/Vite 前端（开发模式端口 `3000`）
- `knowledge_base/`: 知识库语料
- `chroma_db/`: 本地向量库产物

## 🔌 API 说明（后端）

### \`POST /analyze_audio\`

- **Content-Type**: \`multipart/form-data\`
- **入参**：
  - \`file\`（必填）：音频文件
  - \`jd_text\`（可选）：JD/面试题文本
  - \`resume_text\`（可选）：简历文本
  - \`resume_file\`（可选）：简历文件（PDF/Word/图片；优先 LlamaParse，无 key 则本地降级）
  - \`jd_file\`（可选）：JD 文件（同上）
- **返回**（简化）：
  - \`status\`: \`success|error\`
  - \`transcription\`: ASR 识别文本
  - \`ai_analysis\`: 结构化分析结果（\`total_score\`、\`dimensions\`、\`transcript_correction\`、\`improvement_suggestions\` 等）

### \`GET /healthz\`

- **用途**：健康检查与部署验收
- **返回字段**：
  - \`status\`
  - \`api_key_configured\`
  - \`knowledge_collection_ready\`
  - \`web_rag_enabled\`

示例（只传音频 + 文本；Windows 下 \`cmd/powershell\` 均可用 \`curl\`）：

\`\`\`bash
curl -X POST "http://127.0.0.1:8000/analyze_audio" ^
  -F "file=@uploads/input.wav" ^
  -F "jd_text=请做个自我介绍" ^
  -F "resume_text=（可选）这里粘贴简历摘要"
\`\`\`

## 🧩 系统架构（数据流）

\`\`\`mermaid
flowchart LR
  U[用户] --> FE1[静态页 frontend/app.html]
  U --> FE2[React/Vite 前端 :3000]
  FE1 -->|multipart/form-data| API[FastAPI :8000 /analyze_audio]
  FE2 -->|multipart/form-data| API

  API --> ASR[ASR SenseVoiceSmall]
  API --> SCOUT[Scout: DeepSeek-V3]
  API --> COACH[Coach: Qwen3.5-122B]

  API -->|向量检索| CHROMA[(ChromaDB 本地向量库<br/>chroma_db / product_manager_knowledge)]
  API -->|解析 JD/简历文件| PARSE[LlamaParse (可选)]
  PARSE -.无 LLAMA_CLOUD_API_KEY .-> FALLBACK[本地降级解析<br/>pdfplumber / python-docx]

  API -->|本地无有效知识时（可选）| WEB[联网抓取（agent-browser）]
  API --> FE1
  API --> FE2
\`\`\`

## ❓ 常见问题（FAQ）

- **启动后提示 \`API Key 未配置\`**：检查根目录 `.env` 是否存在且包含 `API_KEY`。
- **不配 `LLAMA_CLOUD_API_KEY` 能不能用？**：可以。简历/JD 的文件解析会降级走本地 `pdfplumber` / `python-docx`。
- **建库很慢/卡住？**：首次会下载 embedding 模型并写入向量库，耗时几分钟属正常。
- **为什么强调从根目录运行？**：`knowledge_base/`、`chroma_db/` 在代码里是相对路径；换目录执行会导致库与语料生成在错误位置。

---
*Created by Li Shangkui. 2026.*