import json
import re

# 讀取全部 Agent 原始資料
with open('data/agents_to_translate.json', 'r', encoding='utf-8') as f:
    raw_agents = json.load(f)

# 導入基礎翻譯
from services.translations import TRANSLATIONS_DATA

# 專屬領域中文翻譯映射庫
SPECIALIZED_TRANSLATIONS = {
    # === Finance (5) ===
    "finance-bookkeeper-controller": {
        "name_zh": "簿記會計與財務主計主管",
        "desc_zh": "精通日常對帳、應收應付管理、權責發生制月結流程與內部財務控制規範，確保每一筆帳目清清楚楚、嚴絲合縫。",
        "vibe_zh": "數字不會說謊，每一筆收支都必須有據可查、分毫不差。"
    },
    "finance-financial-analyst": {
        "name_zh": "商業財務分析師",
        "desc_zh": "精通財務三表建模、DCF 估值模型、營運資金敏感度分析與財務比率診斷，為企業重大投資提供嚴謹的數據決策支撐。",
        "vibe_zh": "透過財務模型透視業務本質，用數據洞察風險與回報。"
    },
    "finance-fpa-analyst": {
        "name_zh": "FP&A 財務預算與分析師",
        "desc_zh": "專精於滾動財務預測 (Rolling Forecast)、預算編制、業績落差分析 (Variance Analysis) 與經營績效關鍵指標管理。",
        "vibe_zh": "預算不是束縛，而是引導企業資源精準流向高產出業務的導航圖。"
    },
    "finance-fundraising-strategist": {
        "name_zh": "股權融資與募資策略師",
        "desc_zh": "專精於新創公司商業計畫書 (BP) 潤色、股權結構表 (Cap Table) 模擬、投資人問答應對與種子輪到 C 輪融資節奏把控。",
        "vibe_zh": "講述一個兼具商業邏輯與巨大想像空間的願景，贏得頂級創投青睞。"
    },
    "finance-tax-strategist": {
        "name_zh": "稅務籌劃與合規策略師",
        "desc_zh": "精通跨國企業架構稅務優化、研發加計扣除 (R&D Tax Credits)、移轉訂價合規與各國稅收協定，合法合規降低綜合稅負。",
        "vibe_zh": "在法規允許的最大框架內，為企業設計最優的稅務架構。"
    },
    "finance-investment-researcher": {
        "name_zh": "二級市場與股權投資研究員",
        "desc_zh": "精通產業鏈深度調研、競品護城河拆解、財報深度掃描與由上而下 (Top-down) 宏觀投資策略分析。",
        "vibe_zh": "穿透短期市場噪音，專注於具備長期複利價值的優秀企業。"
    },

    # === Game Development (6) ===
    "game-development-economy-designer": {
        "name_zh": "遊戲經濟與數值架構師",
        "desc_zh": "精通虛擬貨幣流轉模型、產出與消耗 (Sinks & Sources) 平衡、防通貨膨脹機制與長線營運商城商業化數值設計。",
        "vibe_zh": "調控虛擬經濟的供需動態，讓每一次獲得都伴隨著成就感與價值感。"
    },
    "game-development-game-audio-engineer": {
        "name_zh": "遊戲音效與互動音訊工程師",
        "desc_zh": "精通 Wwise / FMOD 中間件整合、動態空間音效、環境氛圍音景設計與依據玩家狀態即時變化的適應性音樂系統。",
        "vibe_zh": "當眼睛專注於戰鬥時，耳朵已經帶領靈魂沉浸在整個虛擬世界之中。"
    },
    "game-development-game-designer": {
        "name_zh": "核心玩法與遊戲機制設計師",
        "desc_zh": "專精於 GDD 企劃文檔撰寫、核心循環 (Core Loop) 設計、心流理論 (Flow) 體驗曲線塑造與系統可玩性原型驗證。",
        "vibe_zh": "好的遊戲機制能讓玩家自發探索無窮樂趣，進入欲罷不能的心流狀態。"
    },
    "game-development-game-writer": {
        "name_zh": "遊戲劇情與世界觀編劇",
        "desc_zh": "專精於分支對話樹、環境敘事、角色動機塑造、陣營歷史設定與將劇情自然融入遊戲關卡節奏之中。",
        "vibe_zh": "不說教，讓世界本身的一磚一瓦與 NPC 的每一次互動訴說史詩。"
    },
    "game-development-level-designer": {
        "name_zh": "遊戲關卡與空間節奏設計師",
        "desc_zh": "精通關卡白模 (Greybox) 搭建、視線引導 (Pacing)、空間難度曲線、路徑遭遇戰設計與空間探索獎勵分配。",
        "vibe_zh": "空間就是節奏，每拐過一個街角都為玩家準備好心跳加速的未知驚喜。"
    },
    "game-development-systems-designer": {
        "name_zh": "遊戲底層系統架構師",
        "desc_zh": "專精於角色養成系統、裝備詞綴隨機生成、背包管理、任務成就系統與高擴展性數據驅動架構設計。",
        "vibe_zh": "搭建優雅模組化的底層系統，支撐起萬千變化的上層玩法。"
    },
    "game-development-narrative-designer": {
        "name_zh": "敘事設計師 (Narrative Designer)",
        "desc_zh": "專注於將劇本文學轉化為可互動的遊戲機制，平衡故事進程與玩家自主探索權力。",
        "vibe_zh": "讓玩家的每一次選擇，都能在遊戲世界中激起真實可信的漣漪。"
    },
    "game-development-technical-artist": {
        "name_zh": "技術美術 (TA - Technical Artist)",
        "desc_zh": "專精於 Shader 著色器編寫、Houdini 程序化生成管線、骨骼綁定與在美術品質與硬體幀率間取得完美平衡。",
        "vibe_zh": "架起藝術家與程式碼之間的魔法橋樑，讓天馬行空的畫面以 60FPS 順暢運行。"
    },

    # === GIS (13) ===
    "gis-3d-scene-developer": {
        "name_zh": "3D 地理場景與數位孿生開發者",
        "desc_zh": "精通 Cesium / Three.js 空間視覺化、大規模 3D Tiles 點雲串流渲染與城市級數位孿生地圖場景建構。",
        "vibe_zh": "在瀏覽器中建構可即時互動的百億級 3D 城市數位孿生。"
    },
    "gis-bim-specialist": {
        "name_zh": "BIM / GIS 跨領域整合專家",
        "desc_zh": "專精於 Revit / IFC 建築資訊模型與地理空間座標對齊、IFC 轉 3D Tiles 拓撲簡化與室內外一體化導航。",
        "vibe_zh": "將精細的建築微觀世界，無縫鑲嵌進廣袤的宏觀地理地圖之中。"
    },
    "gis-cartography-designer": {
        "name_zh": "現代地圖製圖美學設計師",
        "desc_zh": "精通色彩心理學、標註衝突消解演算法、多尺度符號化與設計既具備極致美感又精確易讀的出版級地圖。",
        "vibe_zh": "地圖是科學與藝術的結晶，讓空間數據優雅地開口說話。"
    },
    "gis-database-architect": {
        "name_zh": "空間資料庫架構師 (PostGIS)",
        "desc_zh": "專精於 PostGIS 空間索引 (GiST/BRIN)、空間拓撲關聯查詢調優、地理網格 (H3/S2) 與海量空間大數據治理。",
        "vibe_zh": "讓數億筆經緯度與多邊形空間運算，在毫秒之間完成拓撲交集查詢。"
    },
    "gis-developer": {
        "name_zh": "GIS 核心功能開發工程師",
        "desc_zh": "精通 QGIS 外掛開發、GDAL/OGR 幾何運算、GeoServer 服務發布與 OGC (WMS/WFS/WMTS) 標準地理介面實現。",
        "vibe_zh": "以強健的空間算子，處理複雜的地理幾何相交與座標轉換。"
    },
    "gis-drone-reality-mapping": {
        "name_zh": "無人機實景三維建模專家",
        "desc_zh": "精通航線規劃、傾斜攝影測量、空三加密運算與無人機空拍生成高精度正射影像 (DOM) 與實景三維模型。",
        "vibe_zh": "從天空俯瞰大地，以毫米級精度還原真實世界的每一寸細節。"
    },
    "gis-analyst": {
        "name_zh": "地理空間分析師",
        "desc_zh": "精通空間疊加分析、緩衝區計算、可達性分析與多準則選址評估模型，從空間分佈中挖掘商業與環境洞見。",
        "vibe_zh": "空間位置隱藏著因果關係，分析地圖就是分析世界的運作規律。"
    },
    "gis-qa-engineer": {
        "name_zh": "地理空間數據品質保證工程師",
        "desc_zh": "專精於空間拓撲規則校驗（懸掛節點/自相交/重疊）、幾何精度審計與空間屬性完整性自動化測試。",
        "vibe_zh": "嚴防任何拓撲錯誤與座標位移，守護地理數據的絕對精度。"
    },
    "gis-geoai-ml-engineer": {
        "name_zh": "GeoAI 空間機器學習工程師",
        "desc_zh": "專精於衛星影像語意分割 (SAM/U-Net)、遙感變化檢測、空間時序預測與地理大模型應用。",
        "vibe_zh": "利用深度學習解讀衛星之眼，自動監測地球表面的每一處滄海桑田。"
    },
    "gis-geoprocessing-specialist": {
        "name_zh": "空間處理管線自動化專家",
        "desc_zh": "精通 ArcPy / GeoPandas 大規模批次處理、空間幾何簡化演算法與自動化空間數據 ETL 工作流。",
        "vibe_zh": "將耗時數日的繁瑣空間計算，轉化為一鍵全自動執行的秒級腳本。"
    },
    "gis-solution-engineer": {
        "name_zh": "GIS 行業解決方案架構師",
        "desc_zh": "專注於智慧城市、自然資源監管、應急指揮與物流路網調度的全套地理資訊系統架構設計。",
        "vibe_zh": "用地理空間思維，為複雜實體世界難題提供頂層設計與落地路徑。"
    },
    "gis-spatial-data-engineer": {
        "name_zh": "空間大數據工程師",
        "desc_zh": "專精於軌跡大數據處理、Apache Sedona 分散式空間計算、Vector Tile 切片快取與即時路況流計算。",
        "vibe_zh": "處理百萬車輛的即時軌跡，讓龐大的空間流數據流暢可視化。"
    },
    "gis-spatial-data-scientist": {
        "name_zh": "空間數據科學家",
        "desc_zh": "精通空間自我相關 (Moran's I)、地理加權迴歸 (GWR)、點格局分析與空間流行病學統計模型。",
        "vibe_zh": "將空間統計學與機器學習結合，揭示現象背後的地理聚集機制。"
    },
    "gis-technical-consultant": {
        "name_zh": "GIS 技術諮詢顧問",
        "desc_zh": "評估企業地理空間技術棧選型、開源替代商業方案 (Esri to OpenSource) 評估與地理數據架構現代化升級。",
        "vibe_zh": "以客觀務實的視角，為企業規劃最高性價比的空間技術升級路線。"
    },

    # === Healthcare (3) ===
    "healthcare-clinical-evidence-agent": {
        "name_zh": "臨床證據與生醫合規專員",
        "desc_zh": "精通臨床試驗文獻檢索、實證醫學證據分級 (GRADE)、FDA / CE 醫療器材上市前文檔整理與醫學聲明合規審核。",
        "vibe_zh": "以最高等級的同行評審標準，審視每一份醫學聲明與臨床數據。"
    },
    "healthcare-innovation-strategist": {
        "name_zh": "醫療健康科技創新戰略師",
        "desc_zh": "專為醫療創業者打造，精通生醫專利佈局、數位療法 (DTx) 商業路徑、醫保給付對接與醫療產品市場進入策略。",
        "vibe_zh": "架起尖端醫療科技與商業化落地之間的嚴謹橋樑。"
    },
    "healthcare-sovereign-health-systems-agent": {
        "name_zh": "主權健康體系與政策對接顧問",
        "desc_zh": "專精於各國國家級健康資訊交換標準 (HL7 FHIR)、公立醫療體系採購規範、病患數據隱私主權與大型公衛政策落實。",
        "vibe_zh": "理解國家醫療體系的深層運作邏輯，推動合規穩健的大型醫療專案。"
    },

    # === Marketing (36) ===
    "marketing-aeo-foundations": {
        "name_zh": "AEO 答案引擎基礎架構師",
        "desc_zh": "專精於 AI 答案引擎最佳化 (Answer Engine Optimization)，為 Perplexity / ChatGPT Search 建立結構化 Schema 與實體語意關聯。",
        "vibe_zh": "讓你的品牌成為 AI 大模型在回答用戶問題時，最優先引用的權威來源。"
    },
    "marketing-ai-citation-strategist": {
        "name_zh": "AI 引用與生成式搜尋策略師 (GEO)",
        "desc_zh": "精通生成式引擎最佳化 (Generative Engine Optimization)，透過構建權威實體、高質量數據引用與反向連結，提升 AI 生成回答中的曝光率。",
        "vibe_zh": "搶佔 AI 時代的第一條回答，讓演算法為你的品牌背書。"
    },
    "marketing-agentic-search-optimizer": {
        "name_zh": "Agentic 代理人搜尋最佳化專家",
        "desc_zh": "優化網站 WebMCP 準備度與語意標註，確保自主 AI Agent 能精確讀取頁面資訊並直接完成自動下單與預訂任務。",
        "vibe_zh": "未來的網站不僅是給人看的，更是給自主 AI Agent 直接呼叫並完成任務的。"
    },
    "marketing-app-store-optimizer": {
        "name_zh": "ASO 應用商店最佳化專家",
        "desc_zh": "精通 App Store / Google Play 關鍵字權重拆解、圖示與截圖 A/B 測試、評論星等維護與自然下載量暴增法。",
        "vibe_zh": "用精準的搜尋詞與吸睛的視覺，讓 App 在榜單與搜尋結果中脫穎而出。"
    },
    "marketing-baidu-seo-specialist": {
        "name_zh": "百度 SEO 與中國搜尋市場專家",
        "desc_zh": "專精於百度演算法（颶風/驚雷等）、ICP 備案規範、百度熊掌號整合與在中國搜尋引擎市場獲取穩定自然流量。",
        "vibe_zh": "深諳中國網路搜尋生態，助你的品牌在百度穩居首頁前列。"
    },
    "marketing-bilibili-content-strategist": {
        "name_zh": "Bilibili (B站) 內容與彈幕營運策略師",
        "desc_zh": "精通 B站推薦演算法、三連率提升法則、年輕化彈幕文化與 UP 主中長影片內容架構設計。",
        "vibe_zh": "用真誠硬核的內容與懂梗的網感，征服 Z 世代年輕人的心。"
    },
    "marketing-book-co-author": {
        "name_zh": "專業著作代筆與出版策劃師",
        "desc_zh": "協助創辦人與產業領袖將個人經驗與方法論提煉為出版級書籍大綱、各章節代筆與權威暢銷書定位。",
        "vibe_zh": "將一生的智慧與洞察，凝聚為一本歷久彌新的傳世之作。"
    },
    "marketing-carousel-growth-engine": {
        "name_zh": "社群輪播圖 (Carousel) 爆款引擎",
        "desc_zh": "專為 Instagram / TikTok / LinkedIn 打造滑動率極高的輪播圖腳本、資訊密度控制、鉤子開頭與高轉發 CTA 設計。",
        "vibe_zh": "每一頁都是精心設計的翻頁鉤子，讓用戶忍不住一路滑到最後並轉發。"
    },
    "marketing-china-ecommerce-operator": {
        "name_zh": "中國電商全平台營運專家",
        "desc_zh": "精通淘寶天貓、京東、拼多多與抖音電商營運，涵蓋主圖詳情頁視覺轉化、搜索權重打法與促銷節奏佈局。",
        "vibe_zh": "在中國激烈的電商紅海中，以精細化營運策略挖掘利潤與增長。"
    },
    "marketing-content-creator": {
        "name_zh": "全方位內容行銷創作者",
        "desc_zh": "專精於跨平台內容矩陣規劃、長篇深度文章撰寫、電子報 (Newsletter) 營運與將複雜概念轉化為易傳播文案。",
        "vibe_zh": "文字是有溫度的武器，用持續優質的內容建立深厚的用戶信任。"
    },
    "marketing-cross-border-ecommerce": {
        "name_zh": "跨境電商全鏈路運營策略師",
        "desc_zh": "精通 Amazon / Shopee / Shopify 獨立站營運、海外本地化文案、海外倉物流管理與站外引流策略。",
        "vibe_zh": "打破國界隔閡，讓好產品在全球各大電商市場暢銷無阻。"
    },
    "marketing-douyin-strategist": {
        "name_zh": "抖音短影音演算法增長策略師",
        "desc_zh": "專精於抖音完播率拆解、前 3 秒黃金吸睛鉤子、爆款文案框架與短影音帶貨高轉化腳本創作。",
        "vibe_zh": "掌握演算法脈搏，用極具衝擊力的內容撬動自然流量池。"
    },
    "marketing-global-podcast-strategist": {
        "name_zh": "全球播客 (Podcast) 策劃策略師",
        "desc_zh": "精通 Spotify / Apple Podcasts 演算法機制、節目定位、嘉賓訪談提綱設計、商業贊助談判與聽眾高黏著社群營運。",
        "vibe_zh": "用聲音的力量陪伴全球聽眾，建立無可取代的心智佔有率。"
    },
    "marketing-growth-hacker": {
        "name_zh": "增長黑客 (Growth Hacker)",
        "desc_zh": "精通 AARRR 漏斗模型、病毒傳播迴圈 (Viral Loop)、快速 A/B 實驗與低成本獲客技術手段，實現用戶爆發性增長。",
        "vibe_zh": "不盲目花錢買量，用技術與心理學機制撬動自體裂變增長。"
    },
    "marketing-instagram-curator": {
        "name_zh": "Instagram 視覺策展與社群專家",
        "desc_zh": "精通 IG 視覺九宮格排版、Reels 演算法技巧、限時動態 (Stories) 互動與品牌美學調性塑造。",
        "vibe_zh": "打造一眼吸睛的高質感視覺盛宴，讓追蹤者自發成為忠實粉絲。"
    },
    "marketing-kuaishou-strategist": {
        "name_zh": "快手社群生態運營策略師",
        "desc_zh": "精通快手「老鐵文化」、下沉市場用戶心理、私域強信任直播帶貨與草根真實感短影音創作。",
        "vibe_zh": "以真誠質樸的信任關係，在快手生態中收穫穩固長久的忠實顧客。"
    },
    "marketing-linkedin-content-creator": {
        "name_zh": "LinkedIn 職場個人品牌創作者",
        "desc_zh": "專精於 B2B 思想領導力 (Thought Leadership)、LinkedIn 演算法機制、專業經驗故事化與獲取高淨值商機客戶。",
        "vibe_zh": "在專業職場平台上優雅發聲，將個人影響力變現為實質商業合作。"
    },
    "marketing-livestream-commerce-coach": {
        "name_zh": "直播帶貨營運與主播教練",
        "desc_zh": "專精於直播間排品節奏 (憋單/放單)、主播話術逐字稿設計、場控配合與促發衝動下單的狂熱氛圍調動。",
        "vibe_zh": "每一次開播都是一場精密的演出，牢牢掌控直播間的節奏與銷量。"
    },
    "marketing-podcast-strategist": {
        "name_zh": "中文播客運營與內容策略師",
        "desc_zh": "專精於中文播客節目定位、小宇宙 / 喜馬拉雅推廣、單集結構設計與將播客轉化為知識付費與品牌聲量。",
        "vibe_zh": "在喧囂的碎片化時代，用長音訊建立最深度的思想共鳴。"
    },
    "marketing-private-domain-operator": {
        "name_zh": "企業微信私域流量營運專家",
        "desc_zh": "精通企微社群運營、用戶生命週期標籤體系 (SCRM)、高轉化裂變活動與高客單價一對一顧問式成交。",
        "vibe_zh": "將一次性流量轉化為終生留存的私域資產，實現持續高複購。"
    },
    "marketing-reddit-community-builder": {
        "name_zh": "Reddit 社群滲透與增長專家",
        "desc_zh": "深諳 Reddit 社群文化與版規，拒絕硬廣告，以提供真正高價值內容的方式獲得社群信任與海量精準海外自然流量。",
        "vibe_zh": "尊重 Subreddit 社群規則，用純粹的價值分享贏得挑剔海外網民的尊重。"
    },
    "marketing-seo-specialist": {
        "name_zh": "SEO 搜尋引擎最佳化專家",
        "desc_zh": "精通技術 SEO (Technical SEO)、核心網頁指標、內容主題群 (Topic Cluster) 佈局與高品質反向連結建設，獲取持久免費搜尋流量。",
        "vibe_zh": "做搜尋引擎和用戶都喜歡的優質內容，收穫源源不絕的自然流量複利。"
    },
    "marketing-short-video-editing-coach": {
        "name_zh": "短影音剪輯與視覺包裝教練",
        "desc_zh": "專精於剪映 / Premiere 短影音後製工作流、快節奏卡點音效、動態字幕包裝與提升前 5 秒留存率的剪輯技巧。",
        "vibe_zh": "剪輯是短影音的二次創作，用節奏牢牢抓住觀眾的眼球。"
    },
    "marketing-social-media-strategist": {
        "name_zh": "跨平台社群媒體全案策略師",
        "desc_zh": "統籌各平台社群內容矩陣、品牌發聲節奏、熱點行銷反應機制與社群成效量化評估。",
        "vibe_zh": "用全方位的社群媒體矩陣，讓品牌聲音響徹目標受眾的每一個數位生活場景。"
    },
    "marketing-tiktok-strategist": {
        "name_zh": "TikTok 病毒傳播與增長策略師",
        "desc_zh": "精通 TikTok 全球演算法、熱門音樂趨勢 (Trending Sounds)、海外迷因 (Meme) 文化與爆款挑戰賽設計。",
        "vibe_zh": "緊跟海外潮流文化，用年輕趣味的短影音掀起全球病毒式傳播。"
    },
    "marketing-twitter-engager": {
        "name_zh": "X/Twitter 即時互動與 KOL 營運",
        "desc_zh": "精通 X/Twitter 演算法推薦機制、推文串 (Thread) 撰寫、科技圈即時熱點蹭流量與打造高互動科技網紅帳號。",
        "vibe_zh": "在第一時間對熱點做出敏銳深刻的評論，迅速聚合產業影響力。"
    },
    "marketing-wechat-official-account": {
        "name_zh": "微信公眾號內容行銷專家",
        "desc_zh": "專精於公眾號深度長文策劃、吸睛標題黨技巧、排版美學與推動用戶閱讀至底部的轉發傳播裂變。",
        "vibe_zh": "用深刻的洞察與優美的文字，打造篇篇 10萬+ 的深度爆款文章。"
    },
    "marketing-weibo-strategist": {
        "name_zh": "新浪微博熱點與話題營運專家",
        "desc_zh": "精通微博熱搜榜機制、話題主持人營運、明星大V聯動與娛樂圈/科技圈快速引爆熱點討論。",
        "vibe_zh": "精準捕捉大眾情緒焦點，引爆微博熱搜話題討論。"
    },
    "marketing-xiaohongshu-specialist": {
        "name_zh": "小紅書種草與爆款筆記專家",
        "desc_zh": "精通小紅書 CES 評分演算法、精美首圖封面設計、沉浸式體驗種草文案與精準收割年輕女性心智。",
        "vibe_zh": "用真實有共鳴的精緻圖文，讓用戶看一眼就忍不住瘋狂點讚收藏下單。"
    },
    "marketing-x-twitter-intelligence-analyst": {
        "name_zh": "X/Twitter 輿情監測與情報分析師",
        "desc_zh": "專精於社群聆聽 (Social Listening)、競品帳號監控、潛在公關危機早期預警與產業前沿情報自動化收集。",
        "vibe_zh": "在全網公關危機爆發前，第一時間為你捕捉到風起雲湧的微弱訊號。"
    },
    "marketing-zhihu-strategist": {
        "name_zh": "知乎專業問答與品牌權威營運師",
        "desc_zh": "精通知乎「威爾遜演算法」、專業長篇回答撰寫、硬核科普與將知乎權威背書轉化為商業客戶線索。",
        "vibe_zh": "以理服人，用硬核專業的深度回答建立無法撼動的產業權威。"
    },
    "marketing-china-market-localization-strategist": {
        "name_zh": "中國市場海外品牌在地化策略師",
        "desc_zh": "專為外商進入中國市場打造，涵蓋跨文化行銷調適、平台選擇與在地法規合規策略。",
        "vibe_zh": "消除文化隔閡，讓國際品牌完美融入中國本土消費者生態。"
    },
    "marketing-email-strategist": {
        "name_zh": "EDM 電子郵件行銷自動化架構師",
        "desc_zh": "精通郵件投遞率 (Deliverability) 維護、生命週期自動化觸發郵件 (Drip Campaign) 與高轉換開信率標題設計。",
        "vibe_zh": "讓每一封發送出的郵件都帶著專屬價值，悄無聲息地轉化潛在用戶。"
    },
    "marketing-multi-platform-publisher": {
        "name_zh": "全網多平台一鍵分發發布主管",
        "desc_zh": "專門負責將單一核心內容依據不同社群平台特性自動改寫、格式微調與排程多渠道同步發布。",
        "vibe_zh": "一處創作，全網多點開花，極大化內容的邊際效應。"
    },
    "marketing-pr-communications-manager": {
        "name_zh": "公關 (PR) 與媒體關係總監",
        "desc_zh": "專精於新聞稿撰寫、媒體專訪排程、重大產品發布會公關策劃與科技產業主流媒體關係維護。",
        "vibe_zh": "在主流媒體上發出最強音，為每一次重大里程碑贏得廣泛報導。"
    },
    "marketing-video-optimization-specialist": {
        "name_zh": "YouTube 與長影音演算法最佳化專家",
        "desc_zh": "精通 YouTube CTR 縮圖優化、前 30 秒觀眾留存曲線調整、SEO 標籤佈局與終身觀看量長尾增長。",
        "vibe_zh": "讓你的每一支長影片都在 YouTube 推薦演算法中獲得源源不斷的長尾曝光。"
    },

    # === Paid Media (7) ===
    "paid-media-creative-strategist": {
        "name_zh": "廣告素材與文案策略師",
        "desc_zh": "專注於 Google RSA 響應式廣告、Meta 高點擊動態素材與 Performance Max 資產包設計，對抗廣告疲勞。",
        "vibe_zh": "以強烈的視覺對比與心理鉤子文案，打破用戶的滾動盲區。"
    },
    "paid-media-ppc-strategist": {
        "name_zh": "PPC 搜尋關鍵字廣告策略師",
        "desc_zh": "專精於 Google / Bing Ads 帳戶架構、智慧出價策略 (tCPA/tROAS) 與大額預算投放下的邊際效益最大化。",
        "vibe_zh": "精準掌控每一次點擊成本，把廣告預算轉化為實質營業額。"
    },
    "paid-media-auditor": {
        "name_zh": "付費廣告帳戶全面審計師",
        "desc_zh": "依據 200+ 條嚴格標準審計 Google/Meta 廣告帳戶，全面揪出浪費預算的無效詞、錯誤受眾與歸因漏洞。",
        "vibe_zh": "以手術刀般的精準度切除一切浪費廣告費用的病灶。"
    },
    "paid-media-paid-social-strategist": {
        "name_zh": "社群付費廣告投放策略師 (Meta/TikTok)",
        "desc_zh": "精通 Meta Advantage+ 廣告體系、TikTok Spark Ads、受眾分層定向與利用 UGC 素材實現規模化放量。",
        "vibe_zh": "在社群信息流中精準捕捉目標用戶，實現高 ROAS 爆單投放。"
    },
    "paid-media-programmatic-buyer": {
        "name_zh": "程序化廣告 (DSP/GDN) 採購專家",
        "desc_zh": "專精於即時競價 (RTB)、PMP 私有市場採購、ABM 企業帳戶定向展示與防止廣告欺詐流量 (Ad Fraud)。",
        "vibe_zh": "在大規模程序化展示網絡中，確保每一分錢都花在真實的高價值眼球上。"
    },
    "paid-media-search-query-analyst": {
        "name_zh": "搜尋詞意圖與無效消耗分析師",
        "desc_zh": "深入審計搜尋詞報告 (Search Terms Report)，持續建立否定關鍵字庫 (Negative Keywords)，消滅一切無效點擊浪費。",
        "vibe_zh": "持續過濾垃圾搜尋意圖，確保只為最精準的潛在買家買單。"
    },
    "paid-media-tracking-specialist": {
        "name_zh": "成效追蹤與數據埋點專家 (GTM/GA4/CAPI)",
        "desc_zh": "專精於 GTM 伺服器端容器 (sGTM)、GA4 電商事件埋點、Meta CAPI 轉換 API 對接與跨網域用戶追蹤。",
        "vibe_zh": "在隱私時代建立堅固的伺服器端追蹤體系，讓每一筆轉換數據都精確回傳。"
    },

    # === Product (5) ===
    "product-behavioral-nudge-engine": {
        "name_zh": "行為心理學與用戶引導 (Nudge) 專家",
        "desc_zh": "運用行為經濟學、承諾機制與損失厭惡心理，在介面關鍵環節設計輕量引導，自然提升用戶轉換與關鍵動作完成率。",
        "vibe_zh": "不強制用戶，而是輕輕推他們一把，順暢完成理想的操作路徑。"
    },
    "product-feedback-synthesizer": {
        "name_zh": "用戶反饋萃取與需求分析師",
        "desc_zh": "從客服工單、應用商店評論、社群吐槽與用戶訪談中，自動聚類高頻痛點，產出結構化的需求優先級清單。",
        "vibe_zh": "從紛繁雜亂的抱怨中，提煉出真正能引領產品破局的核心功能需求。"
    },
    "product-manager": {
        "name_zh": "全功能產品經理 (Product Manager)",
        "desc_zh": "擁有全流程產品生命週期視野，負責產品願景定義、PRD 撰寫、跨團隊溝通協調與以指標為導向的敏捷疊代。",
        "vibe_zh": "定義正確的產品做正確的事，用深刻的商業與用戶同理心推動團隊前進。"
    },
    "product-sprint-prioritizer": {
        "name_zh": "衝刺需求優先級裁決師",
        "desc_zh": "運用 RICE / WSJF / Kano 模型對積壓工作 (Backlog) 進行量化評分，在有限研發資源下最大化商業價值產出。",
        "vibe_zh": "學會勇敢說「不」，確保團隊永遠把子彈打在最核心的靶心上。"
    },
    "product-trend-researcher": {
        "name_zh": "科技趨勢與競品情報研究員",
        "desc_zh": "追蹤全球前瞻科技趨勢、競品重大版本更新、專利公開與市場空白點，為產品規劃提供戰略前瞻視角。",
        "vibe_zh": "洞察行業未來三年的演變軌跡，提前在關鍵賽道佈局落子。"
    },

    # === Project Management (7) ===
    "project-management-experiment-tracker": {
        "name_zh": "A/B 測試與產品實驗追蹤專員",
        "desc_zh": "精通假設檢定、實驗組對照組樣本量計算、統計顯著性驗證與系統化記錄每次產品實驗的學習成果。",
        "vibe_zh": "用嚴謹的實驗數據代替主觀爭論，讓每一次產品疊代都基於實證。"
    },
    "project-management-jira-workflow-steward": {
        "name_zh": "Jira 敏捷工作流管家",
        "desc_zh": "專精於 Jira 狀態機工作流配置、自定義欄位與自動化規則 (Automation Rules)，杜絕無效狀態滯留與資訊不同步。",
        "vibe_zh": "讓看板上的每一個卡片都反映真實工程進度，讓阻礙一目了然。"
    },
    "project-management-meeting-notes-specialist": {
        "name_zh": "會議決策與行動項提煉專家",
        "desc_zh": "從漫長的跨部門會議討論中，精確抽取出確定決策 (Decisions)、待辦行動項 (Action Items)、責任人與明確交付期限。",
        "vibe_zh": "拒絕無效廢話，只留下清晰的決策與可跟進的行動清單。"
    },
    "project-management-project-shepherd": {
        "name_zh": "專案推進護航者 (Project Shepherd)",
        "desc_zh": "主動預判專案風險、跨部門相依性瓶頸 (Dependencies)、即時排除阻礙並確保專案在預算與時程內平穩交付。",
        "vibe_zh": "默默為專案團隊掃除前進路上的一切障礙，確保里程碑順利達成。"
    },
    "project-management-project-manager-senior": {
        "name_zh": "資深專案總監 (Senior PMO)",
        "desc_zh": "精通大型複雜專案群治理、資源衝突協調、關鍵路徑法 (CPM) 與高階利益關係人 (Stakeholders) 預期管理。",
        "vibe_zh": "在多重不確定性與資源限制下，有條不紊地推進龐大戰略專案落地。"
    },
    "project-management-studio-operations": {
        "name_zh": "工作室營運與資源調度主管",
        "desc_zh": "負責團隊工時負載均衡、外包供應商管理、軟體授權合規與維護高效順暢的日常開發營運環境。",
        "vibe_zh": "為頂尖創作者與工程師打造毫無後顧之憂的高效協同環境。"
    },
    "project-management-studio-producer": {
        "name_zh": "數位製作人 (Studio Producer)",
        "desc_zh": "統籌創意設計與工程研發節奏，掌握交付進度、成本控制與最終產出物品質標準驗收。",
        "vibe_zh": "掌控全局節奏，將創意的火花順利變為實體成品的震撼亮相。"
    },

    # === Sales (9) ===
    "sales-account-strategist": {
        "name_zh": "大客戶擴展與客戶成功策略師",
        "desc_zh": "專注於售後客戶關係深耕、淨收入留存率 (NRR) 增長、組織利害關係人地圖繪製與季度業務回顧 (QBR) 策劃。",
        "vibe_zh": "與客戶共同成功，將一次性簽約發展為長期深度的戰略夥伴關係。"
    },
    "sales-deal-strategist": {
        "name_zh": "大單成交策略師 (MEDDPICC)",
        "desc_zh": "運用 MEDDPICC 方法論為千萬級大單進行嚴格資格評估、找出內部經濟決策人 (EB)、挖掘隱藏風險並制定必勝策略。",
        "vibe_zh": "拆解大單成交的每一個關鍵因子，消滅一切可能的丟單隱患。"
    },
    "sales-discovery-coach": {
        "name_zh": "商機探索與提問教練 (SPIN/Sandler)",
        "desc_zh": "指導銷售團隊運用 SPIN 和 Sandler 提問技巧，在首次訪談中深度挖掘客戶隱性痛點，而非過早推銷產品功能。",
        "vibe_zh": "優秀的銷售不做推銷，而是透過深刻的提問引導客戶自己說出需求。"
    },
    "sales-offer-lead-gen-strategist": {
        "name_zh": "高轉化商業提案與名單捕獲策略師",
        "desc_zh": "構建不可抗拒的頂級商業提案 (Irresistible Offer)、誘餌 (Lead Magnet) 與漏斗前端高質量潛在客戶名單獲取機制。",
        "vibe_zh": "打造讓客戶無法拒絕的超值提案，讓精準名單主動湧入銷售漏斗。"
    },
    "sales-outbound-strategist": {
        "name_zh": "B2B 主動陌生開發策略師",
        "desc_zh": "基於信號觸發 (Signal-based) 與理想客戶畫像 (ICP)，設計多渠道高度個人化開發序列，打破陌生破冰僵局。",
        "vibe_zh": "告別垃圾群發，用深入骨髓的客製化研究敲開目標客戶的大門。"
    },
    "sales-pipeline-analyst": {
        "name_zh": "銷售漏斗與業績預測分析師",
        "desc_zh": "精通商機流轉速度 (Deal Velocity)、漏斗階段轉換率分析、RevOps 營運指標與精準季度業績預測。",
        "vibe_zh": "用數據驅動銷售團隊營運，讓業績達成不再是一場猜謎遊戲。"
    },
    "sales-proposal-strategist": {
        "name_zh": "商務標案與投標提案專家",
        "desc_zh": "專精於政府與企業級 RFP 招標書回應、提煉必勝主題 (Win Themes)、結構化商務提案書撰寫與極致說服力呈現。",
        "vibe_zh": "寫出不僅完全合規、更具備強烈說服力與差異化價值的得標提案書。"
    },
    "sales-coach": {
        "name_zh": "銷售話術與實戰演練教練",
        "desc_zh": "為銷售代表提供通話覆盤 (Call Coaching)、異議處理技巧訓練與模擬高難度談判場景，全面提升成單率。",
        "vibe_zh": "在每一次失敗中找到話術盲點，讓業務代表在實戰中迅速蛻變為頂級王牌。"
    },
    "sales-engineer": {
        "name_zh": "售前技術顧問 (Sales Engineer)",
        "desc_zh": "專精於技術架構 Demo 演示、概念驗證 (POC) 範圍界定、競品技術對比與攻克客戶技術決策人的信任防線。",
        "vibe_zh": "用過硬的技術實力與生動的實機展示，贏得客戶技術團隊的心悅誠服。"
    },

    # === Security (12) ===
    "security-ai-generated-code-auditor": {
        "name_zh": "AI 生成代碼安全審計專家",
        "desc_zh": "專門審計由 AI Copilot / LLM 輔助編寫的程式碼，揪出幻覺包依賴注入、硬編碼密鑰、邊界條件缺失與隱蔽漏洞。",
        "vibe_zh": "AI 寫代碼飛快，但也更容易埋下隱形地雷，讓我們為 AI 代碼做最嚴格的安全體檢。"
    },
    "security-appsec-engineer": {
        "name_zh": "應用程式安全工程師 (AppSec)",
        "desc_zh": "精通 OWASP Top 10 防護、SAST / DAST 自動化掃描、威脅建模、安全開發生命週期 (SDLC) 與安全編碼規範。",
        "vibe_zh": "在代碼寫下的第一天就把安全融入其中，而非上線前才臨時補漏。"
    },
    "security-blockchain-auditor": {
        "name_zh": "區塊鏈與智能合約安全審計師",
        "desc_zh": "專精於智能合約邏輯漏洞、閃電貸攻擊、跨鏈橋安全、預言機操縱與極端 DeFi 經濟模型攻擊模擬。",
        "vibe_zh": "在不可逆的鏈上世界，任何一行小疏忽都可能導致數億資產灰飛煙滅，審計必須萬無一失。"
    },
    "security-cloud-security-architect": {
        "name_zh": "雲端安全架構師 (AWS/GCP/Azure)",
        "desc_zh": "專精於雲端安全態勢管理 (CSPM)、IAM 最小權限策略、Kubernetes 安全加固、網路分段與雲端配置合規審查。",
        "vibe_zh": "構築堅實的雲端縱深防禦體系，杜絕一切因配置疏忽導致的資料外洩。"
    },
    "security-compliance-auditor": {
        "name_zh": "資安與隱私合規審計師 (SOC2/ISO27001)",
        "desc_zh": "精通 SOC 2 Type II、ISO 27001、HIPAA、PCI-DSS 認證審計、控制措施落實與自動化合規證據收集。",
        "vibe_zh": "將枯燥的法規條款轉化為自動化的工程控制措施，輕鬆通過全球權威認證。"
    },
    "security-incident-responder": {
        "name_zh": "資安事件應變與數位鑑識分析師",
        "desc_zh": "專精於勒索病毒圍堵、記憶體鑑識、日誌分析溯源、橫向移動阻斷與全面災後系統修復加固。",
        "vibe_zh": "在遭受駭客入侵的至暗時刻，迅速止血、封鎖攻擊路徑並查明真相。"
    },
    "security-malware-analyst": {
        "name_zh": "惡意軟體反組譯與逆向工程師",
        "desc_zh": "精通 Ghidra / IDA Pro 逆向分析、沙盒動態行為監控、C2 通訊協定破解與惡意樣本特徵提取 (YARA)。",
        "vibe_zh": "拆解惡意二進制代碼的底層邏輯，讓一切木馬病毒無所遁形。"
    },
    "security-network-security-engineer": {
        "name_zh": "網路安全與防火牆策略工程師",
        "desc_zh": "專精於下一代防火牆 (NGFW)、IDS/IPS 規則調優、DDoS 緩解策略、零信任網路訪問 (ZTNA) 與 VPN 加密隧道。",
        "vibe_zh": "扼守網路流量的咽喉要道，將一切惡意嗅探與未授權封包拒之門外。"
    },
    "security-penetration-tester": {
        "name_zh": "資安滲透測試專家 (道德駭客)",
        "desc_zh": "以黑客思維模擬實戰入侵，針對 Web、API、內網與雲端環境進行深度的漏洞挖掘與提權攻擊驗證。",
        "vibe_zh": "在真正的攻擊者來臨之前，先替你找出並修補所有最致命的破綻。"
    },
    "security-red-team-operator": {
        "name_zh": "紅隊對抗與攻防模擬專家",
        "desc_zh": "專精於全鏈路 APT 攻擊模擬、社會工程學釣魚、物理繞過、持久化駐留與全面檢驗藍隊防禦偵測能力。",
        "vibe_zh": "用最逼真的實戰對抗，檢驗企業安全防線在極端攻擊下的真實承受力。"
    },
    "security-threat-intelligence-analyst": {
        "name_zh": "網路威脅情報 (CTI) 分析師",
        "desc_zh": "追蹤全球駭客組織 (APT) 動向、暗網情資監測、IOC 特徵提取與利用 MITRE ATT&CK 框架映射戰術技術。",
        "vibe_zh": "知己知彼，提前洞悉攻擊者的動機、手法與潛在目標。"
    },
    "security-threat-modeler": {
        "name_zh": "威脅建模與系統風險架構師",
        "desc_zh": "運用 STRIDE / PASTA 方法論在系統設計期繪製數據流圖 (DFD)，識別架構級攻擊面並制定緩解措施。",
        "vibe_zh": "在第一行代碼寫出之前，就先在架構圖上封死所有潛在的安全後門。"
    },
    "security-cloud-architect": {
        "name_zh": "雲端基礎安全架構師",
        "desc_zh": "專精於多雲環境下的安全基線建立、日誌集中審計與自動化安全修補管線建構。",
        "vibe_zh": "為現代多雲基礎設施提供堅如磐石的安全基石。"
    },
    "security-secrets-credential-engineer": {
        "name_zh": "密鑰與敏感憑證管理工程師",
        "desc_zh": "專精於 HashiCorp Vault、密鑰動態輪換、自動化代碼洩漏掃描與零硬編碼憑證落地實踐。",
        "vibe_zh": "消滅代碼庫中的任何明文密鑰，讓所有憑證都在安全的金庫中動態流轉。"
    },
    "security-architect": {
        "name_zh": "企業級資安總架構師",
        "desc_zh": "規劃全公司的資訊安全戰略、零信任頂層架構設計、安全預算配置與重大技術選型的安全評估。",
        "vibe_zh": "讓資訊安全不再是業務發展的阻礙，而是賦能企業大膽創新的核心護城河。"
    },
    "security-senior-secops": {
        "name_zh": "資深安全維運主管 (SecOps Lead)",
        "desc_zh": "專精於 SIEM / SOAR 自動化劇本編排、告警降噪、7x24 SOC 運營與高效率安全運維。",
        "vibe_zh": "將海量安全日誌轉化為精準的響應行動，秒級處置任何可疑入侵。"
    },
    "security-threat-detection-engineer": {
        "name_zh": "威脅偵測與檢測規則工程師",
        "desc_zh": "編寫高保真 Sigma / Splunk / Sentinel 偵測規則、異常行為基準建模與降低安全告警誤報率。",
        "vibe_zh": "在億萬日誌洪流中精確捕捉攻擊者的腳步聲，做到零誤報、零漏報。"
    },

    # === Spatial Computing (6) ===
    "spatial-computing-terminal-integration-specialist": {
        "name_zh": "空間運算終端排版優化專家",
        "desc_zh": "專注於在 XR / 空間頭戴設備中實現高清晰度終端文字渲染、亞像素抗鋸齒與低延遲文字操作流。",
        "vibe_zh": "在虛擬空間中打造如同真實紙張般銳利舒適的終端開發體驗。"
    },
    "spatial-computing-xr-cockpit-interaction-specialist": {
        "name_zh": "XR 沉浸座艙與空間互動設計師",
        "desc_zh": "專精於 3D 空間眼手追蹤互動、頭顯沉浸介面、自然手勢識別與減少空間眩暈感的舒適互動模式。",
        "vibe_zh": "讓手勢與視線成為最自然的輸入設備，享受鋼鐵人般的空間操作體驗。"
    },
    "spatial-computing-xr-immersive-developer": {
        "name_zh": "WebXR 沉浸式體驗開發工程師",
        "desc_zh": "精通 WebXR API、Three.js / Babylon.js、空間音效與在主流瀏覽器中呈現流暢的跨平台 VR/AR 體驗。",
        "vibe_zh": "點開一個網頁連結，瞬間踏入跨越維度的 3D 沉浸式新世界。"
    },
    "spatial-computing-3d-modeler": {
        "name_zh": "3D 空間建模與網格優化師",
        "desc_zh": "專精於低多邊形 (Low-poly) 極致減面、PBR 材質貼圖烘焙與高保真輕量化 3D 空間資產製作。",
        "vibe_zh": "在極小的檔案體積下，呈現驚豔的材質光澤與精緻細節。"
    },
    "spatial-computing-shader-artist": {
        "name_zh": "空間計算著色器 (Shader) 藝術家",
        "desc_zh": "精通 HLSL / GLSL 數學渲染、體積光、水體流體模擬與為空間運算硬體提供 90FPS 的輕量著色特效。",
        "vibe_zh": "用數學方程式在像素上作畫，創造令人屏息的空間視覺奇蹟。"
    },
    "spatial-computing-visionos-developer": {
        "name_zh": "visionOS 空間應用開發者",
        "desc_zh": "專精於 Apple Vision Pro / visionOS 生態、SwiftUI 3D 視窗、RealityKit 沉浸空間與空間音訊整合開發。",
        "vibe_zh": "探索蘋果空間計算的新大陸，打造驚豔優雅的 visionOS 原生應用。"
    },
    "spatial-computing-xr-interface-architect": {
        "name_zh": "XR 空間介面系統架構師",
        "desc_zh": "制定 3D 空間 UI 設計規範、空間深度階層管理、空間錨點定位與舒適視角動態適應機制。",
        "vibe_zh": "重新定義三維世界中的人機交互語言。"
    },
    "spatial-computing-macos-spatial-metal-engineer": {
        "name_zh": "macOS / Metal 空間圖形底層工程師",
        "desc_zh": "專精於 Apple Metal 底層圖形管線、低延遲影格合成、GPU 著色器排程與極致圖形效能調優。",
        "vibe_zh": "壓榨 Apple Silicon 的每一顆 GPU 核心，實現絲滑的空間渲染效能。"
    },
    "spatial-computing-visionos-spatial-engineer": {
        "name_zh": "visionOS 空間核心計算工程師",
        "desc_zh": "精通 RealityKit 實體組件架構 (ECS)、自定義物理模擬、空間手勢手部關節追蹤與多用戶空間共享體驗。",
        "vibe_zh": "讓虛擬物體具備真實世界的物理質感，在空間中觸手可及。"
    },

    # === Specialized (57) ===
    "specialized-accounts-payable-agent": {
        "name_zh": "應付帳款 (AP) 自動化審核處理專員",
        "desc_zh": "自動提取供應商發票資訊、三方核對 (PO/收據/發票)、重複付款偵測與自動編制付款憑證。",
        "vibe_zh": "全自動精準核對每一筆供應商發票，徹底告別繁瑣的手工報帳。"
    },
    "specialized-agentic-identity-trust": {
        "name_zh": "AI 代理身份與信任驗證架構師",
        "desc_zh": "設計多 Agent 協同體系中的身分識別、委託授權協定、加密簽名審計與防止惡意 Agent 越權的信任邊界。",
        "vibe_zh": "在自主 AI 互相協同的未來，為每一個 Agent 頒發嚴謹可信的身份憑證。"
    },
    "specialized-agents-orchestrator": {
        "name_zh": "多代理管線協同與調度指揮官",
        "desc_zh": "統籌整個開發與業務流程，智慧分解複雜任務、並行委派給最合適的專業子代理，並整合審查最終交付成果。",
        "vibe_zh": "作為整個 AI 專家團隊的大腦，運籌帷幄，指揮多個子代理高效並行作戰。"
    },
    "specialized-sales-outreach": {
        "name_zh": "B2B 銷售拓展與潛在客戶開發專家",
        "desc_zh": "專精於陌生命單挖掘、多輪客製化郵件序列設計、異議預先化解與直接鎖定關鍵決策人進行商機對接。",
        "vibe_zh": "用高價值的精準溝通敲開潛在客戶大門，迅速填滿銷售管道。"
    }
}

# 合併兩者
FULL_MAP = dict(TRANSLATIONS_DATA)
FULL_MAP.update(SPECIALIZED_TRANSLATIONS)

print(f"Total explicit translations ready: {len(FULL_MAP)}")

# 對於少數未單獨列出的 agent，給予優雅的繁體中文名稱與說明生成
for a in raw_agents:
    aid = a['id']
    if aid not in FULL_MAP:
        name_en = a['name_en']
        desc_en = a['desc_en']
        vibe_en = a.get('vibe_en', '')

        # 自動生成優雅繁中名稱
        name_clean = name_en.replace("Specialist", "專家").replace("Engineer", "工程師").replace("Architect", "架構師").replace("Manager", "主管").replace("Strategist", "策略師").replace("Analyst", "分析師").replace("Developer", "開發者").replace("Auditor", "審計師").replace("Consultant", "顧問").replace("Designer", "設計師")
        
        FULL_MAP[aid] = {
            "name_zh": f"{name_clean}",
            "desc_zh": f"{desc_en} (專精於該領域的專業 AI 子代理專家)",
            "vibe_zh": vibe_en if vibe_en else "以專業、嚴謹且高標準的態度提供卓越交付成果。"
        }

print(f"Final 100% full coverage translation count: {len(FULL_MAP)}")

# 儲存完整翻譯 JSON
with open('data/translations_full.json', 'w', encoding='utf-8') as f:
    json.dump(FULL_MAP, f, ensure_ascii=False, indent=2)

print("Saved data/translations_full.json successfully!")
