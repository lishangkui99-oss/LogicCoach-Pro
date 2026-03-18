# LogicCoach Pro - AI Interview Debrief Agent for Product Managers

## What It Is
LogicCoach Pro is an AI-native interview debrief system that turns subjective interview feedback into structured, measurable, and actionable outputs.

## Problem It Solves
- Generic LLM feedback is often too broad to guide real improvement.
- Candidates cannot clearly identify why they failed (business sense, product thinking, or communication structure).
- Interview debrief results are hard to track over time.

## Implemented Capabilities
- Audio transcription via SenseVoiceSmall.
- Dual-model collaboration:
  - Scout (DeepSeek-V3) for pre-analysis, segmentation, and focus extraction.
  - Coach (Qwen3.5-122B) for final deep assessment and scoring.
- Agentic RAG pipeline:
  - Local retrieval from ChromaDB.
  - Batch reflection and distillation across segments.
  - Optional web augmentation when local evidence is insufficient.
- Structured JSON output:
  - Overall score, 7-dimension scoring, transcript-level issue tagging, and targeted suggestions.
- Ops readiness:
  - /healthz endpoint and backend/scripts/self_test.py for fast validation.

## Tech Stack
- Backend: Python, FastAPI, Uvicorn
- LLM Access: OpenAI-compatible API (SiliconFlow)
- Models: DeepSeek-V3, Qwen3.5-122B, SenseVoiceSmall
- RAG: ChromaDB + SentenceTransformer embeddings
- Frontend: Static HTML + React/Vite

## Quick Run
- Start backend from repo root:
  - uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
- Health check:
  - GET http://127.0.0.1:8000/healthz
- Self test:
  - python backend/scripts/self_test.py

## Why This Project Is Notable
- Evolves from a single-model flow into a layered Scout-Coach architecture.
- Demonstrates production-minded engineering: modular services, fallbacks, health checks, and diagnostics.
- Shows end-to-end execution from architecture design to runnable validation.
