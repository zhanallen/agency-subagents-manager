# 🎭 Agency Subagents 2.0 - 繁體中文專家子代理與協同工作流管理器 (Windows 獨立 EXE 版)

專為 **Antigravity**、**Gemini CLI**、**Claude Code**、**Cursor** 及現代 AI Agent 打造的**繁體中文圖形化（GUI）Subagent 管理與協作規範分發器**。  
支援瀏覽、搜尋、篩選 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 中的 **255+ 位專業領域 AI 專家**，並將其**一鍵安裝為原生 Subagent（子代理）**與**啟用強制協作規範 (Rule)**！

---

## 🌟 2.0 核心特色與升級亮點

### 1. 🛡️ 一鍵啟用 Subagent 專家協作規範 (Rule)
- **告別 Main Agent 獨攬所有任務**：一鍵將嚴謹的協作工作流規則寫入當前專案之 `.agents/rules/subagent-collaboration.md`。
- **強制工作流原則**：
  - 💬 **專家討論先行 (Consult First)**：接收任務後，Main Agent 必須主動先與專屬領域 Subagent 討論方案與架構。
  - 🧩 **任務拆解與委派執行 (Deconstruct & Delegate)**：拆分子任務並指派各 Subagent 在獨立 Context 視窗中執行。
  - 🧪 **測試驗證與反饋閉環 (Test & Verification Loop)**：Subagent 執行完畢必須執行單元測試或驗證，Main Agent 依測試結果決定迭代修改或交付。

### 2. 📂 專案快速切換下拉選單 (MRU 歷史紀錄)
- 自動記錄最近使用過的專案目錄，頂部下拉選單即時一鍵切換，免去每次在檔案總管深層資料夾重新點選的困擾。

### 3. ⭐ 常用專家星標收藏 (Favorites)
- 點擊卡片右上角 ⭐ 即可加入「我的收藏」，配合側邊欄與篩選膠囊一鍵聚焦常用專家，支援 `localStorage` 本機持久化保存。

### 4. ⚡ 一鍵快速複製呼叫指令與任務模板
- 卡片與詳情視窗提供 **「@指令」** 一鍵複製按鈕，點擊即將 `@<agent-id>` 寫入剪貼簿。
- 詳情視窗提供 Antigravity、Claude Code、Cursor 各平台呼叫與任務指派語法範本。

### 5. ⌨️ 全域鍵盤快捷鍵支援
- **`Ctrl + K` / `Cmd + K`**：立刻聚焦頂部搜尋輸入框。
- **`ESC`**：關閉所有開啟的 Modal 彈窗或清空搜尋。

### 6. 📦 4 大推薦專家組合套裝 (Preset Packs)
- 🚀 **極速全端開發組** (Frontend Dev + Backend Architect + Python Engineer + Code Reviewer + Test Automator)
- 🛡️ **DevSecOps 與資安防禦組** (Security Auditor + Penetration Tester + Cloud Security + DevOps)
- 🎨 **UI/UX 產品體驗研究組** (UI Designer + UX Researcher + UX Architect + Product Manager)
- 📈 **增長黑客與數位行銷組** (SEO Specialist + Content Marketer + Growth Hacker + Paid Media)
- 支援一鍵打包安裝整個組合套件！

### 7. 📋 專案設定檔匯出 / 匯入 (`.json`)
- 一鍵將專案已安裝的 Subagent 清單匯出為 JSON 檔，或在其他專案一鍵匯入批次安裝，極大提升團隊標準化協作效率。

### 8. 📖 詳情視窗 3-Tab 升級
- **【角色總覽 (Overview)】**：中文職責摘要、特色 Vibe 引言、領域標籤。
- **【完整系統提示詞 (Persona)】**：語法高亮 Markdown 檢視與一鍵複製完整 Prompt。
- **【呼叫教學與範例 (Usage)】**：各平台叫用範本與一鍵複製。

---

## 🚀 使用方式

### 方式一：直接雙擊 EXE（最推薦）
直接雙擊根目錄下的 **[`AgencySubagentsManager.exe`](file:///d:/Code/AI/%E6%B5%81%E7%A8%8B%E7%AE%A1%E7%90%86/AgencySubagentsManager.exe)** 即可直接使用！

### 方式二：使用 Python 原始碼執行
```powershell
cd "d:\Code\AI\流程管理"
.venv\Scripts\python.exe app.py
```
啟動後打開瀏覽器前往：`http://localhost:8000`

---

## 💡 如何在 Antigravity 中使用安裝好的 Subagent 與 Rule？

1. **安裝 Subagent**：透過介面將專家安裝至目標專案之 `.agents/agents/*.md`。
2. **啟用協作 Rule**：點擊側邊欄或頂部的「一鍵啟用 Rule」，寫入 `.agents/rules/subagent-collaboration.md`。
3. **在 Antigravity 對話框中呼叫**：
   - 輸入 `@engineering-frontend-developer 請協助重構此元件並進行無障礙測試`。
   - 主助理 (Main Agent) 將自動遵循協作規範，與專家前置溝通並委派執行！

---

## 🙏 致謝與開源聲明 (Acknowledgements & Credits)

- 本專案中的 255+ 位專業領域 AI 專家提示詞庫源自於 [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) 專案。
- 特別感謝原作者 [@msitarzewski](https://github.com/msitarzewski) 與 [AgentLand Contributors](https://github.com/msitarzewski/agency-agents) 的傑出貢獻。
- 本專案基於 **MIT License** 進行二次開發，提供 100% 繁體中文在地化介面、單一 Windows 獨立執行檔 (EXE) 打包、Antigravity 原生 Subagent / 5 階段 Loop Engineering 協作規範分發等增強功能。

---

## 📄 開源授權 (License)

本專案採用 [MIT License](LICENSE) 授權開源。

