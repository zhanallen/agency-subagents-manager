# -*- coding: utf-8 -*-
import json
from pathlib import Path

translations_file = Path("data/translations_full.json")
with open(translations_file, "r", encoding="utf-8") as f:
    translations = json.load(f)

new_translations = {
  "specialized-healthcare-aging-parent-care-companion": {
    "name_zh": "長輩照護協調管家",
    "desc_zh": "專為照顧年邁父母的家庭照顧者打造之照護協調與決策支援專家，遵循 HIPAA 規範管理就醫行程、藥物提醒、照護團隊溝通與照顧者心理支持。",
    "vibe_zh": "每張藥物清單與就醫提醒背後都是養育你的父母與辛苦的照顧者。你需要的是一位可靠的夥伴，而不是另一件繁重的負擔。"
  },
  "specialized-chief-financial-officer": {
    "name_zh": "財務長 (CFO)",
    "desc_zh": "高階財務策略主管，主導資本配置、資金營運、財務規劃、併購財務分析、投資人關係與董事會報告，將複雜財務數據轉化為清晰的商業決策。",
    "vibe_zh": "以權衡取捨、風險調整後回報與長期價值為思考核心，在保護資產負債表與內部控制的同時，確保呈現的每個數字都具備公信力。"
  },
  "specialized-chief-of-staff": {
    "name_zh": "幕僚長 (Chief of Staff)",
    "desc_zh": "創辦人與高階主管的核心協調官，負責過濾雜訊、統籌跨部門流程、推動決策落地並優化產出影響力，協助領導者保持清晰思考。",
    "vibe_zh": "我不獨自擁有任何單一職能，我主導所有職能之間的協作空間。"
  },
  "specialized-codebase-archaeologist": {
    "name_zh": "程式碼考古與漂移檢測專家",
    "desc_zh": "專精於跨工作階段與多種 AI 工具（Claude、Cursor、Copilot、Windsurf）的程式碼漂移審計，找出單次對話無法察覺的邏輯脫節、死代碼與文件代碼分歧。",
    "vibe_zh": "我像解讀年輪般審視程式碼——能告訴你每一層是由哪雙手寫下，以及下一個人接手時留下了哪些未竟之處。"
  },
  "specialized-customer-service": {
    "name_zh": "全方位客戶服務專家",
    "desc_zh": "專業跨行業客服專案經理，以熱忱、高效與以客為尊的態度處理客戶諮詢、客訴處理、帳戶支援、常見問題解答與無縫工單升級。",
    "vibe_zh": "每一次與客戶的互動都是將問題轉化為忠誠度的契機——以細心、速度與人性溫度妥善處理。"
  },
  "specialized-data-consolidation-agent": {
    "name_zh": "銷售數據整合與報表代理",
    "desc_zh": "將分散的銷售數據彙整為即時視覺化儀表板，提供區域、業務代表與商機管道 (Pipeline) 的即時統整摘要。",
    "vibe_zh": "將零散的銷售數據轉化為清晰有力的即時決策儀表板。"
  },
  "specialized-data-privacy-officer": {
    "name_zh": "資料隱私長 (DPO)",
    "desc_zh": "企業資料隱私與合規主管，建構符合 GDPR、CCPA 與全球法規之隱私合規計畫，涵蓋資料對應、隱私影響評估、同意權管理與外包商盡職調查。",
    "vibe_zh": "將個人資料視為應盡量最小化的潛在風險而非隨意囤積的資產——從架構之初即融入隱私設計，隨時做好接受監管機構審查的準備。"
  },
  "specialized-document-generator": {
    "name_zh": "專業文件與報表生成專家",
    "desc_zh": "程式化文件生成專家，透過代碼自動化產出排版精美、內嵌圖表與資料視覺化之專業 PDF、PPTX、DOCX 與 XLSX 報表文件。",
    "vibe_zh": "用代碼生成極致專業的文件——簡報、試算表、PDF 與分析報告一氣呵成。"
  },
  "specialized-esg-sustainability-officer": {
    "name_zh": "ESG 與企業永續長",
    "desc_zh": "企業永續發展策略與 ESG 報告專家，建立環境、社會與公司治理計畫，主導減碳專案，並確保永續揭露符合國際框架與利害關係人期待。",
    "vibe_zh": "打造經得起嚴格檢驗的永續計畫——每項聲明皆有審計數據與國際框架佐證，杜絕任何漂綠風險。"
  },
  "specialized-french-consulting-market": {
    "name_zh": "法國顧問諮詢市場導航專家",
    "desc_zh": "解鎖法國 ESN/SI 自由接案與顧問生態系，精通利潤抽成模型、接案平台機制 (Malt, collective.work)、受薪承攬 (Portage Salarial) 與費率定價策略。",
    "vibe_zh": "深諳法國諮詢產業鏈的內部人士，讓自由工作者與顧問不再因為資訊不對稱而少賺收入。"
  },
  "specialized-grant-writer": {
    "name_zh": "補助款與基金專案企劃師",
    "desc_zh": "專為非營利組織、研究機構與社會企業撰寫補助申請書，涵蓋潛在資助方研究、意向書、完整企劃書、預算編列與獲獎後進度報告。",
    "vibe_zh": "申請補助不是乞求，而是建立一場使命與資源的對話——向資助方證明將資金投入在你的專案上是效益最高的投資。"
  },
  "specialized-hr-onboarding": {
    "name_zh": "人資入職與人才引導專家",
    "desc_zh": "全方位 HR 入職流程專家，主導新人培訓引導、合規文件簽署、福利登記、企業文化融入與第一年留任追蹤，打造卓越的新人入職體驗。",
    "vibe_zh": "前 90 天決定了一位新進同仁會成為長期核心貢獻者還是遺憾離職。從第一天起就把體驗做到極致。"
  },
  "specialized-healthcare-customer-service": {
    "name_zh": "醫療體系病患關懷專員",
    "desc_zh": "具同理心的醫療客服專家，處理病患諮詢、醫療帳單疑問、掛號與排程管理、保險理賠解答與向臨床/行政團隊無縫轉介。",
    "vibe_zh": "每位病患都值得被傾聽、尊重與支持——尤其在他們感到焦慮、困惑或身體不適時。"
  },
  "specialized-hospitality-guest-services": {
    "name_zh": "飯店與款待業賓客服務專家",
    "desc_zh": "飯店、度假村、餐飲與活動場地的貴賓服務主管，統籌預訂、入住/退房接待、禮賓管家服務、客訴處置、會員忠誠計畫與滿意度追蹤。",
    "vibe_zh": "款待不是冰冷的交易，而是一種溫暖的感受。每一次互動都是創造美好記憶與收穫五星好評的契機。"
  },
  "specialized-identity-graph-operator": {
    "name_zh": "身分識別圖譜運營官",
    "desc_zh": "維護多 AI 代理協同系統之共享身分圖譜，確保多代理在並行寫入與複雜查詢下，對「這個實體是誰」始終獲得具備一致性與確定性的權威解答。",
    "vibe_zh": "確保多代理架構中的每位成員對身分實體擁有絕對統一的認知標準。"
  },
  "specialized-korean-business-navigator": {
    "name_zh": "韓國商業文化與談判導航專家",
    "desc_zh": "為外籍專業人士解析韓國商業文化，掌握「稟議 (Pummi)」決策流程、「眼色 (Nunchi)」察言觀色、KakaoTalk 商務禮儀、階級體系與關係導向交易談判。",
    "vibe_zh": "西方直接風格與韓國人際動態之間的橋樑——精準閱讀現場氣氛，確保商業合作圓滿成交。"
  },
  "specialized-language-translator": {
    "name_zh": "即時語言翻譯與在地化專家",
    "desc_zh": "西班牙文 ↔ 英文即時翻譯專家，具備深厚文化語境理解、區域方言洞察與語氣調整能力，適用於商務談判、旅遊導覽與緊急應對情境。",
    "vibe_zh": "以母語者的敏銳度精準跨越語言與文化隔閡，在不同世界之間無縫傳遞意圖。"
  },
  "specialized-legal-billing-time-tracking": {
    "name_zh": "法律工時紀錄與帳單管理專家",
    "desc_zh": "專精於法律從業人員的精確工時記錄、帳單敘述撰寫、發票生成、款項催收與信託帳戶合規，在保障客戶關係的同時實現營收最大化。",
    "vibe_zh": "每 6 分鐘未計費的工時都是損失的價值。每筆模糊的帳單敘述都是未來的糾紛。精準記錄、清晰描述、專業請款。"
  },
  "specialized-legal-client-intake": {
    "name_zh": "法律諮詢初審與客戶接案專家",
    "desc_zh": "律所接案初審專員，負責潛在客戶資格篩選、案情資訊收集、律師諮詢預約、利益衝突審查並產出律師立即可用的接案摘要報告。",
    "vibe_zh": "與潛在客戶的第一次對話奠定了整個委任關係的基調。從一開始就做到溫暖、專業且滴水不漏。"
  },
  "specialized-legal-document-review": {
    "name_zh": "法律合約與訴訟文件審查專家",
    "desc_zh": "合約、訴訟文件與不動產協議審查專家，產出精準摘要、標註高風險條款、比對合約修訂版本並驗證法律合規性。",
    "vibe_zh": "法律文件中的每個字都至關重要。每個漏掉的條款都是潛在責任；及早發現的風險就是對客戶的最佳保護。"
  },
  "specialized-loan-officer-assistant": {
    "name_zh": "房貸與授信審查助理",
    "desc_zh": "房貸與金融借貸專家助理，協助借款人初審、資格預審、文件收集、進度管線追蹤、法規遵循、利率報價與對保撥款協調。",
    "vibe_zh": "每筆貸款都承載著客戶的成家或創業夢想。以精確度、合規性與真誠關懷推動案件順利核貸。"
  },
  "specialized-mcp-builder": {
    "name_zh": "Model Context Protocol (MCP) 開發專家",
    "desc_zh": "精通 Anthropic MCP 協議之專家，設計、構建與測試 MCP 伺服器，為 AI 代理串接自訂工具、資源存取與動態提示詞擴充能力。",
    "vibe_zh": "打造能讓 AI 代理真正與現實世界工具無縫互動的關鍵連接器。"
  },
  "specialized-organizational-psychologist": {
    "name_zh": "組織心理學與團隊健康顧問",
    "desc_zh": "應用組織心理學專家，診斷團隊動態、心理安全感、職場倦怠風險與組織文化健康，運用實證框架協助領導者打造高績效且具韌性的組織。",
    "vibe_zh": "像臨床醫師般診斷團隊功能失調——以同行評審的實證為依據，指出領導者未察覺的隱形盲點。"
  },
  "specialized-personal-growth-mentor": {
    "name_zh": "個人成長與習慣策略導師",
    "desc_zh": "跨領域個人成長教練，專注於目標釐清、習慣建立、重大策略決策與執行當責，拒絕空泛心靈雞湯，落實具體行動成果。",
    "vibe_zh": "系統重於口號，釐清先於行動，執行力勝過短暫的靈感。"
  },
  "specialized-real-estate-buyer-seller": {
    "name_zh": "不動產買賣與交易協調經紀人",
    "desc_zh": "房地產買賣專屬經紀人助理，協助買方/賣方代理、物件刊登管理、出價談判、交易流程協調與交屋過戶，提供世界級的置產體驗。",
    "vibe_zh": "每筆不動產交易都是客戶人生中最重大的財務決策之一。始終以專業、迅速回應與客戶最佳利益為最高原則。"
  },
  "specialized-report-distribution-agent": {
    "name_zh": "業務報表自動分發代理",
    "desc_zh": "依據業務區域、團隊權限與排程參數，自動將統整後的銷售與營運報表精準分發給指定業務代表與主管。",
    "vibe_zh": "在對的時間，將最關鍵的整合報表自動送達對的人手中。"
  },
  "specialized-resume-tailor": {
    "name_zh": "求職履歷客製優化專家",
    "desc_zh": "求職者導向的履歷優化師，深度解析職缺描述 (JD)，將真實經驗對齊職位要求，提高 ATS 關鍵字匹配度，在不捏造資歷的前提下打磨亮點。",
    "vibe_zh": "為職位量身打造最吸睛的履歷，絕不扭曲事實，只讓你的真實價值大放異彩。"
  },
  "specialized-retail-customer-returns": {
    "name_zh": "零售退換貨與逆向物流專員",
    "desc_zh": "零售實體與全通路退換貨專員，處理退款流程、退貨政策執行、防範詐欺、顧客留存與逆向物流分析，在降低損失的同時維護品牌忠誠度。",
    "vibe_zh": "退貨不是失敗，而是一次機會。以速度、公平與誠意妥善處理，失望的顧客也能轉化為忠實鐵粉。"
  },
  "specialized-sales-data-extraction-agent": {
    "name_zh": "Excel 銷售數據提取與監控代理",
    "desc_zh": "專門監控各業務單位 Excel 試算表，自動提取關鍵銷售指標（當月 MTD、年初至今 YTD、全年度預估）以供即時營運分析。",
    "vibe_zh": "緊盯你的 Excel 檔案，精準提取最重要的營運與銷售數據。"
  },
  "specialized-strategy-duel-agent": {
    "name_zh": "博弈論與三十六計策略對決專家",
    "desc_zh": "運用現代博弈論與東方三十六計智慧，展開即時商業與戰略兵棋推演對決，提供辛辣深刻的局勢分析與決策點評。",
    "vibe_zh": "以回合制策略對決拆解高難度戰局，為複雜競爭情勢提供犀利的推演視角。"
  },
  "specialized-study-abroad-advisor": {
    "name_zh": "全方位留學申請與職涯規劃顧問",
    "desc_zh": "涵蓋美、英、加、澳、歐、港、星的留學專家，精通本碩博申請策略、落點選校、自傳文書編修、背景提升、標化考試規劃與海外生活適應。",
    "vibe_zh": "以數據與實戰經驗引導學生走過留學申請的每一步——零焦慮行銷，全心專注於最適合的升學路徑。"
  },
  "specialized-zk-steward": {
    "name_zh": "卡片盒筆記法 (Zettelkasten) 知識管家",
    "desc_zh": "依循盧曼 (Niklas Luhmann) 卡片盒筆記法哲學打造之知識庫管家，落實原子筆記、雙向連結與知識驗證閉環，支援跨領域複雜決策思考。",
    "vibe_zh": "化身盧曼的卡片盒思維，構建具備生命力、相互連結且經得起驗證的個人外腦知識庫。"
  },
  "support-analytics-reporter": {
    "name_zh": "營運數據分析與視覺化專家",
    "desc_zh": "將原始營運資料轉化為可執行的商業洞察，設計即時儀表板、執行統計分析、追蹤 KPI 指標並提供策略決策視覺化報告。",
    "vibe_zh": "將冰冷的原始數據轉化為推動下一個關鍵決策的有力洞察。"
  },
  "support-executive-summary-generator": {
    "name_zh": "高階主管摘要與決策報告生成器",
    "desc_zh": "具備頂級顧問思維之 AI 專家，運用麥肯錫 SCQA、BCG 金字塔原理與 Bain 分析框架，將龐雜商業資訊濃縮為精煉的決策摘要。",
    "vibe_zh": "以麥肯錫資深顧問的邏輯思考，寫出讓執行長與董事會一目了然的決策精華。"
  },
  "support-finance-tracker": {
    "name_zh": "財務追蹤與預算控制顧問",
    "desc_zh": "專精於財務規劃、預算管控、現金流優化與企業營運績效分析，守護企業財務健康並提供成長預測建議。",
    "vibe_zh": "維持清晰健全的帳目，確保現金流順暢，並給予最誠實可靠的財務預測。"
  },
  "support-infrastructure-maintainer": {
    "name_zh": "雲端基礎架構維運與可靠性專家",
    "desc_zh": "專注於系統高可用性、效能調優與營運架構管理，維護具備彈性、可擴展且成本效益卓越的雲端與地端運算環境。",
    "vibe_zh": "確保伺服器穩定運轉、系統不中斷，並讓無效警報降到最低。"
  },
  "support-legal-compliance-checker": {
    "name_zh": "法律與法規合規性審查專員",
    "desc_zh": "跨司法管轄區的法律合規審查專家，確保企業營運、資料處理、商務合約與產出內容完全符合各國法規與產業安全標準。",
    "vibe_zh": "嚴格把關每一項營運環節，確保在所有關鍵市場均站穩合規防線。"
  },
  "support-responder": {
    "name_zh": "全方位客戶支援與滿意度專家",
    "desc_zh": "專門提供多通路客戶支援、疑難排解與使用者體驗優化，將每次客戶反饋轉化為對品牌的信任與正面評價。",
    "vibe_zh": "在每次溝通中解決問題，將受挫的使用者轉化為最忠實的品牌擁護者。"
  },
  "testing-api-tester": {
    "name_zh": "API 介面自動化測試工程師",
    "desc_zh": "API 驗證與介面效能專家，專注於端點功能測試、負載壓力評估、邊界條件校驗與第三方整合介面的品質防線。",
    "vibe_zh": "在使用者遇到問題之前，先替你找出 API 中的每一個脆弱環節。"
  },
  "testing-evidence-collector": {
    "name_zh": "視覺證據與驗收測試專家",
    "desc_zh": "以視覺截圖為依據的嚴格 QA 專家，拒絕空泛通過，預設找出 3~5 個潛在瑕疵，為所有功能驗收提供確鑿的視覺與執行證據。",
    "vibe_zh": "沒有截圖與日誌證明就不算完成——只對有憑有據的品質點頭。"
  },
  "testing-performance-benchmarker": {
    "name_zh": "系統效能基準評測與優化專家",
    "desc_zh": "專門衡量、分析並提升應用程式與底層架構的效能表現，執行壓力測試、延遲分析與資源瓶頸診斷。",
    "vibe_zh": "量測所有關鍵指標，優化真正重要的瓶頸，並用數據證明改善成效。"
  },
  "testing-reality-checker": {
    "name_zh": "上線門檻與實際上線驗收審查官",
    "desc_zh": "專門阻止盲目上線的最終品質守門員，預設維持「仍需修改 (NEEDS WORK)」標準，要求提供充分證據才允許部署至生產環境。",
    "vibe_zh": "預設保持懷疑態度——唯有經過壓倒性測試證明的代碼才配得上生產環境。"
  },
  "testing-test-results-analyzer": {
    "name_zh": "測試結果深度分析與品質洞察師",
    "desc_zh": "評估各項測試結果數據，分析品質指標分佈，從測試覆蓋率、錯誤日誌與回歸測試中提煉出可行的修復方針。",
    "vibe_zh": "像偵探解讀線索般剖析測試報告——不放過任何隱藏的系統弱點。"
  },
  "testing-tool-evaluator": {
    "name_zh": "技術工具與軟體選型評估專家",
    "desc_zh": "評估、測試並推薦最合適的軟體工具與開發平台，協助團隊提升生產力並避免在不合適的工具上浪費資源。",
    "vibe_zh": "嚴謹測試並推薦最適工具，讓團隊不再把寶貴時間浪費在錯誤的技術選型上。"
  },
  "testing-workflow-optimizer": {
    "name_zh": "開發與維運工作流程優化師",
    "desc_zh": "分析、簡化並自動化跨部門業務與開發工作流程，消除溝通阻礙與手動瓶頸，實現生產力最大化。",
    "vibe_zh": "找出瓶頸、重塑流程、將重複作業全面自動化。"
  }
}

translations.update(new_translations)

with open(translations_file, "w", encoding="utf-8") as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"Updated translations_full.json successfully. Total: {len(translations)}")
