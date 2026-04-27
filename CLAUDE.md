# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用指令

```bash
# 啟動應用（主要開發環境）
cd poc && python app.py
# 服務於 http://0.0.0.0:7860

# 建立/更新向量索引
cd poc && python ingest.py               # 增量新增
cd poc && python ingest.py --force       # 全量重建
cd poc && python ingest.py --update <id> # 更新特定商品（如 9-calcium）
cd poc && python ingest.py --list        # 列出 DB 統計

# 執行測試
python test_agent.py       # 多輪對話測試
python test_guardrail.py   # Guardrail 快速驗證
python test_suite.py       # 完整評估套件（6 個評分維度）

# 部署到 HuggingFace Space
bash deploy.sh
```

## 環境設定

- Python 環境：`poc/.venv`（Python 3.11）或 conda `health` 環境
- 環境變數：`poc/.env`（包含 `GOOGLE_API_KEY`，**絕對不能 commit**）
- 參考 `poc/.env.example`

## 架構概覽

### 核心資料流

```
用戶輸入
  → [Input Guardrail] 防 jailbreak
  → naru_agent.Runner (ReAct 迴圈)
      → LLM 思考（gemini-2.5-flash-lite）
      → Tool: search_products
          → embed_query（gemini-embedding-001）
          → ChromaDB 向量搜尋（TOP_K=3）
          → 組合上下文 + 商品連結
      → LLM 回覆生成
  → [MedicalDisclaimerGuardrail] 判斷是否附加醫療免責聲明
  → Gradio UI（聊天視窗 + 參考商品區塊）
```

### 關鍵目錄與檔案

| 路徑 | 說明 |
|------|------|
| `poc/app.py` | 主應用（Gradio UI + naru_agent ReAct Agent） |
| `poc/ingest.py` | 建立 ChromaDB 向量索引 |
| `poc/loaders/greencome_loader.py` | 讀取產品資料並產生 chunks |
| `poc/output/products.json` | 250+ 商品元數據 |
| `poc/output/products/*.md` | 商品詳情 Markdown |
| `poc/chroma_db/` | ChromaDB 本地向量庫（不進 git） |
| `naru_agent/` | 自研輕量 Agent 框架（Git submodule） |
| `hf_space/` | HuggingFace Space 部署版本（由 deploy.sh 同步） |
| `test_suite.py` | 評估套件（醫療合規 6 維度） |

### 模型設定（重要）

```python
EMBED_MODEL = "gemini-embedding-001"       # Embedding
GEN_MODEL   = "gemini/gemini-2.5-flash-lite"  # 主生成（注意：是 flash-lite，不是 flash）
# ingest.py 使用 task_type=RETRIEVAL_DOCUMENT
# app.py    使用 task_type=RETRIEVAL_QUERY
MEMORY_EMBED_DIM = 768  # 記憶層 embedding 降維（MRL），與 Naruvia 一致
```

### 記憶層（Neon DB + pgvector）

- **Store**：`naru_agent/naru_agent/memory/stores/postgres.py`（`PostgresMemoryStore`）
- **資料庫**：Naruvia 專案的 Neon PostgreSQL（共用 DB，獨立 table `health123_memories`）
- **設定**：`poc/.env` 的 `NEON_DATABASE_URL`
- **運作**：每輪對話後，MemoryManager 自動提取用戶偏好事實並存入 Neon；下次對話時語意搜尋相關記憶注入 system prompt
- **降級**：未設定 `NEON_DATABASE_URL` 時自動跳過記憶層（無記憶模式）

### naru_agent 框架

位於 `naru_agent/` 的 Git submodule，核心模組：
- `runner.py`：ReAct 執行迴圈（Thought → Action → Observation）
- `llm/litellm_provider.py`：透過 LiteLLM 支援 100+ 模型
- `tools/base.py`：`@tool` 裝飾器定義工具
- `guardrails/`：輸入/輸出防護介面
- `memory/`：Per-user 對話記憶（ChromaDB 後端）

### MedicalDisclaimerGuardrail

`app.py` 中的輸出端 Guardrail，用 LLM-as-judge（temperature=0）判斷：
- 對話脈絡是否涉及醫療情境？
- 是否推薦了產品？

兩者都是才自動附加免責聲明。**禁止暗示保健品能「治療」「改善病症」「降低數值」**。

### 資料 Pipeline

```
crawl_greencome.py → output/products.json + output/products/*.md
                          ↓
                  greencome_loader.py (chunks)
                          ↓
                     ingest.py → ChromaDB
```

## 部署

`deploy.sh` 自動同步 poc/app.py、naru_agent/、chroma_db/ 到 `hf_space/`，並推送至 HuggingFace Space（`centerseed/health123_poc`）。`hf_space/` 中的 naru_agent 路徑為本地副本（非 submodule）。
