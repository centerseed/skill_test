"""
快速驗證 MedicalDisclaimerGuardrail 的測試腳本
用法：conda run -n health python test_guardrail.py
"""
import os
import sys
from pathlib import Path

# 設定路徑
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "naru_agent"))
sys.path.insert(0, str(ROOT / "poc"))

from dotenv import load_dotenv
load_dotenv(ROOT / "poc" / ".env")

if not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "")

from google import genai
from google.genai import types
from naru_agent.guardrails.base import BaseGuardrail, GuardrailResult


class MedicalDisclaimerGuardrail(BaseGuardrail):
    JUDGE_PROMPT = """你是台灣保健食品業的合規審查員。
判斷下方客服回覆是否同時符合以下兩個條件：

條件 A：對話中出現具體醫療情境，包含：
- 血檢／體檢數值（如膽固醇、血糖、血壓、尿酸、三酸甘油脂等）
- 明確被診斷的疾病或症狀（如高血壓、糖尿病、高血脂、心臟病等）

條件 B：回覆中針對上述醫療情境推薦了特定保健產品

僅當 A 和 B 同時成立才回答 NEED_DISCLAIMER。
以下情況回答 OK（不觸發）：
- 一般保健需求（消化、護眼、增強體力、日常補充等）
- 回覆只表達關懷、建議就醫，未推薦具體產品
- 保健食品一般功效說明（幫助消化、維持視力等），不涉及具體疾病

客服回覆：
{response}

只回答：NEED_DISCLAIMER 或 OK"""

    DISCLAIMER_MARKER = "⚠️ **健康提醒**"
    DISCLAIMER = (
        "\n\n---\n"
        "⚠️ **健康提醒**：保健食品屬日常營養補充品，無法取代醫療診斷與治療。"
        "若您有血檢或體檢數值異常，建議優先攜帶報告諮詢專業醫師。"
    )

    def __init__(self, genai_client):
        self._client = genai_client

    def check_input(self, message: str) -> GuardrailResult:
        return GuardrailResult(passed=True)

    def check_output(self, response: str) -> GuardrailResult:
        if self.DISCLAIMER_MARKER in response:
            return GuardrailResult(passed=True)

        prompt = self.JUDGE_PROMPT.format(response=response)
        verdict = self._client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0),
        ).text.strip()

        print(f"  [judge] verdict={verdict!r}")

        if "NEED_DISCLAIMER" in verdict:
            return GuardrailResult(
                passed=False,
                modified_text=response + self.DISCLAIMER,
            )
        return GuardrailResult(passed=True)


def run_test(guardrail, label, response, expect_disclaimer: bool):
    print(f"\n{'='*60}")
    print(f"測試：{label}")
    print(f"輸入回覆（前80字）：{response[:80]}...")
    result = guardrail.check_output(response)
    # passed=True 且沒有 modified_text → 沒有免責聲明
    # passed=False 且有 modified_text → 有免責聲明
    # 已有 DISCLAIMER_MARKER → check_output 直接 passed=True，原文已含聲明
    if result.passed:
        has_disclaimer = guardrail.DISCLAIMER_MARKER in response
    else:
        has_disclaimer = bool(result.modified_text and guardrail.DISCLAIMER_MARKER in result.modified_text)
    status = "✅ PASS" if (has_disclaimer == expect_disclaimer) else "❌ FAIL"
    print(f"預期有免責聲明：{expect_disclaimer}  實際：{has_disclaimer}  {status}")
    if result.modified_text:
        print(f"--- 輸出末尾 ---\n{result.modified_text[-200:]}")


if __name__ == "__main__":
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("錯誤：缺少 GOOGLE_API_KEY")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    g = MedicalDisclaimerGuardrail(client)

    # 測試案例
    MEDICAL_REPLY = (
        "了解您血檢膽固醇偏高，建議攜帶報告給醫師確認。"
        "在日常保養上，我們的紅麴膠囊含有紅麴成分，很多人會用來輔助日常維護。"
        "另外魚油中的Omega-3也是很多人選擇的日常補充品。"
    )
    NORMAL_REPLY = (
        "我們有賣益生菌！推薦您試試「活力益生菌膠囊」，"
        "含有多種益生菌菌株，幫助維持消化道健康。"
    )
    EYE_REPLY = (
        "護眼產品推薦「葉黃素複方膠囊」，含有葉黃素與玉米黃質，"
        "適合長時間使用3C產品的現代人日常保養。"
    )
    ALREADY_HAS_DISCLAIMER = MEDICAL_REPLY + "\n\n---\n⚠️ **健康提醒**：保健食品屬日常營養補充品。"

    run_test(g, "醫療問題回覆（應觸發）", MEDICAL_REPLY, expect_disclaimer=True)
    run_test(g, "一般益生菌推薦（不應觸發）", NORMAL_REPLY, expect_disclaimer=False)
    run_test(g, "護眼產品推薦（不應觸發）", EYE_REPLY, expect_disclaimer=False)
    run_test(g, "已有免責聲明（不重複附加）", ALREADY_HAS_DISCLAIMER, expect_disclaimer=True)
