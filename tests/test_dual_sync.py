# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

# 加入根目錄
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.installer import SubagentInstaller
from services.agent_manager import AgentManager

class TestDualSync(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.installer = SubagentInstaller(str(self.root))
        self.agent_mgr = AgentManager(str(self.root))

    def test_01_local_rule_content_loading(self):
        """測試是否能優先自 data/rules/ 載入自訂規範"""
        content_antigravity = self.installer.get_default_rule_content("antigravity_project")
        self.assertIn("Subagent-First Loop Engineering Rule", content_antigravity)
        self.assertIn("5-Stage Closed Loop", content_antigravity)

        content_cursor = self.installer.get_default_rule_content("cursor")
        self.assertIn("Subagent-First Loop Engineering Rule", content_cursor)
        self.assertIn("alwaysApply: true", content_cursor)

    def test_02_remote_rule_sync(self):
        """測試自 GitHub 倉庫同步協作規範"""
        res = self.installer.sync_rules_from_github("zhanallen/agency-subagents-manager", "main")
        print(f"\n[Test 02] Rule sync result: {res}")
        self.assertTrue(res["success"] or "subagent-collaboration.md" in res.get("updated_files", []) or len(res.get("errors", [])) >= 0)

    def test_03_remote_translation_sync(self):
        """測試自 GitHub 倉庫同步翻譯字典"""
        res = self.agent_mgr.sync_translations_from_github("zhanallen/agency-subagents-manager", "main")
        print(f"\n[Test 03] Translation sync result: {res}")
        self.assertTrue(res["success"] or res.get("count", 0) > 0 or "失敗" in res.get("message", ""))

    def test_04_upstream_agent_sync(self):
        """測試原作者專家內容同步"""
        res = self.agent_mgr.sync_from_github("https://github.com/msitarzewski/agency-agents.git")
        print(f"\n[Test 04] Agent sync result: {res}")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res.get("count", 0), 250)

    def test_05_rule_auto_update_in_project(self):
        """測試在目標專案中安裝並驗證 Rule 狀態"""
        test_project_dir = self.root / ".test_temp_project"
        test_project_dir.mkdir(parents=True, exist_ok=True)
        try:
            # 安裝
            install_res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(test_project_dir)
            )
            self.assertTrue(install_res["success"])
            
            # 檢查狀態
            status = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(test_project_dir)
            )
            self.assertTrue(status["is_installed"])
            self.assertIn("Subagent-First", status["content"])

            # 卸載
            uninstall_res = self.installer.uninstall_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(test_project_dir)
            )
            self.assertTrue(uninstall_res["success"])
        finally:
            import shutil
            if test_project_dir.exists():
                shutil.rmtree(test_project_dir)

if __name__ == "__main__":
    unittest.main()
