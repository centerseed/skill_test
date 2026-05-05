---
name: product-page-to-md
description: >
  爬取用戶指定的保健品產品頁 URL，提取文字 + 下載圖片 + 平行 OCR，
  整合成雙語結構化 MD，存放到 {OUTPUT_ROOT}/{ingredient_id}/market/ 目錄。
  用戶直接提供 URL 清單，無需 Google 搜尋。
  當使用者說「爬產品頁」「市場調查」「product-page-to-md」
  「幫我整理這些品牌」「爬這幾個 URL」時一定要使用這個 skill。
version: 2.0.0
---

# /product-page-to-md

爬取用戶指定的保健品產品頁，輸出雙語（中文優先）結構化 MD。

依賴：`requests`、`beautifulsoup4`（`pip install requests beautifulsoup4`）

## 輸出結構

```
{OUTPUT_ROOT}\{ingredient_id}\market\
├── mkt_01_{brand-slug}_{product-slug}.md
├── mkt_02_{brand-slug}_{product-slug}.md
├── ...
├── mkt_global_market-cases.md        ← 全域市場摘要
└── images\
    ├── mkt_01_{brand-slug}\
    │   ├── img_01.jpg
    │   └── ...
    └── mkt_02_{brand-slug}\
```

> **注意**：images 子目錄必須加 `mkt_{NN}_` 前綴，與 MD 檔編號一致。

## 執行前確認

詢問使用者（若對話中已知則跳過）：
1. **URL 清單**：要爬取哪些產品頁網址？（一次可以給多個，每行一個或逗號分隔）
2. **原料名稱**（搜尋用）？例如 "Omega-3"、"PureWay-C"
3. **Ingredient ID**？例如 `omega-3`、`pureway-c`（決定輸出目錄名稱）
4. **輸出根目錄**？（Windows 預設：`C:\health-research\ingredients`）

若使用者只提供部分資訊，以對話方式補充其餘欄位，不要直接執行缺少必要參數的步驟。

---

## ⚠️ 核心執行原則

**每一個品牌必須是獨立的 subagent，嚴禁批次處理。**

- Step 2（OCR）：每張圖片一個 subagent（圖片 > 8 張時）
- Step 3（編譯 MD）：每個品牌一個獨立 subagent，不得將多個品牌塞入同一 agent
- **品質目標：每個品牌 MD 最少 200 行，目標 250–350 行**
  - subagent 寫完前必須自計行數；若 < 200 行，找出最薄的段落繼續補充
- **全域市場摘要目標：最少 300 行，目標 400–500 行**
- 平行上限：同時最多 10 個 subagent，超過則分波執行

**orchestrator（主 agent）只負責：接收 URL、抓取文字+圖片、調度 subagent、彙整摘要。不得自己直接寫品牌 MD。**

---

## ⚠️ 每個品牌 MD 必須包含的內容（subagent checklist）

subagent 在輸出前逐項確認，缺少任一項必須補充：

### 1. 產品定位（目標 20–30 行）
- 目標族群（年齡、性別、健康需求）
- 定價策略（高端 / 中端 / 平價，與市場中位數比較）
- 通路策略（D2C 官網 / 藥妝店 / 診所推薦等）
- 品牌差異化點（與市場上其他同類產品有何不同）

### 2. 核心訴求（目標 20–30 行）
- 逐條列出所有功效訴求（不可遺漏）
- 每條訴求標記：✅ 有研究支持 / ⚠️ 誇大 / ❌ 無依據
- 聲稱強度評估：結構功能聲稱？還是疾病聲稱（法規禁止）？

### 3. 臨床數字聲稱（目標 15–25 行）
- 數字來源（品牌內部研究 / 獨立 RCT / Meta-analysis）
- 研究族群（健康人 / 亞健康 / 疾病患者，及樣本量）
- 若無臨床數字：明確標注「無具體臨床數字聲稱」，不可省略此節

### 4. 成分表（目標 15–20 行）
- 完整的主成分與含量（mg/IU/mcg）
- 搭配成分的功效說明
- 與同類競品的成分差異分析

### 5. 競品策略分析（目標 20–30 行）
- 此品牌如何在市場中定位自己對抗競品
- 若頁面有明確競品比較：完整重現比較表
- 若無：分析此品牌的隱性差異化策略

### 6. 品牌聲稱合規性評估（目標 10–20 行）
- 評估各聲稱的合規風險
- 整體評估：✅ 合規 / ⚠️ 灰色地帶 / ❌ 明顯違規

### 7. 圖片資產（完整列表）
- 每張保留圖片的類型說明
- 分析價值（高 / 中 / 低）

---

## Step 1：建立 URL 清單

使用者提供的 URL 清單即為輸入。依序為每個 URL 指定：

```
[
  {"rank": "01", "url": "...", "brand": "品牌名"},
  {"rank": "02", "url": "...", "brand": "品牌名"},
  ...
]
```

若使用者未提供品牌名，從 URL 網域推算（如 `now-foods.com` → `NOW Foods`）。

---

## Step 2：產品頁抓取（每個 URL）

**對每個 URL 執行以下步驟（可 parallel）：**

```
SKILL_DIR = skill 目錄的絕對路徑（SKILL.md 所在目錄）

執行指令（Windows 命令提示字元）：
python "{SKILL_DIR}\scripts\parse_page.py" "{URL}" "C:\Windows\Temp\product_{SLUG}"

執行指令（PowerShell）：
python "$env:SKILL_DIR\scripts\parse_page.py" "{URL}" "$env:TEMP\product_{SLUG}"

輸出：
- C:\Windows\Temp\product_{SLUG}_text.txt
- C:\Windows\Temp\product_{SLUG}_images.json
```

```
python "{SKILL_DIR}\scripts\dl_images.py" ^
  "C:\Windows\Temp\product_{SLUG}_images.json" ^
  "{OUTPUT_ROOT}\{ingredient_id}\market\images\mkt_{RANK}_{BRAND_SLUG}\" ^
  15
```

> SLUG = 品牌名小寫去空格，例如 `nature-s-plus`
> 若 parse_page.py 返回 403 或失敗：記錄跳過，繼續下一個 URL。

---

## Step 3：OCR（parallel subagents）

**有兩種執行模式，依圖片數量選擇：**

**模式 A（圖片 ≤ 8 張）**：每個品牌一個 subagent，在 subagent 內批次讀取所有圖片做 OCR。
**模式 B（圖片 > 8 張）**：每張圖一個 subagent，全部同時 spawn。

每個 OCR 任務判斷標準：
```
圖片 OCR 審查員。讀取圖片，判斷是否有實質資訊。

圖片路徑：{IMAGE_PATH}

判斷標準：
- 有用（含產品說明、數字、認證、成分、比較表、功效文字）→ 輸出完整 OCR 文字
- 無用（純裝飾、背景色塊、單一 logo 無文字、UI 圖示）→ 用 Bash 刪除檔案

輸出格式：
[保留] {檔名} — {圖片類型}
{OCR 文字}

或：
[刪除] {檔名} — {原因一句話}
```

---

## Step 4：編譯 MD（每個品牌一個 subagent）

**為每個品牌 spawn 一個 subagent，讀取文字 + 整合 OCR 結果，輸出雙語 MD。**

每個 subagent 輸入（orchestrator 必須全部提供）：
- 頁面文字：`C:\Windows\Temp\product_{SLUG}_text.txt`
- OCR 結果：（直接傳入文字，不傳圖片）
- 品牌資訊、URL、日期、原料名稱
- **已有其他品牌的摘要清單**（品牌名 + 主要差異化點），供競品策略分析用

輸出格式（中文優先）：
```markdown
# {產品名稱}

**品牌**：{品牌}（{國家/地區}）
**目標族群**：{明確描述}
**售價**：{價格 + 每日成本試算}
**URL**：...
**抓取日期**：{TODAY}
**相關原料**：{INGREDIENT_NAME}

---

## 產品定位
【目標 20–30 行；嚴禁只寫一兩句】

## 核心訴求
【目標 20–30 行；逐條列出，每條標記合規評估】

## 臨床數字聲稱
【目標 15–25 行；若無則明確標注「無具體臨床數字聲稱」，不可省略】

## 成分表
| 成分 | 含量 | 形式/來源 | 搭配原因 |
|------|------|---------|---------|

## 功效聲稱（逐條中英對照）
| # | 中文聲稱 | 原文 | 聲稱類型 | 合規評估 |

## 競品策略分析
【目標 20–30 行；必須有具體洞察】

## 認證與第三方驗證
| 認證名稱 | 發證機構 | 說明 |

## 圖片資產
| 檔名 | 圖片類型 | OCR 重點 | 分析價值（高/中/低） |

## 顧客評論（若有）

## 品牌聲稱合規性評估
【目標 10–20 行】
整體評估：✅ 合規 / ⚠️ 有灰色地帶 / ❌ 有明顯違規

## 注意事項（FDA 聲明等）

## 市場分析小結
【目標 10–15 行】
```

存檔路徑：`{OUTPUT_ROOT}\{ingredient_id}\market\mkt_{RANK}_{BRAND_SLUG}_{PRODUCT_SLUG}.md`

**寫入前品質自查：**
1. 計算行數 → 若 < 200 行，補充最薄的段落
2. 每個 section 都有實質內容
3. 臨床數字聲稱節已填寫
4. 競品策略分析有具體洞察

---

## Step 5：生成全域市場摘要

**所有個別 MD 完成後，彙整成一份全域市場摘要。**

> 品質要求：最少 300 行，目標 400–500 行。
> 核心價值是「跨品牌洞察」，不是各品牌摘要清單。

存檔路徑：`{OUTPUT_ROOT}\{ingredient_id}\market\mkt_global_market-cases.md`

```markdown
# {INGREDIENT_NAME} 全球市場使用案例彙整

**整理日期**：{TODAY}
**涵蓋品牌數**：{N} 個

---

## 產品總覽表
| # | 品牌 | 國家 | 目標族群 | 劑量 | 主要搭配成分 | 售價 | 每日成本 |

## 市場規律分析
### 劑量分布
### 最常見搭配成分
### 主要訴求分類
### 定價帶分析

## 配方設計深度分析
### 市場主流配方
### 差異化配方方向
### 尚未有品牌佔領的配方方向（市場空白）

## 各族群市場現況
### 成人通用市場
### 兒童市場
### 孕婦/哺乳市場
### 銀髮/老年市場

## 市場空白與機會

## 聲稱合規風險地圖

## 對本原料產品開發的具體建議
```

---

## Step 6：彙整回報

完成後向使用者回報：
1. 成功處理幾家品牌（成功/跳過）
2. 各 MD 路徑 + 品牌名
3. 共保留/刪除幾張圖片
4. 哪些 URL 因 403 跳過
5. 輸出根目錄完整路徑（方便用戶直接開啟）

---

## 注意事項

- **403 站點**：記錄跳過，不強制使用 Playwright
- **OCR 空圖**：直接刪除，不進 MD
- **中文優先**：所有外文必須附中文翻譯，格式為「中文（原文：英文）」
- **日文/韓文站點**：翻譯成中文，格式同上
- **Slug 規則**：小寫英文、數字、連字號，空格→-，特殊字元移除
- **Python 環境**：使用 `python`（Windows 上確認已加入 PATH）
- **路徑**：輸出目錄若不存在，scripts 會自動建立
