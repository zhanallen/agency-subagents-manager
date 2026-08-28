# -*- coding: utf-8 -*-
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.installer import SubagentInstaller

class TestLoopEngineeringRule(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.installer = SubagentInstaller(str(self.root))

    def test_01_antigravity_rule_structure(self):
        """Test Antigravity 6-Stage Loop Engineering Protocol structure and keywords"""
        content = self.installer.get_default_rule_content("antigravity_project")
        
        # Core Identity & Mandate
        self.assertIn("Subagent-First Loop Engineering Protocol", content)
        self.assertIn("Chief Orchestrator & Quality Gatekeeper", content)
        
        # Decision Matrix
        self.assertIn("Decision Matrix: When Subagents are MANDATORY", content)
        self.assertIn("Trivial (Solo Allowed)", content)
        self.assertIn("Non-Trivial (SUBAGENTS MANDATORY)", content)
        
        # 6 Stages
        self.assertIn("Stage 1: Consult & Acceptance Criteria (AC) Formulation", content)
        self.assertIn("Stage 2: Deconstruct & Subtask Delegation", content)
        self.assertIn("Stage 3: Isolated Subagent Execution", content)
        self.assertIn("Stage 4: Empirical Verification & Test Gate (Zero Assumption)", content)
        self.assertIn("Stage 5: Loop Iteration & Error Backpropagation", content)
        self.assertIn("Stage 6: Gatekeeper Acceptance & Delivery", content)
        
        # Feedback Packet & Self Check
        self.assertIn("Feedback Packet", content)
        self.assertIn("Strict Anti-Patterns & Enforcement Rules", content)
        self.assertIn("Pre-Action Verification Protocol (Self-Check)", content)

    def test_02_cursor_rule_structure(self):
        """Test Cursor MDC Loop Engineering structure and frontmatter"""
        content = self.installer.get_default_rule_content("cursor")
        
        self.assertIn('globs: "*"', content)
        self.assertIn("alwaysApply: true", content)
        self.assertIn("Subagent-First Loop Engineering Protocol (Cursor Mode)", content)
        self.assertIn("Decision Matrix (Strict Triage)", content)
        self.assertIn("6-Stage Closed-Loop Workflow", content)
        self.assertIn("Forbidden Anti-Patterns", content)

    def test_03_installer_rule_lifecycle(self):
        """Test rule install, status check, and uninstall in a temporary project directory"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_rule_lifecycle_"))
        try:
            # Check not installed
            status = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertFalse(status["is_installed"])

            # Install
            res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(res["success"])

            # Check installed
            status_after = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(status_after["is_installed"])
            self.assertIn("Subagent-First Loop Engineering Protocol", status_after["content"])

            # Uninstall
            un_res = self.installer.uninstall_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(un_res["success"])

            # Check not installed
            status_final = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertFalse(status_final["is_installed"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_04_auto_install_essential_subagents(self):
        """Test that installing collaboration rule automatically installs essential subagents"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_essential_subagents_"))
        try:
            from services.installer import ESSENTIAL_COLLABORATION_AGENT_IDS
            res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir),
                install_essential_agents=True
            )
            self.assertTrue(res["success"])
            self.assertEqual(res.get("essential_count", 0), 3)
            self.assertIn("specialized-agents-orchestrator", res.get("installed_essential_agents", []))
            self.assertIn("engineering-multi-agent-systems-architect", res.get("installed_essential_agents", []))
            self.assertIn("engineering-prompt-engineer", res.get("installed_essential_agents", []))

            # Verify files on disk
            installed_ids = self.installer.get_installed_agent_ids(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            for eid in ESSENTIAL_COLLABORATION_AGENT_IDS:
                self.assertIn(eid, installed_ids)
                agent_file = temp_dir / ".agents" / "agents" / f"{eid}.md"
                self.assertTrue(agent_file.exists())
                with open(agent_file, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    self.assertIn("subagent: true", file_content)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
