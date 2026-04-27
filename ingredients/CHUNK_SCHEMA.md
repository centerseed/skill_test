# Ingredient Chunk Schema v2.0

**適用範圍**：所有原料知識庫 chunk 檔案（`ingredients/*/chunks/*.md`）
**設計目標**：同時支援傳統 RAG（向量檢索）和 Graph RAG（實體關係圖）

---

## 目錄結構

```
ingredients/{ingredient_id}/
└── chunks/
    ├── {ingredient_id}_overview.md
    ├── {ingredient_id}_mechanism_{descriptor}.md
    ├── {ingredient_id}_human_rct_{study_slug}.md
    ├── {ingredient_id}_in_vitro_{study_slug}.md
    ├── {ingredient_id}_systematic_review_{study_slug}.md
    ├── {ingredient_id}_regulatory_{jurisdiction}.md
    ├── {ingredient_id}_brand_{brand_slug}.md
    ├── {ingredient_id}_market_analysis.md
    ├── {ingredient_id}_formula_{application}.md
    └── {ingredient_id}_comparison_vs_{target_ingredient}.md
```

---

## Frontmatter Schema

```yaml
---
# ── Identity ──────────────────────────────────────────
chunk_id: {ingredient_id}_{chunk_type}_{descriptor}
chunk_type: {見下方 Chunk Types}
version: "2.0"

# ── Entity ────────────────────────────────────────────
ingredient_id: pureway-c
ingredient_name: PureWay-C®

# ── Source（只引用一個最權威來源，不重複） ─────────────
source_type: supplier_pdf | academic_paper | market_page | youtube
source_file: {檔名}
source_url: {url，若有}
created: YYYY-MM-DD
updated: YYYY-MM-DD

# ── RAG Metadata（用於向量檢索的 pre-filter） ──────────
claims: []                     # 受控詞彙，見 Claims Vocabulary
evidence_level: {見下方}        # 單一值，反映本 chunk 的最高證據等級
has_human_data: true | false   # 是否包含人體試驗數據
regulatory_jurisdiction: []    # taiwan | usa | eu | global（可多個）
regulatory_compliant: true | false | unknown   # 本 chunk 的聲稱是否符合法規

# ── Graph RAG Relations（顯式邊，用於知識圖譜） ─────────
relations:
  - {rel: VALIDATED_BY, target_id: study_pancorbo2008, target_type: study}
  - {rel: COMPARES_TO, target_id: ester-c, target_type: ingredient}
---
```

---

## Chunk Types

| chunk_type | 中文 | 每個 chunk | 目標字數 | 說明 |
|-----------|------|-----------|---------|------|
| `overview` | 原料概述 | 每原料 1 個 | 200–300 字 | 是什麼、組成、核心訴求、認證 |
| `mechanism` | 作用機制 | 每機制 1 個 | 150–250 字 | 為什麼有效：分子路徑、吸收機制 |
| `human_rct` | 人體 RCT | 每篇論文 1 個 | 200–350 字 | 人體隨機對照試驗結果 |
| `human_observational` | 人體觀察 | 每篇論文 1 個 | 150–250 字 | 非 RCT 人體研究 |
| `in_vitro` | 細胞實驗 | 每篇論文 1 個 | 150–200 字 | 體外細胞或動物實驗 |
| `systematic_review` | 系統性回顧 | 每篇論文 1 個 | 200–350 字 | Meta-analysis 或系統性回顧 |
| `regulatory` | 法規 | 每個司法管轄區 1 個 | 150–250 字 | 允許/限制的宣稱與劑量上限 |
| `brand_product` | 市場產品 | 每個品牌產品 1 個 | 200–300 字 | 含該原料的市場產品 |
| `market_analysis` | 市場分析 | 每原料 1 個 | 250–350 字 | 市場趨勢、定價帶、配方空白 |
| `formula` | 配方建議 | 每個應用方向 1 個 | 150–250 字 | 特定應用場景的配方建議 |
| `comparison` | 競品比較 | 每個比較對象 1 個 | 150–250 字 | 與特定競品的比較 |
| `youtube_video` | YouTube 影片 | 每支影片 1 個 | 200–400 字 | YouTube 專家/品牌影片的知識萃取 |

---

## 命名規則

格式：`{ingredient_id}_{chunk_type}_{descriptor}.md`

| 範例 | 說明 |
|------|------|
| `pureway-c_overview.md` | overview 固定無 descriptor |
| `pureway-c_mechanism_svct-bypass.md` | 機制主題作 descriptor |
| `pureway-c_human_rct_pancorbo2008.md` | 作者+年份 |
| `pureway-c_in_vitro_weeks2007-absorption.md` | 作者+年份+主題 |
| `pureway-c_systematic_review_calder2025.md` | 作者+年份 |
| `pureway-c_regulatory_taiwan.md` | 司法管轄區 |
| `pureway-c_regulatory_usa.md` | |
| `pureway-c_brand_jigsaw-health.md` | 品牌 slug |
| `pureway-c_market_analysis.md` | market_analysis 固定無 descriptor |
| `pureway-c_formula_immune.md` | 應用方向 |
| `pureway-c_formula_beauty.md` | |
| `pureway-c_formula_sports.md` | |
| `pureway-c_comparison_vs-ester-c.md` | 競品 slug |
| `pureway-c_comparison_vs-regular-aa.md` | |
| `pureway-c_youtube_01_examine-com.md` | 頻道 slug |

Slug 規則：全小寫英文、數字、連字號，空格→`-`，特殊字元移除。

---

## Claims Vocabulary（受控詞彙）

所有 chunk 的 `claims` 欄位只能從此清單選取，確保跨原料一致性：

| 詞彙 | 中文 | 說明 |
|------|------|------|
| `bioavailability` | 生物利用率/吸收率 | 吸收速度、血清濃度、細胞攝取 |
| `immune` | 免疫 | 免疫細胞功能、免疫調節 |
| `antioxidant` | 抗氧化 | 自由基清除、ORAC、DPPH |
| `collagen` | 膠原蛋白 | 膠原蛋白合成、結締組織 |
| `wound_healing` | 傷口癒合 | 組織修復、纖維母細胞 |
| `anti_inflammatory` | 抗發炎 | CRP、細胞激素 |
| `cardiovascular` | 心血管 | oxLDL、動脈彈性 |
| `cognitive` | 認知/神經 | 神經突生長、神經傳導 |
| `energy` | 能量代謝 | 肉鹼合成、粒線體 |
| `gut_health` | 腸道健康 | 腸道耐受、益菌 |
| `skin_beauty` | 皮膚美容 | 皮膚緊緻、黑色素抑制、UV 防護 |
| `bone_joint` | 骨骼關節 | 骨密度、關節軟骨 |
| `sports_recovery` | 運動恢復 | 肌肉損傷修復、脂質過氧化 |
| `longevity` | 抗老 | 細胞老化、氧化壓力 |
| `iron_absorption` | 鐵吸收 | 促進非血基質鐵吸收 |

---

## Evidence Level Vocabulary

| 值 | 中文 | 說明 |
|----|------|------|
| `systematic_review` | 系統性回顧 | 含 Meta-analysis |
| `human_rct` | 人體 RCT | 隨機對照試驗 |
| `human_observational` | 人體觀察研究 | 非隨機人體研究 |
| `in_vitro` | 體外實驗 | 細胞或動物實驗 |
| `book_chapter` | 書章/文獻回顧 | 非期刊同儕審查 |
| `market_data` | 市場資料 | 產品頁、市場調查 |
| `supplier_claim` | 供應商聲稱 | 未同儕審查，僅供應商提供 |
| `regulatory` | 法規文件 | 衛福部、FDA 等官方文件 |

---

## Relations Vocabulary（Graph RAG 邊類型）

| rel | 方向 | 說明 |
|-----|------|------|
| `VALIDATED_BY` | chunk → study | 本聲稱被此研究支持 |
| `COMPARES_TO` | chunk → ingredient | 本 chunk 比較了此競品 |
| `USES` | brand → ingredient | 品牌產品使用此原料 |
| `FUNDED_BY` | study → organization | 研究由此機構資助（利益衝突） |
| `PERMITTED_BY` | claim → regulatory | 此宣稱在此法規下允許 |
| `RESTRICTED_BY` | claim → regulatory | 此宣稱在此法規下受限 |
| `SYNERGIZES_WITH` | ingredient → ingredient | 協同效應 |
| `CITES` | study → study | 論文引用關係 |
| `SOURCED_FROM` | chunk → supplier | 原料由此供應商提供 |

---

## 內文格式規範

### 必要結構

```markdown
{FRONTMATTER}

以下是 {ingredient_name} 的 {chunk_type 中文描述}：

{內文，純文字段落，不使用過多子標題}
```

### 內文規則

1. **首行語境**：`以下是 {ingredient_name} 的 {描述}：` —— 讓 chunk 在脫離脈絡時仍可理解
2. **Frontmatter 不嵌入 text**：Loader 應將 frontmatter 解析為 metadata，不 embed 進向量
3. **數字完整保留**：所有 %、mg、p值、n數、倍數
4. **人體 vs 細胞明確標注**：in_vitro chunk 必須在內文第一行標注「本研究為細胞實驗，數據不等同人體效果」
5. **每個 chunk 只談一件事**：不在同一 chunk 中混合免疫和美容應用
6. **無子標題**：chunk 是最小單元，內部用段落而非 H2/H3 分節

### chunk_type = `in_vitro` 必加警語

```
⚠️ 本研究為體外細胞實驗，數字不等同人體服用效果，只能用於機制說明，不能作為主要功效聲稱依據。
```

---

## 去重規則（Deduplication）

**同一研究只能有一個 chunk，不得跨 skill 重複。**

| 來源 | 優先級 | 說明 |
|------|--------|------|
| 學術論文（academic-paper-to-md） | 最高 | 產生 `human_rct`、`in_vitro`、`systematic_review` chunk |
| 供應商 PDF（supplier-pdf-to-md） | 次之 | 若學術 chunk 已存在，供應商 chunk 不重複產生同研究內容；改為在 `overview` 的 `relations` 中引用 |
| 市場頁（product-page-to-md） | 最低 | 只產生 `brand_product` chunk，不重複學術數據 |

---

## Loader 規範（供 ingest.py 使用）

Loader 必須：
1. 分離 frontmatter（作為 ChromaDB metadata）與內文（作為 embed text）
2. 將 `claims` list 平展為 metadata（`claims_immune: true`、`claims_antioxidant: true`）
3. 將 `relations` 序列化為 JSON string metadata
4. 不 embed frontmatter YAML 本身

ChromaDB document = 首行語境 + 內文（不含 frontmatter）
ChromaDB metadata = 所有 frontmatter 欄位

---

## 範例：pureway-c_human_rct_pancorbo2008.md

```markdown
---
chunk_id: pureway-c_human_rct_pancorbo2008
chunk_type: human_rct
version: "2.0"

ingredient_id: pureway-c
ingredient_name: PureWay-C®

source_type: academic_paper
source_file: rsc_02_pancorbo-2008_serum-bioavailability.md
source_url: https://pubmed.ncbi.nlm.nih.gov/18971870/
created: 2026-04-25
updated: 2026-04-25

claims: [bioavailability, anti_inflammatory, cardiovascular]
evidence_level: human_rct
has_human_data: true
regulatory_jurisdiction: [global]
regulatory_compliant: true

relations:
  - {rel: VALIDATED_BY, target_id: study_pancorbo2008, target_type: study}
  - {rel: COMPARES_TO, target_id: ester-c, target_type: ingredient}
  - {rel: COMPARES_TO, target_id: regular-aa, target_type: ingredient}
  - {rel: CITES, target_id: calder2025, target_type: study}
---

以下是 PureWay-C® 的人體隨機對照試驗數據（Pancorbo et al., 2008）：

Pancorbo 等人（2008）在 40 位健康受試者中進行雙盲隨機試驗，比較 PureWay-C®、一般抗壞血酸（AA）、抗壞血酸鈣（CaA）和 Ester-C® 各 1,000 mg 單次口服後的血清維生素 C 動態。受試者先接受 14 天低維生素 C 飲食洗脫期，再於禁食隔夜後服藥，並在 0、1、2、4、6、24 小時採血。

主要結果：PureWay-C® 組在給藥後 2 小時血清峰值為 2.2 mg/dL，高於 Ester-C® 1.7 mg/dL、AA 1.65 mg/dL 和 CaA 1.1 mg/dL。在 1、2、4、6 小時四個時間點，PureWay-C® 血清濃度均顯著高於 CaA（p<0.05）。24 小時後 PureWay-C® 組仍比基線高 52%（AA 為 42%），顯示更佳的短期滯留性，但此優勢到 24 小時後消失。

抗炎與心血管指標：PureWay-C® 組的血漿 CRP（C反應蛋白）和 oxLDL 下降幅度在四組中最優，但原文未報告具體百分比，屬方向性結論。

期刊：Medical Science Monitor，2008；PMID 18971870；IF=1.95，Q2。
⚠️ 利益衝突：第二作者 Pedro P. Perez 任職於 Innovation Laboratories（PureWay-C® 製造商），非獨立研究者。本研究已被 Calder et al. 2025 系統性回顧（Nutrients Q1）獨立收錄確認。
```

---

## 範例：pureway-c_formula_immune.md

```markdown
---
chunk_id: pureway-c_formula_immune
chunk_type: formula
version: "2.0"

ingredient_id: pureway-c
ingredient_name: PureWay-C®

source_type: supplier_pdf
source_file: 03-美隆 - PUREWAY C 複方維生素C.pdf
created: 2026-04-25
updated: 2026-04-25

claims: [immune, anti_inflammatory]
evidence_level: supplier_claim
has_human_data: false
regulatory_jurisdiction: [taiwan, global]
regulatory_compliant: true

relations:
  - {rel: SYNERGIZES_WITH, target_id: zinc, target_type: ingredient}
  - {rel: SYNERGIZES_WITH, target_id: vitamin-d3, target_type: ingredient}
  - {rel: PERMITTED_BY, target_id: taiwan_fda, target_type: regulatory}
---

以下是 PureWay-C® 的免疫應用配方建議：

供應商推薦的免疫強化配方，適合感冒季節保健或免疫力低下族群（老年人、抽菸者、壓力族群）。

配方一（基礎型）：PureWay-C® 500 mg + 維生素 D3 25 mcg + 鋅（葡萄糖酸鋅）11 mg + 接骨木莓 50 mg + 芽孢益生菌 11.5 mg + 阿拉伯膠 200 mg。

配方二（高效型）：PureWay-C® 1,000 mg + 維生素 D3 25 mcg + 鋅 11 mg + 接骨木莓 600 mg。

台灣法規允許的功效宣稱：具抗氧化作用；促進膠原蛋白形成有助傷口癒合。台灣膠囊錠劑劑型每日維生素 C 上限 1,000 mg（衛福部規定）。

注意：以上為供應商配方建議，尚未經同儕審查驗證，不具 clinical evidence 效力。
```
