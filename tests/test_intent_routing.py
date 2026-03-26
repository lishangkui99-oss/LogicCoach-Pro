import sys
import types
import unittest
from pathlib import Path
from urllib.parse import quote


# Add backend directory to import path: backend/services/*
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# Lightweight stubs so tests can import modules without full runtime deps.
if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")

    class OpenAI:  # pragma: no cover
        pass

    openai_stub.OpenAI = OpenAI
    sys.modules["openai"] = openai_stub

if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    class _Utils:  # pragma: no cover
        @staticmethod
        def quote(text):
            return quote(text)

    requests_stub.utils = _Utils()
    sys.modules["requests"] = requests_stub


from services.scout_coach import (  # noqa: E402
    _normalize_intent_label,
    build_dynamic_evaluation_criteria,
    scan_interview_intent,
)
from services.rag_pipeline import apply_intent_rag_routing  # noqa: E402


class TestIntentNormalization(unittest.TestCase):
    def test_normalize_exact_label(self):
        self.assertEqual(_normalize_intent_label("AI技术面"), "AI技术面")

    def test_normalize_hr_variants(self):
        self.assertEqual(_normalize_intent_label("HR interview"), "HR通用面")
        self.assertEqual(_normalize_intent_label("重点看沟通和价值观"), "HR通用面")

    def test_normalize_product_variants(self):
        self.assertEqual(_normalize_intent_label("需求分析和商业模式") , "产品专业面")

    def test_normalize_ai_variants(self):
        self.assertEqual(_normalize_intent_label("Prompt strategy for agent"), "AI技术面")

    def test_normalize_unknown(self):
        self.assertEqual(_normalize_intent_label("随便聊聊"), "未识别")


class TestDynamicCriteria(unittest.TestCase):
    def test_product_criteria_contains_expected_weights(self):
        text = build_dynamic_evaluation_criteria("产品专业面", "需求优先级和指标闭环")
        self.assertIn("场景: 产品专业面", text)
        self.assertIn("主权重 65%", text)
        self.assertIn("参考红线", text)

    def test_ai_criteria_contains_expected_anchor(self):
        text = build_dynamic_evaluation_criteria("AI技术面", "Agent评估标准")
        self.assertIn("场景: AI技术面", text)
        self.assertIn("意图路由", text)

    def test_unknown_criteria_has_fallback(self):
        text = build_dynamic_evaluation_criteria("其他")
        self.assertIn("场景: 未识别", text)
        self.assertIn("均衡权重", text)


class TestIntentScanner(unittest.TestCase):
    class _FakeCompletions:
        def __init__(self, content=None, raises=False):
            self._content = content
            self._raises = raises

        def create(self, **kwargs):
            if self._raises:
                raise RuntimeError("mock scanner error")

            message = types.SimpleNamespace(content=self._content)
            choice = types.SimpleNamespace(message=message)
            return types.SimpleNamespace(choices=[choice])

    class _FakeClient:
        def __init__(self, content=None, raises=False):
            self.chat = types.SimpleNamespace(
                completions=TestIntentScanner._FakeCompletions(content=content, raises=raises)
            )

    def test_scan_intent_maps_model_output(self):
        client = self._FakeClient(content="AI技术面")
        text = "这段面试重点讨论了大模型边界、prompt策略、agent流程与评估标准。"
        self.assertEqual(scan_interview_intent(client, "mock-model", text), "AI技术面")

    def test_scan_intent_fallback_on_exception(self):
        client = self._FakeClient(raises=True)
        text = "这段文本长度足够触发扫描，但是模型调用会抛异常。"
        self.assertEqual(scan_interview_intent(client, "mock-model", text), "未识别")


class TestIntentRagRouting(unittest.TestCase):
    def setUp(self):
        self.segments = [
            {
                "id": 1,
                "topic": "增长策略",
                "rag_queries": ["漏斗优化", "用户分层"],
            },
            {
                "id": 2,
                "topic": "模型能力",
                "rag_queries": ["上下文窗口"],
            },
        ]

    def test_bypass_for_hr(self):
        routed = apply_intent_rag_routing("HR通用面", self.segments)
        self.assertEqual(routed, self.segments)

    def test_product_routing_enhances_queries(self):
        routed = apply_intent_rag_routing("产品专业面", self.segments, max_queries_per_segment=4)
        self.assertEqual(len(routed), 2)
        self.assertLessEqual(len(routed[0]["rag_queries"]), 4)
        joined = " ".join(routed[0]["rag_queries"])
        self.assertTrue("需求分析框架" in joined or "商业模式闭环与指标体系" in joined)

    def test_ai_routing_enhances_queries(self):
        routed = apply_intent_rag_routing("AI技术面", self.segments, max_queries_per_segment=4)
        joined = " ".join(routed[1]["rag_queries"])
        self.assertTrue("Prompt工程策略" in joined or "Agent架构与生成内容评估" in joined)

    def test_empty_segments(self):
        self.assertEqual(apply_intent_rag_routing("产品专业面", []), [])


if __name__ == "__main__":
    unittest.main()
