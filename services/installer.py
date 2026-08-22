import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class SubagentInstaller:
    """負責將 Agency Agents 轉換並安裝為符合各官方規範的 Subagent / Agent 定義檔 (嚴格單一目錄安裝，不重複寫入)"""

    def __init__(self, default_project_root: str):
        self.default_project_root = Path(default_project_root)
        self.home_dir = Path.home()

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
        """獲取高密度、節省 Token 且具備 Loop Engineering 閉環機制的 Subagent 協作規範 (English Rule)"""
        if target_type == "cursor":
            return """---
description: "Enforce Subagent-First Orchestration & Loop Engineering (Consult -> Delegate -> Automated Test -> Iteration Loop -> Quality Gate Delivery)."
globs: "*"
alwaysApply: true
---

# 🤖 Subagent-First Loop Engineering Rule

## 🎯 Core Mandate: Chief Orchestrator & Quality Gatekeeper
The Main Agent MUST NEVER act as a solo executor for complex tasks. The Main Agent acts exclusively as the **Chief Orchestrator & Quality Gatekeeper**, orchestrating specialized domain subagents through a rigorous, test-driven **Loop Engineering Cycle**.

---

## 🔄 The Loop Engineering Cycle (5-Stage Closed Loop)

1. **CONSULT**: Before writing code, consult specialized domain subagents (e.g., frontend, backend, security, QA) to establish architecture, edge cases, and testable Acceptance Criteria (AC).
2. **DECONSTRUCT & DELEGATE**: Break the objective into single-responsibility subtasks. Dispatch to Subagents in isolated context windows.
3. **EXECUTE**: Subagents implement targeted solutions without context window pollution.
4. **AUTOMATED TEST GATE**: Subagents/Main Agent MUST run automated unit tests, linters, or build commands. NEVER declare completion without concrete test execution evidence.
5. **EVALUATION & ITERATION LOOP**:
   - ❌ **On Failure / Regression**: Capture failure logs/traces, feed them back to the Subagent (`loop_iteration++`), and re-test until green.
   - ✅ **On 100% Pass**: Synthesize results, verify acceptance criteria, and deliver final walkthrough.

## 🚫 Strict Anti-Patterns
- ❌ **No Solo Coding**: Main Agent must not bypass expert subagents.
- ❌ **No Blind Delivery**: Never mark tasks done without running tests.
"""
        else:
            return """---
description: Enforce Subagent-First Orchestration & Loop Engineering (Consult -> Delegate -> Automated Test -> Iteration Loop -> Quality Gate Delivery).
always_on: true
---

# 🤖 Subagent-First Loop Engineering Rule

## 🎯 Core Mandate: Chief Orchestrator & Quality Gatekeeper
The Main Agent MUST NEVER act as a solo executor for complex tasks. The Main Agent acts exclusively as the **Chief Orchestrator & Quality Gatekeeper**, orchestrating specialized domain subagents through a rigorous, test-driven **Loop Engineering Cycle**.

---

## 🔄 The Loop Engineering Cycle (5-Stage Closed Loop)

```
[User Request]
       │
       ▼
 ┌─────────────┐
 │ 1. CONSULT  │ ◄─── Consult specialized domain subagents first
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ 2. DELEGATE │ ◄─── Deconstruct into focused tasks & assign to subagents
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ 3. EXECUTE  │ ◄─── Subagent implements in isolated context window
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ 4. TEST/RUN │ ◄─── Execute automated tests, linters, or build checks
 └──────┬──────┘
        │
   [Pass / Fail?]
   ┌────┴────────────────────────┐
   │ FAIL                        │ PASS (100% Verified)
   ▼                             ▼
┌──────────────────┐      ┌─────────────┐
│ 5a. ITERATE LOOP │      │ 5b. DELIVER │ ──► [Walkthrough & Verified Output]
│ (Feed error back │      └─────────────┘
│  to Subagent)    │
└────────┬─────────┘
         │
         └───► Returns to Stage 3 (Iterate until green)
```

### Stage 1: Consult & Spec
- Identify required domains (Frontend, Backend, Security, QA, UI/UX) and invoke/consult relevant Subagents.
- Establish architecture, boundaries, and concrete **Acceptance Criteria (AC)**.

### Stage 2: Deconstruct & Delegate
- Split complex workflows into modular, single-responsibility subtasks.
- Dispatch clear task instructions to Subagents in isolated context windows.

### Stage 3: Subagent Execution
- Subagents execute code, configs, or styling within their specialized personas.

### Stage 4: Automated Test & Verification Gate
- Every change MUST be verified with real automated tests (`pytest`, `npm test`, `cargo test`), linters, or build commands.
- **Zero Assumption**: Code is unverified until test logs prove it.

### Stage 5: Evaluation & Loop Iteration Gate
- ❌ **If Tests Fail / Defects Found**:
  - Main Agent extracts failure traces and feeds them back to the Subagent.
  - Subagent refactors and re-runs tests until 100% pass.
- ✅ **If All Tests Pass & Quality Gates Cleared**:
  - Main Agent synthesizes verified changes and delivers the final walkthrough.

---

## 🚫 Strict Anti-Patterns
- ❌ **Solo Implementation**: Main Agent attempting to write all code and debug alone.
- ❌ **Blind Delivery**: Claiming a task is complete without running verification commands.
- ❌ **Skipping Consultation**: Starting implementation without expert Subagent input.
"""

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
        """檢查協作 Rule 是否已安裝於目前目標專案"""
        try:
            rule_path = self.get_rule_file_path(target_type, project_path)
            exists = rule_path.exists()
            content = ""
            if exists:
                try:
                    with open(rule_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception:
                    pass
            return {
                "success": True,
                "is_installed": exists,
                "file_path": str(rule_path),
                "file_name": rule_path.name,
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "is_installed": False,
                "file_path": "",
                "message": str(e)
            }

    def install_collaboration_rule(
        self,
        target_type: str = "antigravity_project",
        project_path: Optional[str] = None,
        custom_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """一鍵安裝/更新 Subagent 協作工作流規範 (Rule)"""
        try:
            rule_path = self.get_rule_file_path(target_type, project_path)
            rule_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = custom_content if custom_content else self.get_default_rule_content(target_type)
            with open(rule_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "success": True,
                "file_path": str(rule_path),
                "message": f"成功建立協作規範：{rule_path.relative_to(rule_path.parent.parent.parent) if len(rule_path.parts) > 3 else rule_path.name}"
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

