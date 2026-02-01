# LogicCoach Pro 🤖
> 基于 DeepSeek-V3 与 RAG 技术的 AI 产品经理面试教练系统。

## 核心功能
LogicCoach Pro 旨在通过“准备-实战-复盘”的闭环逻辑，解决传统模拟面试反馈泛化的问题。
- **👂 听觉层**: 集成 SenseVoice，支持高精度语音转文字 (ASR)。
- **🧠 认知层**: 基于 DeepSeek-V3 模型，结合人岗匹配逻辑进行深度推理。
- **📚 记忆层**: RAG (检索增强生成) 挂载 110+ 篇私有产品方法论，拒绝通用幻觉。
- **📊 表现层**: 自动生成 7 维能力雷达图与逻辑纠错报告。

## 技术栈
- **Backend**: Python 3.11, FastAPI
- **AI Model**: DeepSeek-V3 (via SiliconFlow API)
- **Vector DB**: ChromaDB
- **Frontend**: Native HTML/JS + Chart.js

## 如何运行
1. 克隆仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 配置环境: 创建 `.env` 文件并填入 `API_KEY=your_key`
4. 初始化知识库: `python backend/build_db.py`
5. 启动服务:
   ```bash
   cd backend
   uvicorn main:app --reload