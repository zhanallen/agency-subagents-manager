# -*- coding: utf-8 -*-
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from services.installer import SubagentInstaller
from services.agent_manager import AgentManager
from app import get_agents, get_agent_detail, check_updates, apply_all_updates, UpdateAllRequest, agent_manager as app_agent_mgr, installer as app_installer

class TestUpdateDetection(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.agent_mgr = app_agent_mgr
        self.agent_mgr.load_translations()
        self.agent_mgr.load_agents()
        self.installer = app_installer

    def test_01_agent_update_detection(self):
        """測試子代理安裝後之內容比對與更新檢測"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_agent_update_"))
        try:
            agent_id = "engineering-frontend-developer"
            agent = self.agent_mgr.get_agent(agent_id)
            self.assertIsNotNone(agent)

            # 1. 安裝子代理
            res = self.installer.install_agent(
                agent=agent,
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(res["success"])

            # 2. 檢測初始安裝狀態：應為最新 (has_update = False)
            status = self.installer.get_installed_agents_status(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr
            )
            self.assertIn(agent_id, status["installed_ids"])
            self.assertFalse(status["updates_map"].get(agent_id))
            self.assertEqual(status["updates_count"], 0)

            # 3. 模擬本地檔案被修改或雲端定義已更新（修改本地檔案內容）
            installed_file = temp_dir / ".agents" / "agents" / f"{agent_id}.md"
            self.assertTrue(installed_file.exists())
            with open(installed_file, "a", encoding="utf-8") as f:
                f.write("\n\n<!-- Local modified comment -->\n")

            # 4. 再次檢測：應識別出 has_update = True
            status_after_mod = self.installer.get_installed_agents_status(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr
            )
            self.assertTrue(status_after_mod["updates_map"].get(agent_id))
            self.assertEqual(status_after_mod["updates_count"], 1)
            self.assertIn(agent_id, status_after_mod["agents_with_updates"])

            # 5. 執行更新（重新覆寫安裝）
            update_res = self.installer.install_agent(
                agent=agent,
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(update_res["success"])

            # 6. 更新後檢測：應恢復為 has_update = False
            status_after_update = self.installer.get_installed_agents_status(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr
            )
            self.assertFalse(status_after_update["updates_map"].get(agent_id))
            self.assertEqual(status_after_update["updates_count"], 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_02_rule_update_detection(self):
        """測試協作規範安裝後之內容比對與更新檢測"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_rule_update_"))
        try:
            # 1. 安裝協作規範
            install_res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr,
                install_essential_agents=False
            )
            self.assertTrue(install_res["success"])

            # 2. 檢測初始規範狀態：應為最新 (has_update = False)
            status = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(status["is_installed"])
            self.assertFalse(status["has_update"])

            # 3. 模擬專案內規範內容為舊版或被自訂修改
            rule_file = temp_dir / ".agents" / "rules" / "subagent-collaboration.md"
            self.assertTrue(rule_file.exists())
            with open(rule_file, "w", encoding="utf-8") as f:
                f.write("# Old Rule Version Content\n")

            # 4. 再次檢測：應識別出 has_update = True
            status_after_mod = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(status_after_mod["is_installed"])
            self.assertTrue(status_after_mod["has_update"])

            # 5. 升級規範至最新版
            upgrade_res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr,
                install_essential_agents=False
            )
            self.assertTrue(upgrade_res["success"])

            # 6. 升級後檢測：應恢復為 has_update = False
            status_after_upgrade = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(status_after_upgrade["is_installed"])
            self.assertFalse(status_after_upgrade["has_update"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_03_agent_manager_filter_updates(self):
        """測試 AgentManager 之 filter_status='updates' 篩選"""
        updates_map = {
            "engineering-frontend-developer": True,
            "engineering-backend-architect": False
        }
        installed_ids = ["engineering-frontend-developer", "engineering-backend-architect"]

        results = self.agent_mgr.search_agents(
            installed_ids=installed_ids,
            filter_status="updates",
            updates_map=updates_map
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "engineering-frontend-developer")

    def test_04_api_endpoints_update_payload(self):
        """測試 API 端點 get_agents 與 check_updates 之回傳欄位與狀態"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_api_update_"))
        try:
            agent = self.agent_mgr.get_agent("engineering-frontend-developer")
            self.installer.install_agent(
                agent=agent,
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )

            # 修改使之可更新
            installed_file = temp_dir / ".agents" / "agents" / "engineering-frontend-developer.md"
            with open(installed_file, "a", encoding="utf-8") as f:
                f.write("\n<!-- change -->")

            # 測試 get_agents
            data = asyncio.run(get_agents(target_type="antigravity_project", project_path=str(temp_dir)))
            self.assertTrue(data["success"])
            self.assertEqual(data["updates_count"], 1)
            self.assertIn("engineering-frontend-developer", data["agents_with_updates"])

            found = next((a for a in data["agents"] if a["id"] == "engineering-frontend-developer"), None)
            self.assertIsNotNone(found)
            self.assertTrue(found["is_installed"])
            self.assertTrue(found["has_update"])

            # 測試 check_updates
            check_data = asyncio.run(check_updates(target_type="antigravity_project", project_path=str(temp_dir)))
            self.assertTrue(check_data["success"])
            self.assertEqual(check_data["agents_updates_count"], 1)
            self.assertIn("engineering-frontend-developer", check_data["agents_with_updates"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_05_apply_all_updates(self):
        """測試一鍵更新全部過期 Subagent 與協作規範"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_apply_all_"))
        try:
            # 安裝子代理與規則
            agent = self.agent_mgr.get_agent("engineering-frontend-developer")
            self.installer.install_agent(
                agent=agent,
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                install_essential_agents=False
            )

            # 修改使之過期
            agent_file = temp_dir / ".agents" / "agents" / "engineering-frontend-developer.md"
            with open(agent_file, "a", encoding="utf-8") as f:
                f.write("\n<!-- outdated -->")

            rule_file = temp_dir / ".agents" / "rules" / "subagent-collaboration.md"
            with open(rule_file, "w", encoding="utf-8") as f:
                f.write("# Outdated Rule\n")

            # 執行一鍵更新
            req = UpdateAllRequest(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                update_rule=True,
                update_agents=True
            )
            result = asyncio.run(apply_all_updates(req))
            self.assertTrue(result["success"])
            self.assertEqual(result["total_updated"], 2)
            self.assertIn("engineering-frontend-developer", result["updated_agents"])
            self.assertTrue(result["rule_updated"])

            # 驗證更新後皆無更新
            status = self.installer.get_installed_agents_status(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                agent_manager=self.agent_mgr
            )
            self.assertEqual(status["updates_count"], 0)

            rule_status = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertFalse(rule_status["has_update"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
