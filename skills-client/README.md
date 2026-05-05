# Health Research Skills — Windows 安裝指南

這套 skills 讓 Claude Code 能幫你自動爬取保健品產品頁與 YouTube 影片知識，整理成結構化 Markdown 文件。

---

## 快速開始（99% 的情況用這個就夠了）

**只需要兩步：**

1. 安裝 **Node.js**：前往 [nodejs.org](https://nodejs.org/) 下載 LTS 版本並安裝（全部點下一步即可）

2. 安裝 **Claude Code**：安裝完 Node.js 後，開啟「命令提示字元」，貼上這行指令並按 Enter：
   ```
   npm install -g @anthropic-ai/claude-code
   ```

完成後，**在 Windows 檔案總管中找到 `skills-client` 資料夾，右鍵點擊空白處 → 「在終端機中開啟」**（Windows 10 請按住 Shift 再右鍵 → 「在此處開啟 PowerShell 視窗」），輸入 `claude` 啟動，然後照 `SETUP_PROMPT.md` 的說明操作，剩下的都會自動安裝好。

> **不需要**事先安裝 Python、ffmpeg 或其他任何東西——`SETUP_PROMPT.md` 裡的指令會自動幫你裝好並確認。

---

## 目錄

- [一、安裝 Claude Code CLI](#一安裝-claude-code-cli)
- [二、安裝 Python](#二安裝-python)
- [三、安裝 Python 套件](#三安裝-python-套件)
- [四、安裝 yt-dlp（YouTube skill 需要）](#四安裝-yt-dlp)
- [五、複製 Skills 到 Claude Code](#五複製-skills-到-claude-code)
- [六、確認輸出資料夾](#六確認輸出資料夾)
- [七、快速測試](#七快速測試)
- [八、使用說明](#八使用說明)

---

## 一、安裝 Claude Code CLI

1. 安裝 **Node.js**（v18 以上）：前往 [nodejs.org](https://nodejs.org/) 下載 LTS 版本並安裝。

2. 開啟「命令提示字元」或「PowerShell」，執行：
   ```
   npm install -g @anthropic-ai/claude-code
   ```

3. 驗證安裝成功：
   ```
   claude --version
   ```
   看到版本號即成功。

4. 啟動 Claude Code（首次執行需要登入 Anthropic 帳號）：
   ```
   claude
   ```

---

## 二、安裝 Python

建議安裝 **Python 3.11**（其他 3.x 也可以）。

1. 前往 [python.org/downloads](https://www.python.org/downloads/windows/)，下載 Python 3.11 Windows installer。
2. 安裝時 **一定要勾選「Add Python to PATH」**。
3. 驗證：
   ```
   python --version
   ```
   看到 `Python 3.11.x` 即成功。

> 已有 Anaconda / Miniconda 的用戶可跳過此步驟，但執行時請確認 `python` 指令可用。

---

## 三、安裝 Python 套件

開啟命令提示字元，逐行執行：

```
pip install requests beautifulsoup4
pip install youtube-transcript-api
pip install yt-dlp
```

驗證 yt-dlp：
```
yt-dlp --version
```

---

## 四、安裝 yt-dlp

`yt-dlp` 在上一步已透過 pip 安裝。若需要獨立執行檔版本（不需 Python）：

1. 前往 [github.com/yt-dlp/yt-dlp/releases](https://github.com/yt-dlp/yt-dlp/releases)
2. 下載 `yt-dlp.exe`，放到 `C:\Windows\System32\` 或其他 PATH 目錄。

### 選用：安裝 ffmpeg（部分影片格式需要）

`ffmpeg` 讓 yt-dlp 能合併高品質音訊和影片流。本 skill 目前**不需要下載影片**（只抓字幕），可暫時跳過。

若日後需要，安裝方式：
```
winget install ffmpeg
```
或前往 [ffmpeg.org](https://ffmpeg.org/download.html) 手動下載，將 `bin\` 目錄加入系統 PATH。

---

## 五、複製 Skills 到 Claude Code

Skills 需要放到 Claude Code 的 skills 目錄才能被啟用。

1. 找到你的 Claude Code 設定目錄：
   - 通常在 `C:\Users\你的名字\.claude\`
   - 若找不到，在 Claude Code 中輸入 `/config` 查看

2. 在 `.claude\` 下建立 `skills\` 目錄（若不存在）。

3. 將本包中的兩個 skill 資料夾複製進去：

   **複製前的結構**（本包）：
   ```
   skills-client\
   ├── README.md
   ├── product-page-to-md\
   │   ├── SKILL.md
   │   └── scripts\
   └── youtube-video-to-md\
       ├── SKILL.md
       └── scripts\
   ```

   **複製後的結構**（.claude 目錄）：
   ```
   C:\Users\你的名字\.claude\
   └── skills\
       ├── product-page-to-md\
       │   ├── SKILL.md
       │   └── scripts\
       └── youtube-video-to-md\
           ├── SKILL.md
           └── scripts\
   ```

   用命令提示字元執行（將 `你的名字` 換成你的 Windows 帳號名稱）：
   ```
   xcopy /E /I "skills-client\product-page-to-md" "C:\Users\你的名字\.claude\skills\product-page-to-md"
   xcopy /E /I "skills-client\youtube-video-to-md" "C:\Users\你的名字\.claude\skills\youtube-video-to-md"
   ```

---

## 六、確認輸出資料夾

所有處理後的資料會存放在你指定的「輸出根目錄」下。

建議先建立一個專用資料夾，例如：
```
C:\health-research\
└── ingredients\         ← 所有原料資料都在這裡
    ├── omega-3\
    │   ├── market\      ← 產品頁 Markdown + 圖片
    │   └── youtube\     ← YouTube 影片 Markdown
    ├── vitamin-c\
    │   ├── market\
    │   └── youtube\
    └── ...
```

建立指令：
```
mkdir C:\health-research\ingredients
```

每次使用 skill 時，Claude 會詢問你的輸出根目錄，填入 `C:\health-research\ingredients` 即可。

---

## 七、快速測試

安裝完成後，啟動 Claude Code 並輸入以下內容測試：

**測試產品頁爬取 skill：**
```
/product-page-to-md
```
Claude 會詢問你要爬哪些 URL，以及輸出到哪個資料夾。

**測試 YouTube skill：**
```
/youtube-video-to-md
```
Claude 會詢問你要處理哪些 YouTube 影片連結。

---

## 八、使用說明

### product-page-to-md（產品頁爬取）

**用途**：輸入品牌產品頁 URL，自動爬取文字與圖片，整理成結構化 Markdown。

**你需要提供**：
- 你要爬取的產品頁網址（一次可以給多個）
- 原料名稱（例如：Omega-3）
- Ingredient ID（目錄名，例如：`omega-3`）
- 輸出根目錄（例如：`C:\health-research\ingredients`）

**輸出位置**：
```
C:\health-research\ingredients\{ingredient-id}\market\
├── mkt_01_{品牌名}_{產品名}.md    ← 每個品牌一份 Markdown
├── mkt_02_{品牌名}_{產品名}.md
├── mkt_global_market-cases.md   ← 全域市場摘要
└── images\
    ├── mkt_01_{品牌名}\          ← 各品牌的產品圖片
    │   ├── img_01.jpg
    │   └── ...
    └── mkt_02_{品牌名}\
```

---

### youtube-video-to-md（YouTube 影片整理）

**用途**：輸入 YouTube 影片網址，自動抓取字幕並翻譯成中文，整理成結構化知識 Markdown。

**你需要提供**：
- YouTube 影片網址（一次可以給多個，例如 `https://www.youtube.com/watch?v=xxxxx`）
- 相關原料名稱（用於知識整理的標籤）
- Ingredient ID（目錄名）
- 輸出根目錄

**注意**：
- 只能處理有**英文字幕**的影片（手動或自動字幕皆可）
- 沒有英文字幕的影片會被跳過
- yt-dlp 和 youtube-transcript-api 必須已安裝

**輸出位置**：
```
C:\health-research\ingredients\{ingredient-id}\youtube\
├── yt_01_{頻道名}_{主題}.md    ← 每支影片一份 Markdown
├── yt_02_{頻道名}_{主題}.md
└── ...
```

---

## 常見問題

**Q：執行 `python` 出現「找不到指令」**
A：Python 未加入 PATH。重新安裝 Python，安裝時勾選「Add Python to PATH」。

**Q：執行 `yt-dlp` 出現「找不到指令」**
A：執行 `pip install yt-dlp` 後，重新開啟命令提示字元。

**Q：字幕抓取失敗**
A：可能是該影片沒有英文字幕，或該影片受地區限制。此 skill 只處理有英文字幕的影片。

**Q：爬取產品頁時出現 403 錯誤**
A：部分網站有防爬蟲機制，skill 會記錄並跳過，繼續處理其他 URL。

**Q：Claude Code 找不到 skill 指令**
A：確認 SKILL.md 已正確放到 `C:\Users\你的名字\.claude\skills\product-page-to-md\SKILL.md`。重新啟動 Claude Code。

---

## 支援

如有問題，請聯繫交付方。
