"""
完整 Agent 多輪對話測試（含 guardrail）
用法：conda run -n health python test_agent.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "naru_agent"))
sys.path.insert(0, str(ROOT / "poc"))

from dotenv import load_dotenv
load_dotenv(ROOT / "poc" / ".env")
if not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")

import importlib.util
spec = importlib.util.spec_from_file_location("app", ROOT / "poc" / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

chat_fn = app.make_gradio_chat(app._runner, app._last_chunks)


def chat(q: str, history: list) -> tuple[str, list]:
    updated, sources, _ = chat_fn(q, history)
    answer = updated[-1]["assistant"]
    return answer, updated


def show(label: str, q: str, answer: str):
    has = "⚠️ **健康提醒**" in answer
    print(f"\n{'='*60}")
    print(f"[{label}]")
    print(f"問：{q}")
    print(f"-"*60)
    print(answer)
    print(f"\n→ 含免責聲明：{'✅ 是' if has else '❌ 否（符合預期）' if not has else '❌ 否（異常）'}")


# ── 情境一：膽固醇問題 → 多輪推薦 ───────────────────────────
print("\n" + "█"*60)
print("情境一：膽固醇偏高 → 多輪對話")
print("█"*60)

history = []
q1 = "我血檢膽固醇比較高，有什麼產品推薦？"
a1, history = chat(q1, history)
show("第1輪：提問（不應立即推銷）", q1, a1)

q2 = "我平常飲食還好，就是想保養一下，有推薦的嗎？"
a2, history = chat(q2, history)
show("第2輪：用戶給背景→agent推薦產品（應觸發免責聲明）", q2, a2)

# ── 情境二：一般益生菌問題 ───────────────────────────────────
print("\n" + "█"*60)
print("情境二：一般問題，不涉及醫療")
print("█"*60)

history = []
q1 = "你們有賣益生菌嗎？"
a1, history = chat(q1, history)
show("第1輪：一般提問", q1, a1)

q2 = "就是想幫助消化，哪款比較好？"
a2, history = chat(q2, history)
show("第2輪：推薦（不應觸發）", q2, a2)
