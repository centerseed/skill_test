---
name: youtube-video-to-md
description: >
  用戶直接指定 YouTube 影片網址，優先抓取英文字幕，無字幕時自動下載音訊並用 Whisper 語音辨識，
  翻譯成繁體中文，整理成結構化 MD 知識文件，存放到 {OUTPUT_ROOT}/{ingredient_id}/youtube/ 目錄。
  三個步驟：字幕/語音辨識 → 知識整理（parallel subagents）→ 輸出 MD。
  當使用者說「整理這些 YouTube 影片」「抓影片知識」「youtube-video-to-md」
  「幫我整理這個影片」「建立影片知識庫」時一定要使用這個 skill。
version: 2.1.0
---

# /youtube-video-to-md

用戶指定 YouTube 影片 URL，抓取字幕翻譯後整理成結構化 MD。

依賴：`yt-dlp`、`youtube-transcript-api`、`faster-whisper`、`ffmpeg`
（`python -m pip install yt-dlp youtube-transcript-api faster-whisper`，ffmpeg 需另外安裝）

## 輸出結構

```
{OUTPUT_ROOT}\{ingredient_id}\youtube\
├── yt_01_{channel-slug}_{topic-slug}.md
├── yt_02_{channel-slug}_{topic-slug}.md
├── ...
└── yt_07_{channel-slug}_{topic-slug}.md
```

## 執行前確認

詢問使用者（若對話中已知則跳過）：
1. **YouTube 影片網址清單**（必填）  
   例如：
   ```
   https://www.youtube.com/watch?v=ABC123
   https://www.youtube.com/watch?v=XYZ789
   ```
   可以一次提供多個連結（每行一個）。
2. **相關原料名稱**？例如 "Omega-3"、"PureWay-C"（用於知識文件的標籤）
3. **Ingredient ID**（目錄名）？例如 `omega-3`、`pureway-c`
4. **輸出根目錄**？（Windows 預設：`C:\health-research\ingredients`）

---

## ⚠️ 核心執行原則

**每一支影片必須是獨立的 subagent，嚴禁批次處理。**

- Step 2（知識整理）：每支影片一個獨立 subagent，不得將多支影片塞入同一 agent
- 品質目標：每支影片 MD 目標 150–300 行，完整覆蓋所有時間戳段落
- 平行上限：同時最多 7 個 subagent

**orchestrator 只負責：接收 URL、抓字幕、調度 subagent、彙整結果。不得自己直接寫影片 MD。**

---

## 輸入處理：解析使用者提供的 URL

從使用者提供的 YouTube 網址提取影片資訊：

```
對每個 URL，用 yt-dlp 取得影片元數據：

執行（命令提示字元）：
yt-dlp --dump-json --no-warnings --no-playlist "{URL}"

從輸出 JSON 提取：
- id：影片 ID
- title：影片標題
- view_count：觀看數
- duration：時長（秒）
- uploader：頻道名稱
- webpage_url：完整 URL

建立：
- rank：01, 02, ... （依 URL 順序，兩位數補零）
- channel_slug：頻道名小寫、空格替換為 -、取前 20 字元
- topic_slug：標題關鍵詞小寫、空格替換為 -、取前 25 字元
- transcript_path：%TEMP%\transcript_{VIDEO_ID}.json
- output_filename：yt_{rank}_{channel_slug}_{topic_slug}.md
```

若 yt-dlp 無法取得元數據，從 URL 提取影片 ID 並以 URL 本身作為標題。

---

## Step 1：逐字稿擷取（依序執行）

**為每支影片取得逐字稿，存成 JSON。腳本自動判斷用字幕還是語音辨識。**

```
SKILL_DIR = skill 目錄的絕對路徑（SKILL.md 所在目錄）

對每支影片，執行：
python "{SKILL_DIR}\scripts\fetch_transcript.py" {VIDEO_ID} "%TEMP%\transcript_{VIDEO_ID}.json"

腳本執行邏輯（自動）：
1. 優先抓取手動英文字幕
2. 若無手動字幕，嘗試自動英文字幕
3. 若無任何英文字幕 → 用 yt-dlp 下載音訊，再用 Whisper (base model) 語音辨識

輸出：%TEMP%\transcript_{VIDEO_ID}.json（格式相同，不論來源）
失敗時（exit code 非 0）：記錄跳過，不中止流程
```

回報給 orchestrator 時，說明每支影片的逐字稿來源：
- `[subtitle]`：有英文字幕，速度快
- `[whisper]`：無字幕，語音辨識，**長影片需數分鐘**，MD 品質略低（辨識偶有錯字）

---

## Step 2：知識整理（parallel subagents）

**為每支有字幕的影片各派一個 subagent，同時執行，互不干擾。**

每個 subagent 的完整 prompt：

```
你是一個 YouTube 影片知識整理員。

=== 輸入 ===
字幕 JSON 路徑：%TEMP%\transcript_{VIDEO_ID}.json
影片資訊：
  - 標題：{TITLE}
  - 頻道：{UPLOADER}
  - 觀看數：{VIEW_COUNT}
  - 時長：{DURATION_MIN}:{DURATION_SEC}
  - URL：{URL}
  - 相關原料：{INGREDIENT_NAME}

=== 輸出路徑 ===
{OUTPUT_ROOT}\{ingredient_id}\youtube\{OUTPUT_FILENAME}

=== 執行步驟 ===

1. 讀取字幕 JSON（Read tool 讀取 %TEMP%\transcript_{VIDEO_ID}.json）

2. 完整瀏覽所有 segments，建立對影片的全局理解

3. 依照以下格式輸出 MD 文件：

--- MD 格式開始 ---
# {TITLE}

**來源**: YouTube
**頻道**: {UPLOADER}
**觀看數**: {VIEW_COUNT_FORMATTED}（加逗號千分位）
**時長**: {DURATION_MIN}:{DURATION_SEC}
**URL**: {URL}
**整理日期**: {TODAY}
**相關原料**: {INGREDIENT_NAME}

---

## 影片摘要

（150-250字的中文摘要，涵蓋：影片主題、主要論點、對原料的評價或提及方式）

---

## 重點整理（中文）

### [{MM:SS}] {小節標題}

（以原字幕的時間戳為分節依據，每節：
- 完整保留該段的說話內容與論述脈絡，用段落文字呈現，保留推論過程、舉例、轉折
- 保留所有數字：劑量、百分比、研究天數、受試者人數、倍數
- 若提及品牌或產品名稱（如 PureWay-C、Ester-C）完整保留
- 目標是讓讀者不看影片也能獲得幾乎等量的資訊
- 【可刪除】重複說了三遍以上的同一觀點只保留一次；口語填充詞；純廣告段落）

（重複上述結構，覆蓋影片主要段落，一般 5-12 個小節）

---

## 關鍵數據與引用

（條列所有數字性主張與出處，格式：
- 數字/結論：...
  - 來源：影片時間 {MM:SS}，原文：「...」）

---

## 對 {INGREDIENT_NAME} 的提及

（若影片有直接提及該原料，整理相關評論、比較、推薦語）
（若無直接提及，填「本影片未直接提及」）
--- MD 格式結束 ---

⚠️ **格式鎖定：以上四個 section 是輸出的全部，嚴禁在「對 {INGREDIENT_NAME} 的提及」之後新增任何額外節（如「完整字幕摘錄」「頻道背景」「補充說明」等）。多餘的節一律不輸出。**

4. 將 MD 寫入輸出路徑（建立目錄若不存在）

=== 完成後回報 ===
- 輸出路徑
- 字幕 segment 數量
- 產出 MD 的主要小節數
- 是否有直接提及 {INGREDIENT_NAME}
```

**注意：所有 subagent 在同一個 Agent tool 呼叫中一起 spawn，讓它們並行執行。**

---

## Step 3：彙整結果

完成後向使用者回報：
1. 成功處理幾支影片 / 總共幾支
2. **輸出目錄路徑**（方便用戶直接開啟）：`{OUTPUT_ROOT}\{ingredient_id}\youtube\`
3. 各 MD 檔名 + 觀看數 + 是否有提及目標原料
4. 哪些影片因無字幕而跳過

---

## 注意事項

- **逐字稿來源**：優先字幕（快）→ 自動降級 Whisper 語音辨識（慢，但有結果）
- **Whisper 首次執行**：自動下載 base model（約 145MB），只下載一次，之後快取在本機
- **Whisper 速度**：CPU 模式，10 分鐘影片約需 3–5 分鐘辨識，請耐心等候
- **Whisper 辨識品質**：英文辨識準確率高，偶有人名/專有名詞錯字，知識整理 subagent 處理時可修正
- **ffmpeg 必要**：無字幕時需要 ffmpeg 下載音訊；安裝方式：`winget install ffmpeg`
- **Slug 規則**：只用英文小寫、數字、連字號，去掉特殊字元
- **日期**：用當天日期（YYYY-MM-DD）
- **Python 環境**：使用 `python`（Windows 上確認已加入 PATH）
- **路徑**：若輸出目錄不存在，script 會自動建立
