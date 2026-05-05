# 使用說明

## 開啟 Claude Code 的方式（重要）

1. 在檔案總管中，找到這個 `skills-client` 資料夾
2. **Windows 11**：在資料夾空白處右鍵 → 點「在終端機中開啟」
   **Windows 10**：按住 Shift 鍵 + 右鍵 → 點「在此處開啟 PowerShell 視窗」
3. 在跳出的視窗中輸入 `claude`，按 Enter
4. 把下方「--- 開始複製 ---」到「--- 結束複製 ---」之間的全部文字複製，貼到 Claude Code 中，按 Enter

> 如果輸入 `claude` 出現「不是內部或外部命令」，表示 Claude Code 還沒安裝。
> 請先安裝 Node.js（https://nodejs.org 下載 LTS 版本），安裝完後在同一個視窗執行：
> `npm install -g @anthropic-ai/claude-code`
> 完成後重新執行步驟 3。

---

--- 開始複製 ---
你現在在 Windows 的 skills-client 目錄中。我是沒有軟體經驗的用戶，請用簡單的語言說明每個步驟的進度，遇到錯誤不要給我技術說明，直接告訴我「接下來要做什麼」。

請依序執行以下安裝，每步驟成功才繼續下一步。

---

**Step 1：確認目錄正確**
執行：python -c "import os; print('OK' if os.path.exists('product-page-to-md/SKILL.md') else 'WRONG_DIR')"

- 若輸出 OK → 繼續
- 若輸出 WRONG_DIR 或報錯 → 停止，告訴使用者：「請確認你是在 skills-client 資料夾內開啟終端機，而不是其他資料夾。請關閉視窗，重新在正確的資料夾右鍵開啟終端機。」

---

**Step 2：確認 Python 已安裝**
執行：python --version

- 若看到 Python 3.x.x → 繼續
- 若看到「不是內部或外部命令」或任何錯誤 → 停止，告訴使用者：
  「需要先安裝 Python。請：
  1. 用瀏覽器前往 https://www.python.org/downloads/
  2. 點擊黃色的「Download Python」按鈕
  3. 下載後執行安裝程式，安裝時務必勾選最下方的「Add Python to PATH」選項
  4. 安裝完成後，關閉這個視窗，重新在 skills-client 資料夾右鍵開啟終端機，再輸入 claude 重新開始」

---

**Step 3：安裝 Python 套件**
執行（一整行，不要分行）：
python -m pip install requests beautifulsoup4 youtube-transcript-api yt-dlp faster-whisper

等待安裝完成（可能需要 1–3 分鐘）。若出現紅色錯誤訊息，把錯誤訊息完整複製給我看。

安裝完成後，逐一驗證每個套件是否正確安裝：
python -c "import requests; print('requests OK')"
python -c "import bs4; print('beautifulsoup4 OK')"
python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('youtube-transcript-api OK')"
python -m yt_dlp --version
python -c "from faster_whisper import WhisperModel; print('faster-whisper OK')"

若任何一行出現錯誤：
- 若是 faster-whisper 失敗，先執行：python -m pip install --upgrade pip setuptools wheel 再重新安裝：python -m pip install faster-whisper
- 若是其他套件失敗，把錯誤訊息告訴使用者

---

**Step 4：安裝 ffmpeg**
先檢查是否已安裝：
python -c "import subprocess; r=subprocess.run(['ffmpeg','-version'],capture_output=True); print('ffmpeg 已安裝' if r.returncode==0 else 'ffmpeg 未安裝')"

若「ffmpeg 已安裝」→ 繼續 Step 5

若「ffmpeg 未安裝」→ 執行：
winget install --id Gyan.FFmpeg -e

等待安裝完成。安裝完成後，告訴使用者：
「ffmpeg 安裝完成！但需要重新啟動才能生效。請：
1. 關閉這個 Claude Code 視窗
2. 重新在 skills-client 資料夾右鍵開啟終端機
3. 輸入 claude 重新啟動 Claude Code
4. 重新貼上這個設定 prompt（從頭貼，之前的步驟會自動略過）」

然後停止，等使用者重新啟動。

若 winget 指令出現「不是內部或外部命令」，改用以下方式安裝 Chocolatey 再裝 ffmpeg（需要以系統管理員身份開啟 PowerShell）：

告訴使用者：「請在 Windows 搜尋列輸入 PowerShell，右鍵點擊 → 以系統管理員身份執行，然後貼上以下指令：
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
安裝完 Chocolatey 後，在同一個視窗執行：choco install ffmpeg -y
完成後重新開啟 Claude Code。」

---

**Step 5：複製 skills 到 Claude Code**
先確認 .claude 目錄存在（Claude Code 應已建立）：
mkdir "%USERPROFILE%\.claude\skills" 2>nul

執行以下兩個指令複製 skills：
xcopy /E /I /Y "product-page-to-md" "%USERPROFILE%\.claude\skills\product-page-to-md"
xcopy /E /I /Y "youtube-video-to-md" "%USERPROFILE%\.claude\skills\youtube-video-to-md"

若 xcopy 出現「找不到路徑」，告訴使用者：「請確認 Claude Code 已正確安裝。請關閉視窗，重新執行 npm install -g @anthropic-ai/claude-code 後再試。」

---

**Step 6：建立輸出資料夾**
執行：mkdir "C:\health-research\ingredients" 2>nul

（若資料夾已存在，2>nul 會靜默略過，屬正常）

---

**Step 7：最終確認**
逐一執行並回報結果：

python --version
python -m yt_dlp --version
python -c "import subprocess; r=subprocess.run(['ffmpeg','-version'],capture_output=True); print('ffmpeg OK' if r.returncode==0 else 'ffmpeg 未安裝')"
python -c "import os; print('product-page skill OK' if os.path.exists(r'%USERPROFILE%\.claude\skills\product-page-to-md\SKILL.md') else 'product-page skill 未安裝')"
python -c "import os; print('youtube skill OK' if os.path.exists(r'%USERPROFILE%\.claude\skills\youtube-video-to-md\SKILL.md') else 'youtube skill 未安裝')"
python -c "import os; print('輸出資料夾 OK' if os.path.exists(r'C:\health-research\ingredients') else '輸出資料夾未建立')"

若所有項目都 OK → 繼續 Step 8
若有任何項目失敗 → 針對失敗的項目重新執行對應步驟

---

**Step 8：開始使用**
全部確認後，告訴使用者：
「設定完成！所有工具已就緒。

請問你要做什麼？
A) 爬取保健品產品頁 → 請貼上你想分析的品牌產品頁網址
B) 整理 YouTube 影片 → 請貼上 YouTube 影片網址（有沒有字幕都可以）

請直接貼上網址，我就開始處理。」
--- 結束複製 ---
