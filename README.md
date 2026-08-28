# 🎭 Agency Subagents 2.0 - 繁體中文專家子代理與協同工作流管理器

<p align="center">
  <a href="https://github.com/zhanallen/agency-subagents-manager/releases/latest">
    <img src="https://img.shields.io/github/v/release/zhanallen/agency-subagents-manager?color=6366f1&label=Latest%20Release&logo=github" alt="Latest Release">
  </a>
  <a href="https://github.com/zhanallen/agency-subagents-manager/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/zhanallen/agency-subagents-manager?color=3b82f6" alt="License">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-10b981?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Web-8b5cf6" alt="Platform Windows">
  <a href="https://github.com/msitarzewski/agency-agents">
    <img src="https://img.shields.io/badge/Upstream-msitarzewski%2Fagency--agents-f59e0b" alt="Upstream">
  </a>
</p>

專為 **Google Antigravity**、**Gemini CLI**、**Claude Code**、**Cursor** 及現代 AI Agent 打造的**繁體中文圖形化（GUI）Subagent 管理與協作規範分發器**。  
支援瀏覽、搜尋、篩選 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 中的 **255+ 位專業領域 AI 專家**，並將其**一鍵安裝為原生 Subagent（子代理）**與**啟用強制協作規範 (Rule)**！

---

## 📥 下載最新版 (Download)

> [!TIP]
> **Windows 使用者無需安裝 Python 或輸入任何指令，直接下載打包好的獨立執行檔即可使用！**

👉 **[前往 GitHub Releases 下載最新版 `AgencySubagentsManager.exe`](https://github.com/zhanallen/agency-subagents-manager/releases/latest)**

*(在 Releases 頁面下方的 **Assets** 區塊中點擊 `AgencySubagentsManager.exe` 下載)*

---

## 📖 5 步驟快速上手教學 (Quickstart Guide)

### 🔹 步驟 1：下載並啟動
前往 [Releases 頁面](https://github.com/zhanallen/agency-subagents-manager/releases/latest) 下載 `AgencySubagentsManager.exe`，下載後**直接雙擊執行**，即可開啟極簡現代桌面視窗。

### 🔹 步驟 2：選擇目標專案目錄
點擊頂部導航列的 **專案路徑下拉選單** 或點擊 **「瀏覽選擇其他專案」**，選擇您正在開發的程式碼專案資料夾（例如 `D:\Projects\MyApp`）。系統會自動記錄至最近專案歷史 (MRU) 中方便隨時切換。

### 🔹 步驟 3：一鍵啟用 Subagent 協作規範 (Rule)
點擊側邊欄或頂部的 **「一鍵啟用協作 Rule」** 按鈕：
- 系統將自動在您的專案目錄寫入 `.agents/rules/subagent-collaboration.md`。
- **5 階段閉環工作流 (Loop Engineering)**：強制要求主助理 (Main Agent) 在接收複雜任務時，必須先諮詢專家、拆解任務指派給 Subagent、執行自動化測試驗證，確保代碼品質。

### 🔹 步驟 4：挑選並安裝領域專家 (Subagents)
1. **瀏覽與搜尋**：透過側邊欄 17 大部門（軟體工程、視覺設計、資安、產品、測試、學術等）或按 `Ctrl + K` 搜尋 255+ 位繁中專家。
2. **一鍵安裝**：點擊專家卡片上的 **「安裝為 Subagent」**，檔案將自動寫入專案之 `.agents/agents/*.md`。
3. **推薦套裝 (Preset Packs)**：點擊頂部 📦 按鈕，可一鍵打包安裝「極速全端組」、「DevSecOps 資安組」、「UI/UX 設計組」等常用組合。

### 🔹 步驟 5：在 AI 編輯器中立即呼叫
打開 **Google Antigravity**、**Cursor** 或 **Claude Code**，在聊天對話框中輸入 `@<agent-slug>` 即可調用：
```markdown
@engineering-frontend-developer 請協助重構首頁卡片元件，並遵循無障礙 WCAG AA 標準進行測試。
```
主助理將自動根據協作規範，與專家前置溝通並在獨立視窗中委派執行！

---

## 🌟 核心特色與亮點

### 1. 🛡️ 高密度英文 Loop Engineering 協作規範 (Rule)
- **節省 60%~70% Token**：以高密度英文控制語料減少上下文消耗。
- **閉環驗證機制**：包含 `Consult` ➔ `Delegate` ➔ `Execute` ➔ `Automated Test Gate` ➔ `Iteration Loop` 5 大階段，杜絕 AI 盲目交付未經測試的代碼。

### 2. 🔄 雲端雙向智慧同步 (Auto Dual-Source Sync Engine)
- **協作規範與在地翻譯**：自動自 [zhanallen/agency-subagents-manager](https://github.com/zhanallen/agency-subagents-manager) 同步最新規範模板 (`data/rules/`) 與 100% 繁中翻譯字典 (`data/translations_full.json`)。
- **專家定義與最新提示詞**：自動自原作者官方倉庫 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 同步最新 255+ 位 AI 專家的原始 Markdown 提示詞。
- **專案 Rule 自動升級**：同步完成時，若當前專案已安裝 Rule，系統會自動將專案內的規範升級為最新版。

### 3. 🎨 極簡現代介面與防截斷排版 (Linear/Vercel-style)
- **卡片防截斷排版**：徹底解決長英文 Slug（如 `@engineering-inclusive-visuals-specialist`）與職稱被擠壓遮擋問題。
- **底部浮動操作 Dock**：批次管理按鈕平時收合，僅在選取專家時優雅滑入。
- **常用星標收藏 (Favorites)** 與 **專案歷史切換器 (MRU)**。
- **全域鍵盤快捷鍵**：`Ctrl + K` 搜尋、`ESC` 關閉彈窗。

---

## 💻 開發者手動建置與源碼執行 (For Developers)

如果您希望從 Python 原始碼執行或自行二次開發：

```powershell
# 1. 複製專案倉庫
git clone https://github.com/zhanallen/agency-subagents-manager.git
cd agency-subagents-manager

# 2. 建立虛擬環境並安裝依賴
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt

# 3. 啟動伺服器
.venv\Scripts\python.exe app.py
```
啟動後瀏覽器打開：`http://localhost:8000`

### 🔨 自行打包 Windows 獨立 EXE
```powershell
pyinstaller --clean -y --onefile --noconsole --name AgencySubagentsManager --collect-all uvicorn --collect-all fastapi --collect-all starlette --collect-all pydantic --collect-all anyio --collect-all webview --add-data "static;static" --add-data "data;data" --add-data "services;services" app.py
```

---

## 🙏 致謝與開源聲明 (Acknowledgements & Credits)

- 本專案中的 255+ 位專業領域 AI 專家提示詞庫源自於 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 專案。
- 特別感謝原作者 [@msitarzewski](https://github.com/msitarzewski) 與 [AgentLand Contributors](https://github.com/msitarzewski/agency-agents) 的傑出貢獻。
- 本專案基於 **MIT License** 進行二次開發，提供 100% 繁體中文在地化介面、單一 Windows 獨立執行檔 (EXE) 打包、Antigravity 原生 Subagent / 5 階段 Loop Engineering 協作規範分發等增強功能。

---

## 📄 開源授權 (License)

本專案採用 [MIT License](LICENSE) 授權開源。


