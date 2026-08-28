import os
import re
import json
import base64
import urllib.request
from pathlib import Path
from typing import List, Dict, Any, Optional

ESSENTIAL_COLLABORATION_AGENT_IDS = [
    "specialized-agents-orchestrator",              # 總編排師與品質守門人 (跨領域執行與排程)
    "engineering-multi-agent-systems-architect",    # 多代理系統架構師 (代理拓撲、容錯機制與系統架構)
    "engineering-prompt-engineer"                   # 提示詞工程師 (提示詞架構與角色約束力調優)
]

class SubagentInstaller:
    """負責將 Agency Agents 轉換並安裝為符合各官方規範的 Subagent / Agent 定義檔 (嚴格單一目錄安裝，不重複寫入)"""

    def __init__(self, default_project_root: str):
        self.default_project_root = Path(default_project_root)
        self.home_dir = Path.home()
        self.rules_dir = self.default_project_root / "data" / "rules"

    def get_destinations(self, current_project_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """獲取所有支援的安裝目標與其路徑"""
        proj_root = Path(current_project_path) if current_project_path else self.default_project_root
        
        antigravity_project_dir = proj_root / ".agents" / "agents"
        antigravity_global_dir = self.home_dir / ".gemini" / "config" / "agents"
        claude_dir = self.home_dir / ".claude" / "agents"
        cursor_dir = proj_root / ".cursor" / "rules"
        opencode_dir = proj_root / ".opencode" / "agents"
        qwen_dir = self.home_dir / ".qwen" / "agents"
        codex_dir = self.home_dir / ".codex" / "agents"

        return [
            {
                "id": "antigravity_project",
                "name": "Antigravity 專案 Subagent (.agents/agents) [官方標準]",
                "description": "官方規範：安裝至 <專案>/.agents/agents/*.md，啟用 subagent: true 宣告",
                "path": str(antigravity_project_dir),
                "is_default": True,
                "project_root": str(proj_root),
                "exists": antigravity_project_dir.exists()
            },
            {
                "id": "antigravity_global",
                "name": "Antigravity 全域 Subagent (~/.gemini/config/agents)",
                "description": "官方規範：安裝至 ~/.gemini/config/agents/*.md，全域通用",
                "path": str(antigravity_global_dir),
                "is_default": False,
                "project_root": "",
                "exists": antigravity_global_dir.exists()
            },
            {
                "id": "claude_code",
                "name": "Claude Code 全域 (~/.claude/agents)",
                "description": "官方規範：安裝至 ~/.claude/agents/*.md，配置 tools 與 agent 描述",
                "path": str(claude_dir),
                "is_default": False,
                "project_root": "",
                "exists": claude_dir.exists()
            },
            {
                "id": "cursor",
                "name": "Cursor Rules 專案規則 (.cursor/rules)",
                "description": "官方規範：轉換為 <專案>/.cursor/rules/*.mdc，配置 globs 與 alwaysApply",
                "path": str(cursor_dir),
                "is_default": False,
                "project_root": str(proj_root),
                "exists": cursor_dir.exists()
            },
            {
                "id": "opencode",
                "name": "OpenCode 專案 Agent (.opencode/agents)",
                "description": "官方規範：安裝至 <專案>/.opencode/agents/*.md，配置 mode: subagent",
                "path": str(opencode_dir),
                "is_default": False,
                "project_root": str(proj_root),
                "exists": opencode_dir.exists()
            },
            {
                "id": "qwen",
                "name": "Qwen Code 全域 Subagent (~/.qwen/agents)",
                "description": "官方規範：安裝至 ~/.qwen/agents/*.md，配置 role: subagent",
                "path": str(qwen_dir),
                "is_default": False,
                "project_root": "",
                "exists": qwen_dir.exists()
            },
            {
                "id": "codex",
                "name": "Codex 自訂 Agent (~/.codex/agents)",
                "description": "官方規範：安裝至 ~/.codex/agents/*.toml 格式",
                "path": str(codex_dir),
                "is_default": False,
                "project_root": "",
                "exists": codex_dir.exists()
            },
            {
                "id": "custom",
                "name": "自訂任意資料夾 (Custom Path)",
                "description": "自由指定本機電腦上的任意目錄路徑",
                "path": "",
                "is_default": False,
                "project_root": "",
                "exists": False
            }
        ]

    def _resolve_target_dir(self, target_type: str, custom_path: Optional[str] = None, project_path: Optional[str] = None) -> Path:
        """解析目標資料夾路徑並自動建立"""
        proj_root = Path(project_path) if project_path else self.default_project_root

        if target_type == "antigravity_project":
            target_dir = proj_root / ".agents" / "agents"
        elif target_type in ["antigravity_global", "gemini_global"]:
            target_dir = self.home_dir / ".gemini" / "config" / "agents"
        elif target_type == "claude_code":
            target_dir = self.home_dir / ".claude" / "agents"
        elif target_type == "cursor":
            target_dir = proj_root / ".cursor" / "rules"
        elif target_type == "opencode":
            target_dir = proj_root / ".opencode" / "agents"
        elif target_type == "qwen":
            target_dir = self.home_dir / ".qwen" / "agents"
        elif target_type == "codex":
            target_dir = self.home_dir / ".codex" / "agents"
        elif target_type == "custom":
            if not custom_path:
                raise ValueError("自訂目錄模式必須提供有效路徑")
            target_dir = Path(custom_path)
        else:
            raise ValueError(f"未知的安裝目標: {target_type}")

        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def get_installed_agent_ids(self, target_type: str, custom_path: Optional[str] = None, project_path: Optional[str] = None) -> List[str]:
        """檢查指定目標目錄中已安裝的 Agent ID 清單"""
        try:
            target_dir = self._resolve_target_dir(target_type, custom_path, project_path)
            if not target_dir.exists():
                return []

            installed = []
            for item in target_dir.iterdir():
                if item.is_file() and item.suffix in [".md", ".mdc", ".toml"]:
                    installed.append(item.stem)

            return installed
        except Exception as e:
            print(f"Error checking installed agents: {e}")
            return []

    def get_installed_agents_status(
        self,
        target_type: str,
        custom_path: Optional[str] = None,
        project_path: Optional[str] = None,
        agent_manager: Optional[Any] = None
    ) -> Dict[str, Any]:
        """檢查指定目標目錄中已安裝的 Agent 清單及其是否需要更新 (has_update)"""
        try:
            target_dir = self._resolve_target_dir(target_type, custom_path, project_path)
            if not target_dir.exists():
                return {
                    "installed_ids": [],
                    "updates_map": {},
                    "updates_count": 0,
                    "agents_with_updates": []
                }

            installed_ids = []
            updates_map = {}
            agents_with_updates = []

            for item in target_dir.iterdir():
                if item.is_file() and item.suffix in [".md", ".mdc", ".toml"]:
                    agent_id = item.stem
                    installed_ids.append(agent_id)
                    
                    has_update = False
                    if agent_manager:
                        agent = agent_manager.get_agent(agent_id)
                        if agent:
                            try:
                                with open(item, "r", encoding="utf-8", errors="ignore") as f:
                                    local_content = f.read().replace("\r\n", "\n").strip()
                                expected_content = self._convert_to_subagent_format(agent, target_type).replace("\r\n", "\n").strip()
                                if local_content != expected_content:
                                    has_update = True
                            except Exception as ex:
                                print(f"Error checking update for agent {agent_id}: {ex}")
                    
                    updates_map[agent_id] = has_update
                    if has_update:
                        agents_with_updates.append(agent_id)

            return {
                "installed_ids": installed_ids,
                "updates_map": updates_map,
                "updates_count": len(agents_with_updates),
                "agents_with_updates": agents_with_updates
            }
        except Exception as e:
            print(f"Error checking installed agents status: {e}")
            return {
                "installed_ids": [],
                "updates_map": {},
                "updates_count": 0,
                "agents_with_updates": []
            }

    def _convert_to_subagent_format(self, agent: Dict[str, Any], target_type: str) -> str:
        """依據官方規範生成 Subagent 檔案內容（100% 保持與官方來源相同的英文提示詞主體）"""
        name_en = agent.get("name_en", "")
        slug = agent.get("id", "")
        desc_en = agent.get("description_en", agent.get("description", ""))
        vibe_en = agent.get("vibe_en", agent.get("vibe", ""))
        division_zh = agent.get("division_name_zh", "")
        tags = agent.get("tags", [])
        
        # 100% 原始官方 Prompt Markdown 主體
        body = agent.get("body_markdown", agent.get("raw_markdown", ""))

        if target_type in ["antigravity_project", "antigravity_global", "gemini_global"]:
            # Google Antigravity 官方規範 (https://antigravity.google/docs/subagents/)
            return f"""---
name: {slug}
description: >-
  {desc_en}
subagent: true
model: inherit
enable_write_tools: true
enable_mcp_tools: true
tags:
{self._format_yaml_list(tags)}
division: "{division_zh}"
vibe: "{vibe_en}"
---

{body}
"""

        elif target_type == "claude_code":
            # Claude Code 官方規範
            return f"""---
name: {name_en}
description: >-
  {desc_en}
tools:
  - Read
  - Write
  - Bash
  - Glob
---

{body}
"""

        elif target_type == "cursor":
            # Cursor Rules 官方規範
            return f"""---
description: "{desc_en}"
globs: "*"
alwaysApply: false
---

{body}
"""

        elif target_type == "opencode":
            # OpenCode 官方規範
            return f"""---
name: {name_en}
description: >-
  {desc_en}
mode: subagent
---

{body}
"""

        elif target_type == "qwen":
            # Qwen Code 官方規範
            return f"""---
name: {name_en}
description: >-
  {desc_en}
role: subagent
---

{body}
"""

        elif target_type == "codex":
            # Codex 官方規範
            escaped_desc = desc_en.replace('"', '\\"')
            return f"""name = "{name_en}"
description = "{escaped_desc}"
developer_instructions = '''
{body}
'''
"""

        else:
            # 通用自訂格式
            return f"""---
name: {slug}
description: >-
  {desc_en}
subagent: true
---

{body}
"""

    def _format_yaml_list(self, items: List[str]) -> str:
        """格式化為乾淨的 YAML 清單語法"""
        if not items:
            return "  - general"
        return "\n".join(f"  - {item}" for item in items)

    def install_agent(
        self,
        agent: Dict[str, Any],
        target_type: str = "antigravity_project",
        custom_path: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """安裝單個 Subagent（只寫入單一指定目標目錄，絕不重複安裝）"""
        try:
            target_dir = self._resolve_target_dir(target_type, custom_path, project_path)
            
            ext = ".toml" if target_type == "codex" else (".mdc" if target_type == "cursor" else ".md")
            target_file = target_dir / f"{agent['id']}{ext}"

            content = self._convert_to_subagent_format(agent, target_type)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "agent_id": agent["id"],
                "file_path": str(target_file),
                "message": f"成功依規範安裝【{agent['name_zh']} ({agent['name_en']})】至 {target_file.name}"
            }
        except Exception as e:
            return {
                "success": False,
                "agent_id": agent.get("id"),
                "message": f"安裝失敗: {str(e)}"
            }

    def install_batch(
        self,
        agents: List[Dict[str, Any]],
        target_type: str = "antigravity_project",
        custom_path: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """批次安裝多個 Subagent"""
        success_count = 0
        failed_count = 0
        details = []

        for agent in agents:
            res = self.install_agent(agent, target_type, custom_path, project_path)
            if res["success"]:
                success_count += 1
            else:
                failed_count += 1
            details.append(res)

        return {
            "success": failed_count == 0,
            "total": len(agents),
            "success_count": success_count,
            "failed_count": failed_count,
            "details": details,
            "message": f"批次安裝完成：成功 {success_count} 位，失敗 {failed_count} 位"
        }

    def uninstall_agent(
        self,
        agent_id: str,
        target_type: str = "antigravity_project",
        custom_path: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """解除安裝單個 Subagent"""
        try:
            target_dir = self._resolve_target_dir(target_type, custom_path, project_path)
            ext = ".toml" if target_type == "codex" else (".mdc" if target_type == "cursor" else ".md")
            target_file = target_dir / f"{agent_id}{ext}"

            removed = False
            if target_file.exists():
                target_file.unlink()
                removed = True

            # 額外清理歷史遺留的舊相容目錄檔案（若有）
            if target_type == "antigravity_project":
                legacy_file = (Path(project_path) if project_path else self.default_project_root) / ".agent" / "agents" / f"{agent_id}{ext}"
                if legacy_file.exists():
                    legacy_file.unlink()
                    removed = True

            if removed:
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "message": f"已成功移除 {target_file.name}"
                }
            else:
                return {
                    "success": False,
                    "agent_id": agent_id,
                    "message": f"檔案不存在: {target_file.name}"
                }
        except Exception as e:
            return {
                "success": False,
                "agent_id": agent_id,
                "message": f"移除失敗: {str(e)}"
            }

    def uninstall_batch(
        self,
        agent_ids: List[str],
        target_type: str = "antigravity_project",
        custom_path: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """批次解除安裝多個 Subagent"""
        success_count = 0
        failed_count = 0
        details = []

        for aid in agent_ids:
            res = self.uninstall_agent(aid, target_type, custom_path, project_path)
            if res["success"]:
                success_count += 1
            else:
                failed_count += 1
            details.append(res)

        return {
            "success": failed_count == 0,
            "total": len(agent_ids),
            "success_count": success_count,
            "failed_count": failed_count,
            "details": details,
            "message": f"批次移除完成：成功 {success_count} 位，失敗 {failed_count} 位"
        }

    def get_default_rule_content(self, target_type: str = "antigravity_project") -> str:
        """獲取高密度、節省 Token 且具備 Loop Engineering 閉環機制的 Subagent 協作規範 (優先自 data/rules 讀取已同步最新範本)"""
        # 1. 優先嘗試讀取本機已同步的最新 Rule 檔案
        if self.rules_dir.exists():
            rule_file = self.rules_dir / ("cursor-collaboration.mdc" if target_type == "cursor" else "subagent-collaboration.md")
            if rule_file.exists():
                try:
                    with open(rule_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            return content
                except Exception:
                    pass

        # 2. 內建預設模板降級回退 (Fallback)
        if target_type == "cursor":
            return """---
description: "Enforce Subagent-First Orchestration & Loop Engineering across all domains (Consult -> Delegate -> Verify/Test -> Iteration Loop -> Quality Gate Delivery)."
globs: "*"
alwaysApply: true
---

# 🤖 Subagent-First Loop Engineering Protocol (Cursor Mode)

## 🎯 Role Mandate: Chief Orchestrator & Quality Gatekeeper
You are the **Chief Orchestrator & Quality Gatekeeper**. You **MUST NEVER** act as a solo executor for non-trivial tasks across code, design, product, marketing, or strategy. You strictly orchestrate specialized domain subagents and enforce empirical closed-loop verification.

---

## 🚦 Decision Matrix (Strict Triage)
- **Trivial (Solo Allowed)**: Typos, comments, single-line variable renaming (≤ 5 lines), pure read-only answers.
- **Non-Trivial (SUBAGENTS MANDATORY)**: Code changes (> 5 lines), design specs, PRDs, marketing copy, research audits, prompt optimizations. **PROHIBITED from generating deliverables solo.** Must delegate to subagents.

---

## 🔄 6-Stage Closed-Loop Workflow
1. **CONSULT & AC**: Consult relevant domain subagents (e.g., orchestrator, architect, designer, product manager, QA). Formulate testable Acceptance Criteria (AC: Given-When-Then).
2. **DECONSTRUCT & DELEGATE**: Break objectives into single-responsibility subtasks. Dispatch to subagents with strict boundaries and expected outputs.
3. **ISOLATED EXECUTION**: Subagents implement targeted solutions without polluting the main context window.
4. **EMPIRICAL VERIFICATION GATE**: Run real automated tests (`pytest`, `npm test`, `tsc`) for code, or schema/AC validation for non-code deliverables. **Zero Assumption**: Output is unverified until terminal logs or empirical proof confirm 100% pass.
5. **LOOP ITERATION**: 
   - ❌ **On Failure**: Extract exact terminal stack trace / defect critique -> Package as feedback -> Dispatch back to subagent (`loop_count++`) -> Re-verify until green.
   - ❌ **No Solo Patching**: Do NOT fix subagent errors directly in the main composer.
6. **GATEKEEPER DELIVERY**: Verify all Stage 1 ACs against diff evidence. Deliver final walkthrough with verified logs/evidence.

---

## 🚫 Forbidden Anti-Patterns
- ❌ **No Solo Execution**: Never generate non-trivial deliverables without subagent delegation.
- ❌ **No Blind Delivery**: Never mark tasks done without running verification commands.
- ❌ **No Spec Weakening**: Never weaken test assertions or AC to mask underlying bugs.
- ❌ **No Silent Error Ignoring**: All terminal errors must be fed back to subagents.
"""
        else:
            return """---
description: Enforce Subagent-First Orchestration & Loop Engineering Protocol across all domains (Triage -> Consult -> Delegate -> Verify/Test -> Loop Iteration -> Quality Gate Delivery).
always_on: true
---

# 🤖 Subagent-First Loop Engineering Protocol (Universal & Multi-Domain)

## 🎯 Core Mandate: Chief Orchestrator & Quality Gatekeeper
You are the **Chief Orchestrator & Quality Gatekeeper**. You **MUST NEVER** act as a solo executor for non-trivial tasks across engineering, product design, marketing, research, strategy, or operations. Your core responsibility is to coordinate domain-expert subagents, enforce architectural and domain consistency, and drive iterative closed-loop verification (**Loop Engineering**).

---

## 🚦 Decision Matrix: When Subagents are MANDATORY

Before executing any action, evaluate your task against this matrix:

| Task Characteristics | Classification | Required Workflow |
| :--- | :--- | :--- |
| • Minor typo / comment / formatting tweak (≤ 5 lines)<br>• Read-only inspection / answering basic conceptual questions | **Trivial (Solo Allowed)** | Direct execution permitted. |
| • **Code & DevOps**: Feature implementation (> 5 lines), refactoring, API/DB design, bug fixing, test suite creation<br>• **Design & UX**: Design contracts, UI components, user flow architecture, design tokens<br>• **Product & Strategy**: PRD drafting, roadmap decomposition, user story formulation<br>• **Marketing & Content**: Campaign strategy, SEO audit, copywriting, growth experiments<br>• **Research & Analysis**: Statistical modeling, domain investigation, audit reports<br>• **Prompt & Agents**: System prompt design, persona optimization, workflow tuning | **Non-Trivial (SUBAGENTS MANDATORY)** | **STRICTLY PROHIBITED from acting solo.** Must follow the 6-Stage Loop Engineering Cycle below. |

---

## 🔄 The 6-Stage Loop Engineering Cycle

```
[User Request] ──► [Stage 1: Consult & AC] ──► [Stage 2: Deconstruct & Delegate]
                          ▲                                  │
                          │                                  ▼
                 [Stage 5: Loop Feedback] ◄── [FAIL] ── [Stage 4: Verify & Test Gate]
                 (Send Evidence to Subagent)                 │ [PASS]
                          │                                  ▼
                 [Stage 3: Subagent Exec] ────────────► [Stage 6: Gatekeeper Delivery]
```

### Stage 1: Consult & Acceptance Criteria (AC) Formulation
- **Domain Specialist Identification**: Identify required specialists from the 255+ agent library (e.g., `@specialized-agents-orchestrator`, `@engineering-prompt-engineer`, `@backend-architect`, `@design-ui-designer`, `@product-product-manager`, `@marketing-growth-hacker`, `@academic-statistician`).
- **Expert Consultation**: Consult relevant subagents first to establish architecture, edge cases, methodologies, and constraints.
- **AC Specification**: Formulate explicit, testable Acceptance Criteria using standard format:
  ```markdown
  - AC-1: Given [precondition], When [action/input], Then [expected output/behavior].
  - AC-2: [Constraint / Edge-case verification criteria].
  ```

### Stage 2: Deconstruct & Subtask Delegation
- **Modular Breakdown**: Split the objective into isolated, single-responsibility subtasks.
- **Structured Dispatch**: Delegate tasks to subagents with:
  1. Specific scope & file/context boundaries.
  2. Input/Output contracts and AC references.
  3. Prohibited side effects or cross-domain pollution.

### Stage 3: Isolated Subagent Execution
- Domain subagents execute implementation within their specialized personas and clean context windows.
- Subagents produce precise code diffs, design specs, copies, configs, or research artifacts matching the specification.

### Stage 4: Empirical Verification & Test Gate (Zero Assumption)
- **For Code & Engineering**: Run automated test suites, linters, or build commands (`pytest`, `npm test`, `cargo test`, `tsc --noEmit`, etc.).
- **For Non-Code Deliverables**: Run schema validators, syntax linters, fact-check queries, or evaluate against Stage 1 AC checklists with tangible output evidence.
- **Zero Assumption Rule**: Output is considered **UNVERIFIED / DEFECTIVE** until proven by real terminal logs or structured empirical evidence. Imaginary test passes are strictly forbidden.

### Stage 5: Loop Iteration & Error Backpropagation
- ❌ **If Tests Fail, Errors Occur, or AC Criteria are Missed**:
  1. Extract the exact failure traceback, logs, or defect critique.
  2. Construct a **Feedback Packet** for the responsible Subagent:
     ```markdown
     - Failed Verification / Command: [Exact command / criteria]
     - Defect Log / Traceback: [Raw terminal error or specific defect evidence]
     - Root Cause Analysis: [Identified breakdown]
     - Target Correction: [Specific fix request]
     ```
  3. Subagent refactors implementation (Iterate `loop_count++` until 100% green/passed).
  4. Never patch subagent deliverables directly in the main orchestrator context.

### Stage 6: Gatekeeper Acceptance & Delivery
- ✅ **Delivery Criteria**:
  1. 100% of verification commands/tests pass (backed by real terminal logs).
  2. All Stage 1 Acceptance Criteria are verified against the deliverable diff.
  3. No regressions, lint errors, or unverified assumptions.
- Provide a concise summary walkthrough with evidence and file references.

---

## 🚫 Strict Anti-Patterns & Enforcement Rules

| Anti-Pattern | Violation Description | Enforced Remedy |
| :--- | :--- | :--- |
| ❌ **Solo Execution** | Main Agent producing non-trivial code, design, marketing copy, or PRDs alone without subagent delegation. | **IMMEDIATE HALT.** Invoke domain subagent expert before creating/editing files. |
| ❌ **Blind Delivery** | Claiming a task is complete without running real verification commands or presenting empirical evidence. | Execute verification checks and display proof. |
| ❌ **Ad-hoc Patching** | Main Agent attempting to fix subagent defects inline instead of looping back to subagent. | Extract error/defect log and dispatch back to the subagent. |
| ❌ **Spec Erosion** | Weakening test assertions or AC criteria to mask underlying failures. | Deliverables must satisfy AC. Never lower the quality bar. |
| ❌ **Skipping Consultation** | Jumping straight into generation without formulating AC or consulting domain experts. | Execute Stage 1 (Consult & AC) first. |

---

## 🛡️ Pre-Action Verification Protocol (Self-Check)

Before calling file editing or bash execution tools for non-trivial tasks, the Orchestrator MUST confirm:
1. `[TRIAGE]`: Is this task Non-Trivial across any domain? (Yes ➔ Delegate).
2. `[CONSULTED]`: Have domain subagent experts been consulted?
3. `[AC_DEFINED]`: Are testable Acceptance Criteria established?
4. `[EVIDENCE_READY]`: Is there a concrete verification command/method ready to execute?
"""

    def sync_rules_from_github(
        self,
        repo_owner_repo: str = "zhanallen/agency-subagents-manager",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """從使用者的 GitHub 倉庫同步最新協作規範 (Rule 模板)"""
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        files_to_sync = [
            "subagent-collaboration.md",
            "cursor-collaboration.mdc"
        ]
        
        updated = []
        errors = []
        
        for fname in files_to_sync:
            fetched_content = None
            
            # 策略 1: raw.githubusercontent.com
            raw_url = f"https://raw.githubusercontent.com/{repo_owner_repo}/{branch}/data/rules/{fname}"
            try:
                req = urllib.request.Request(
                    raw_url,
                    headers={"User-Agent": "AgencySubagentsManager-Sync/2.0"}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status == 200:
                        fetched_content = response.read().decode("utf-8")
            except Exception as e:
                pass

            # 策略 2: GitHub Contents API (備援)
            if not fetched_content:
                api_url = f"https://api.github.com/repos/{repo_owner_repo}/contents/data/rules/{fname}?ref={branch}"
                try:
                    req = urllib.request.Request(
                        api_url,
                        headers={"User-Agent": "AgencySubagentsManager-Sync/2.0"}
                    )
                    with urllib.request.urlopen(req, timeout=8) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode("utf-8"))
                            if "content" in data:
                                fetched_content = base64.b64decode(data["content"]).decode("utf-8")
                except Exception as e:
                    errors.append(f"{fname}: {str(e)}")

            if fetched_content:
                try:
                    target_file = self.rules_dir / fname
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(fetched_content)
                    updated.append(fname)
                except Exception as e:
                    errors.append(f"{fname} 寫入失敗: {str(e)}")
            else:
                if not any(fname in err for err in errors):
                    errors.append(f"{fname}: 未能自遠端取得內容")
        
        if updated:
            return {
                "success": True,
                "updated_files": updated,
                "message": f"成功自 {repo_owner_repo} 同步 {len(updated)} 個協作規範模板",
                "errors": errors
            }
        else:
            return {
                "success": False,
                "updated_files": [],
                "message": f"同步協作規範失敗 (已使用本機快取規範): {'; '.join(errors)}",
                "errors": errors
            }


    def get_rule_file_path(self, target_type: str = "antigravity_project", project_path: Optional[str] = None) -> Path:
        """獲取目標專案之協作 Rule 檔案完整路徑"""
        proj_root = Path(project_path) if project_path else self.default_project_root
        
        if target_type == "antigravity_project":
            return proj_root / ".agents" / "rules" / "subagent-collaboration.md"
        elif target_type in ["antigravity_global", "gemini_global"]:
            return self.home_dir / ".gemini" / "config" / "rules" / "subagent-collaboration.md"
        elif target_type == "cursor":
            return proj_root / ".cursor" / "rules" / "subagent-collaboration.mdc"
        elif target_type == "claude_code":
            return self.home_dir / ".claude" / "rules" / "subagent-collaboration.md"
        elif target_type == "opencode":
            return proj_root / ".opencode" / "rules" / "subagent-collaboration.md"
        else:
            return proj_root / ".agents" / "rules" / "subagent-collaboration.md"

    def check_rule_status(self, target_type: str = "antigravity_project", project_path: Optional[str] = None) -> Dict[str, Any]:
        """檢查協作 Rule 是否已安裝於目前目標專案，以及是否有新版本可更新"""
        try:
            rule_path = self.get_rule_file_path(target_type, project_path)
            exists = rule_path.exists()
            content = ""
            has_update = False
            if exists:
                try:
                    with open(rule_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    latest_content = self.get_default_rule_content(target_type)
                    norm_current = content.replace("\r\n", "\n").strip()
                    norm_latest = latest_content.replace("\r\n", "\n").strip()
                    if norm_current != norm_latest:
                        has_update = True
                except Exception:
                    pass
            return {
                "success": True,
                "is_installed": exists,
                "has_update": has_update,
                "file_path": str(rule_path),
                "file_name": rule_path.name,
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "is_installed": False,
                "has_update": False,
                "file_path": "",
                "message": str(e)
            }

    def install_collaboration_rule(
        self,
        target_type: str = "antigravity_project",
        project_path: Optional[str] = None,
        custom_content: Optional[str] = None,
        agent_manager: Optional[Any] = None,
        install_essential_agents: bool = True
    ) -> Dict[str, Any]:
        """一鍵安裝/更新 Subagent 協作工作流規範 (Rule) 並可自動配置核心協作專家"""
        try:
            rule_path = self.get_rule_file_path(target_type, project_path)
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = custom_content if custom_content else self.get_default_rule_content(target_type)
            with open(rule_path, "w", encoding="utf-8") as f:
                f.write(content)

            installed_agents = []
            if install_essential_agents:
                mgr = agent_manager
                if mgr is None:
                    try:
                        from services.agent_manager import AgentManager
                        mgr = AgentManager(str(self.default_project_root))
                    except Exception:
                        mgr = None

                if mgr:
                    for aid in ESSENTIAL_COLLABORATION_AGENT_IDS:
                        agent = mgr.get_agent(aid)
                        if agent:
                            res = self.install_agent(
                                agent=agent,
                                target_type=target_type,
                                project_path=project_path
                            )
                            if res.get("success"):
                                installed_agents.append(aid)

            rule_display_name = rule_path.relative_to(rule_path.parent.parent.parent) if len(rule_path.parts) > 3 else rule_path.name
            if installed_agents:
                msg = f"成功建立協作規範（{rule_display_name}），並已自動配置核心編排師、多代理系統架構師與提示詞工程師！"
            else:
                msg = f"成功建立協作規範：{rule_display_name}"

            return {
                "success": True,
                "file_path": str(rule_path),
                "installed_essential_agents": installed_agents,
                "essential_count": len(installed_agents),
                "message": msg
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"安裝協作規範失敗: {str(e)}"
            }

    def uninstall_collaboration_rule(
        self,
        target_type: str = "antigravity_project",
        project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """移除 Subagent 協作工作流規範 (Rule)"""
        try:
            rule_path = self.get_rule_file_path(target_type, project_path)
            if rule_path.exists():
                rule_path.unlink()
                return {
                    "success": True,
                    "message": f"已成功移除協作規範：{rule_path.name}"
                }
            return {
                "success": True,
                "message": "協作規範檔案原本就不存在"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"移除協作規範失敗: {str(e)}"
            }

