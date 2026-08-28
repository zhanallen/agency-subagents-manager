import os
import re
import json
import subprocess
import urllib.request
from pathlib import Path
from typing import List, Dict, Any, Optional

# 部門繁體中文對照表與設定
DIVISIONS_CONFIG = {
    "academic": {
        "id": "academic",
        "name_zh": "學術研究",
        "name_en": "Academic",
        "icon": "GraduationCap",
        "color": "#8B5CF6",
        "desc_zh": "人類學、歷史研究、統計分析、地理空間與敘事心理學專家"
    },
    "design": {
        "id": "design",
        "name_zh": "視覺與體驗設計",
        "name_en": "Design",
        "icon": "PenTool",
        "color": "#EC4899",
        "desc_zh": "UI/UX 設計、品牌視覺規範、微互動、無障礙體驗與圖像提示詞"
    },
    "engineering": {
        "id": "engineering",
        "name_zh": "軟體與系統工程",
        "name_en": "Engineering",
        "icon": "Code",
        "color": "#3B82F6",
        "desc_zh": "前端/後端/全端開發、系統架構、DevOps、Web3、嵌入式與資料庫調優"
    },
    "finance": {
        "id": "finance",
        "name_zh": "金融與財務科技",
        "name_en": "Finance",
        "icon": "DollarSign",
        "color": "#22C55E",
        "desc_zh": "財務分析、會計審計、風險控制、合規模型與金融科技策略"
    },
    "game-development": {
        "id": "game-development",
        "name_zh": "遊戲開發與引擎",
        "name_en": "Game Development",
        "icon": "Gamepad2",
        "color": "#A855F7",
        "desc_zh": "遊戲機制設計、Unity/Unreal 引擎開發、數值平衡與著色器優化"
    },
    "gis": {
        "id": "gis",
        "name_zh": "地理資訊與空間分析",
        "name_en": "GIS",
        "icon": "Map",
        "color": "#14B8A6",
        "desc_zh": "GIS 空間分析、地圖數據處理、座標轉換與地理空間視覺化"
    },
    "healthcare": {
        "id": "healthcare",
        "name_zh": "醫療與健康科技",
        "name_en": "Healthcare",
        "icon": "Stethoscope",
        "color": "#0D9488",
        "desc_zh": "醫療資訊交換、健康科技合規、臨床工作流與生醫數據分析"
    },
    "marketing": {
        "id": "marketing",
        "name_zh": "行銷推廣與社群",
        "name_en": "Marketing",
        "icon": "Megaphone",
        "color": "#F97316",
        "desc_zh": "增長黑客、內容行銷、SEO、社群媒體經營、播客與跨國電商"
    },
    "paid-media": {
        "id": "paid-media",
        "name_zh": "付費媒體與廣告投放",
        "name_en": "Paid Media",
        "icon": "Target",
        "color": "#EAB308",
        "desc_zh": "Google/Meta 廣告策略、成效追蹤、ROAS 優化與關鍵字審計"
    },
    "product": {
        "id": "product",
        "name_zh": "產品管理與規劃",
        "name_en": "Product",
        "icon": "Box",
        "color": "#D946EF",
        "desc_zh": "產品藍圖、需求規格 (PRD)、使用者研究、競品分析與敏捷疊代"
    },
    "project-management": {
        "id": "project-management",
        "name_zh": "專案管理與敏捷",
        "name_en": "Project Management",
        "icon": "ClipboardList",
        "color": "#0EA5E9",
        "desc_zh": "Scrum/Kanban 敏捷推進、時程把控、風險管理與跨團隊協作"
    },
    "sales": {
        "id": "sales",
        "name_zh": "銷售與商務拓展",
        "name_en": "Sales",
        "icon": "TrendingUp",
        "color": "#10B981",
        "desc_zh": "B2B 銷售開發、商機挖掘 (MEDDPICC)、技術提案與客戶談判"
    },
    "security": {
        "id": "security",
        "name_zh": "資訊安全與防護",
        "name_en": "Security",
        "icon": "ShieldCheck",
        "color": "#EF4444",
        "desc_zh": "滲透測試、程式碼安全審計、雲端合規、漏洞修復與事件應變"
    },
    "spatial-computing": {
        "id": "spatial-computing",
        "name_zh": "空間運算 (XR/VR/AR)",
        "name_en": "Spatial Computing",
        "icon": "Boxes",
        "color": "#06B6D4",
        "desc_zh": "Vision Pro / Meta Quest 空間計算、3D 互動、WebXR 與著色器開發"
    },
    "specialized": {
        "id": "specialized",
        "name_zh": "特殊專家與領域顧問",
        "name_en": "Specialized",
        "icon": "Sparkles",
        "color": "#6366F1",
        "desc_zh": "領域專家諮詢、專利分析、高階戰略規劃與複雜領域專家"
    },
    "support": {
        "id": "support",
        "name_zh": "客戶支援與服務",
        "name_en": "Support",
        "icon": "LifeBuoy",
        "color": "#84CC16",
        "desc_zh": "技術客服支援、客戶成功 (CS)、知識庫建設與 SLA 品質監控"
    },
    "testing": {
        "id": "testing",
        "name_zh": "測試與品質保證 (QA)",
        "name_en": "Testing",
        "icon": "FlaskConical",
        "color": "#F59E0B",
        "desc_zh": "自動化測試、端到端 (E2E) 測試、效能壓力測試與品質防線"
    }
}

class AgentManager:
    """負責管理、解析、搜尋與快取 Agency Agents 的專家資料（支援 100% 繁體中文 UI 呈現，保留原生提示詞）"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.repo_dir = self.workspace_root / "data" / "agency-agents-repo"
        self.cache_file = self.workspace_root / "data" / "agents_database.json"
        self.translations_file = self.workspace_root / "data" / "translations_full.json"
        self.translations_map: Dict[str, Dict[str, str]] = {}
        self.agents: List[Dict[str, Any]] = []
        self.agents_map: Dict[str, Dict[str, Any]] = {}
        
        self.load_translations()
        self.load_agents()

    def load_translations(self):
        """載入繁體中文翻譯字典庫"""
        if self.translations_file.exists():
            try:
                with open(self.translations_file, "r", encoding="utf-8") as f:
                    self.translations_map = json.load(f)
            except Exception as e:
                print(f"Failed to load translations: {e}")

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, str], str]:
        """解析 Markdown 的 YAML Frontmatter"""
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not fm_match:
            return {}, content
        
        fm_text, body = fm_match.groups()
        metadata = {}
        for line in fm_text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip().strip('"\'')
        return metadata, body.strip()

    def build_database_from_repo(self) -> List[Dict[str, Any]]:
        """掃描 repo_dir 並生成具備完整繁中化介面與原生提示詞的 Agent 資料庫"""
        if not self.repo_dir.exists():
            return []

        agents = []
        for div_id, div_info in DIVISIONS_CONFIG.items():
            div_dir = self.repo_dir / div_id
            if not div_dir.is_dir():
                continue

            for file in div_dir.glob("*.md"):
                if file.name.lower() in ["readme.md", "nexus.md"]:
                    continue

                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        raw_content = f.read()

                    meta, body = self._parse_frontmatter(raw_content)
                    name_en = meta.get("name", file.stem.replace(f"{div_id}-", "").replace("-", " ").title())
                    desc_en = meta.get("description", "")
                    emoji = meta.get("emoji", "🤖")
                    color = meta.get("color", div_info["color"])
                    vibe_en = meta.get("vibe", "")
                    
                    slug = f"{div_id}-{file.stem.replace(f'{div_id}-', '')}"

                    # 查詢繁體中文翻譯庫
                    trans = self.translations_map.get(slug, {})
                    name_zh = trans.get("name_zh", name_en)
                    desc_zh = trans.get("desc_zh", desc_en)
                    vibe_zh = trans.get("vibe_zh", vibe_en)

                    # 標籤
                    tags = [div_info["name_zh"], div_info["name_en"]]
                    if "frontend" in name_en.lower() or "react" in desc_en.lower():
                        tags.append("Frontend")
                    if "backend" in name_en.lower() or "api" in desc_en.lower():
                        tags.append("Backend")
                    if "test" in name_en.lower():
                        tags.append("Testing")
                    if "security" in name_en.lower():
                        tags.append("Security")

                    agent_item = {
                        "id": slug,
                        "slug": slug,
                        "division_id": div_id,
                        "division_name_zh": div_info["name_zh"],
                        "division_name_en": div_info["name_en"],
                        "division_icon": div_info["icon"],
                        "division_color": div_info["color"],
                        # 介面顯示用 (繁體中文)
                        "name_zh": name_zh,
                        "description_zh": desc_zh,
                        "description": desc_zh,  # 預設給 UI 讀取
                        "vibe_zh": vibe_zh,
                        "vibe": vibe_zh,        # 預設給 UI 讀取
                        # 原汁原味英文 (供安裝時使用)
                        "name_en": name_en,
                        "description_en": desc_en,
                        "vibe_en": vibe_en,
                        "file_path": str(file.relative_to(self.workspace_root)),
                        "relative_file": f"{div_id}/{file.name}",
                        "tags": list(set(tags)),
                        "emoji": emoji,
                        "color": color,
                        # 原廠 Markdown 與 Body (100% 原汁原味)
                        "raw_markdown": raw_content,
                        "body_markdown": body
                    }
                    agents.append(agent_item)
                except Exception as e:
                    print(f"Error parsing {file}: {e}")

        # 排序：依部門與名稱
        agents.sort(key=lambda x: (x["division_id"], x["name_en"]))
        
        # 寫入快取
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)

        return agents

    def load_agents(self) -> List[Dict[str, Any]]:
        """載入 Agent 資料"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.agents = json.load(f)
                    self.agents_map = {a["id"]: a for a in self.agents}
                    return self.agents
            except Exception as e:
                print(f"Failed to read cache: {e}")

        self.agents = self.build_database_from_repo()
        self.agents_map = {a["id"]: a for a in self.agents}
        return self.agents

    def get_divisions(self) -> List[Dict[str, Any]]:
        """獲取所有部門資訊與對應的專家數量"""
        counts = {}
        for a in self.agents:
            div = a["division_id"]
            counts[div] = counts.get(div, 0) + 1

        result = []
        for div_id, info in DIVISIONS_CONFIG.items():
            result.append({
                "id": div_id,
                "name_zh": info["name_zh"],
                "name_en": info["name_en"],
                "icon": info["icon"],
                "color": info["color"],
                "desc_zh": info["desc_zh"],
                "count": counts.get(div_id, 0)
            })
        return result

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """根據 ID 獲取單個 Agent 詳情"""
        return self.agents_map.get(agent_id)

    def search_agents(
        self,
        query: str = "",
        division: str = "all",
        installed_ids: Optional[List[str]] = None,
        filter_status: str = "all"
    ) -> List[Dict[str, Any]]:
        """搜尋與多維度篩選 Agent（支援中英文雙向匹配）"""
        query = query.strip().lower()
        results = []

        for agent in self.agents:
            if division != "all" and agent["division_id"] != division:
                continue

            is_installed = (installed_ids is not None) and (agent["id"] in installed_ids)
            if filter_status == "installed" and not is_installed:
                continue
            if filter_status == "uninstalled" and is_installed:
                continue

            if query:
                match = (
                    query in agent.get("name_zh", "").lower()
                    or query in agent.get("name_en", "").lower()
                    or query in agent.get("description_zh", "").lower()
                    or query in agent.get("description_en", "").lower()
                    or query in agent.get("vibe_zh", "").lower()
                    or query in agent.get("vibe_en", "").lower()
                    or query in agent.get("division_name_zh", "").lower()
                    or query in agent.get("division_name_en", "").lower()
                    or any(query in tag.lower() for tag in agent.get("tags", []))
                )
                if not match:
                    continue

            results.append(agent)

        return results

    def sync_translations_from_github(
        self,
        repo_owner_repo: str = "zhanallen/agency-subagents-manager",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """從使用者的 GitHub 倉庫同步最新的繁體中文在地化字典 (translations_full.json)"""
        url = f"https://raw.githubusercontent.com/{repo_owner_repo}/{branch}/data/translations_full.json"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AgencySubagentsManager-Sync/2.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    raw_data = response.read().decode("utf-8")
                    parsed = json.loads(raw_data)
                    if isinstance(parsed, dict) and len(parsed) > 0:
                        self.translations_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(self.translations_file, "w", encoding="utf-8") as f:
                            f.write(raw_data)
                        self.translations_map = parsed
                        return {
                            "success": True,
                            "count": len(parsed),
                            "message": f"成功自 {repo_owner_repo} 同步 {len(parsed)} 筆繁中翻譯字典"
                        }
            return {"success": False, "message": "遠端未返回有效翻譯資料"}
        except Exception as e:
            return {"success": False, "message": f"同步翻譯字典失敗 (已使用本機快取): {str(e)}"}

    def sync_from_github(
        self,
        repo_url: str = "https://github.com/msitarzewski/agency-agents.git"
    ) -> Dict[str, Any]:
        """從 GitHub 官方倉庫 (msitarzewski/agency-agents) 同步最新的專家定義"""
        try:
            if not self.repo_dir.exists():
                self.repo_dir.mkdir(parents=True, exist_ok=True)

            # 若無 .git，先初始化並綁定 remote
            if not (self.repo_dir / ".git").exists():
                subprocess.run(["git", "init"], cwd=str(self.repo_dir), capture_output=True, text=True, timeout=10)
                subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=str(self.repo_dir), capture_output=True, text=True, timeout=10)

            # 嘗試拉取 main 或 master 分支
            res = subprocess.run(
                ["git", "pull", "origin", "main", "--allow-unrelated-histories"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            if res.returncode != 0:
                res = subprocess.run(
                    ["git", "pull", "origin", "master", "--allow-unrelated-histories"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            # 重新加載翻譯並重構資料庫
            self.load_translations()
            self.agents = self.build_database_from_repo()
            self.agents_map = {a["id"]: a for a in self.agents}
            return {
                "success": True,
                "message": f"成功自原作者官方倉庫同步！共載入 {len(self.agents)} 位 AI 專家",
                "count": len(self.agents)
            }
        except Exception as e:
            # 即使 git pull 失敗，也重新讀取本機資料庫確保運行正常
            self.load_translations()
            self.agents = self.build_database_from_repo()
            self.agents_map = {a["id"]: a for a in self.agents}
            return {
                "success": True,
                "count": len(self.agents),
                "message": f"同步完成 (使用現有專家庫，共 {len(self.agents)} 位): {str(e)}"
            }
