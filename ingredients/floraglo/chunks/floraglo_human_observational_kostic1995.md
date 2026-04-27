---
chunk_id: floraglo_human_observational_kostic1995
chunk_type: clinical_study
version: "2.0"

ingredient_id: floraglo
ingredient_name: FloraGLO® 葉黃素（Lutein）

source_type: pubmed_abstract
source_url: https://pubmed.ncbi.nlm.nih.gov/7661123/
created: 2026-04-26
updated: 2026-04-26

claims: [absorption_interaction, formulation_antagonism, bioavailability]
evidence_level: human_observational
has_human_data: true
regulatory_jurisdiction: [global]
regulatory_compliant: unknown

relations:
  - {rel: USES, target_id: floraglo, target_type: ingredient}
  - {rel: ANTAGONIZES, target_id: beta-carotene, target_type: ingredient}
---

⚠️ 配方拮抗警告：以下是 FloraGLO® 葉黃素的吸收交互作用研究（Kostic 1995，AJCN，β-胡蘿蔔素拮抗）：

**研究概要**：Kostic et al.（1995），American Journal of Clinical Nutrition（Q1，IF≈9），PMID 7661123。n=8 健康成人，單次口服等摩爾量葉黃素（L）和/或 β-胡蘿蔔素（β-C），精確追蹤血清動態35天（13個採血點），愛荷華州立大學主導，NIH 政府基金（CA-46406）資助，無商業利益衝突。

**⚠️ 核心發現：β-胡蘿蔔素使葉黃素 AUC 降低 39–46%**

量化數據（P < 0.025，統計顯著）：
- 單獨葉黃素：AUC = 100%（基準）；血清峰值 16 小時
- 聯合 β-胡蘿蔔素：葉黃素 AUC 降至 **54–61%**（損失 39–46%）
- 反向：葉黃素使 β-胡蘿蔔素 AUC 降至 66%（損失 34%）
- 連帶：β-胡蘿蔔素→維生素A 代謝（視黃酯）AUC 也降至 74%
- 葉黃素本身吸收效率高於 β-胡蘿蔔素（AUC 59.6 vs 26.3 μmol·h/L，P < 0.005）

**競爭機制**：兩者共用腸道吸收途徑——SR-BI 和 CD36 轉運蛋白（腸上皮細胞頂端膜）、NPC1L1 蛋白、乳糜微粒脂質裝載空間均為有限容量，多種類胡蘿蔔素同時存在時必然產生競爭性抑制。β-胡蘿蔔素（更疏水）對乳糜微粒核心親和力更強，在競爭中優先排擠葉黃素。

**⚠️ 配方設計禁忌（直接應用）**：
1. FloraGLO® 葉黃素補充劑配方中**禁止含高劑量 β-胡蘿蔔素**——若配方含 10 mg 葉黃素 + β-胡蘿蔔素，使用者實際吸收的葉黃素可能只有 5.4–6.1 mg，吸收折損近一半，臨床有效性受損
2. 使用者**不宜同時服用**含 β-胡蘿蔔素的複合維生素；若必須，應至少間隔 4–6 小時
3. 含葉黃素 + β-胡蘿蔔素的複合配方在葉黃素吸收效率上存在內在缺陷

**AREDS 配方演進連結**：原版 AREDS（2001）含 β-胡蘿蔔素 15 mg（無葉黃素）；AREDS2（2013）移除 β-胡蘿蔔素，改用葉黃素 10 mg + 玉米黃素 2 mg。Kostic 1995 的拮抗數據是這一配方改革的藥動學依據之一。AREDS2 長期追蹤（Report 28，2022）確認葉黃素/玉米黃素配方 AMD 保護效益優於 β-胡蘿蔔素配方。

**注意**：本研究為急性單次給藥設計，長期日常膳食中的競爭效應（van het Hof 2000）較急性場景小，但在補充劑高劑量純化形式使用情境中，本研究的警示仍直接適用。
