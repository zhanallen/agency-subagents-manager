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
        """Test Antigravity Multi-Agent Architecture Protocol structure and keywords"""
        content = self.installer.get_default_rule_content("antigravity_project")
        
        # Core Identity & Mandate
        self.assertIn("MULTI-AGENT ARCHITECTURE GOVERNANCE", content)
        self.assertIn("Chief Orchestrator & Quality Gatekeeper", content)
        self.assertIn("CONDITION-LOCKED", content)
        self.assertIn("STRICTLY PROHIBITED FROM SELF-APPROVING", content)
        
        # Multi-Agent State Machine & Pre-Flight Gate
        self.assertIn("MULTI-AGENT GOVERNANCE STATE MACHINE", content)
        self.assertIn("PHASE 0: ARCHITECTURE & ROSTER CONSULTATION", content)
        self.assertIn("Specialist Roster Formulation", content)
        self.assertIn("MANDATORY PRE-FLIGHT CHECK", content)
        self.assertIn("SELF-REFUSE DIRECT FILE WRITING", content)
        
        # 6 Stages with Multi-Agent Roster & Sandbox/Visual Sign-off Gates
        self.assertIn("Stage 1: Multi-Agent Architecture & Specialist Roster Consultation (Phase 0)", content)
        self.assertIn("Stage 2: Deconstruct & Subtask Delegation", content)
        self.assertIn("Stage 3: Isolated Subagent Execution", content)
        self.assertIn("Stage 4: Empirical Sandbox & Visual Verification Gate (Zero Assumption)", content)
        self.assertIn("Stage 5: Loop Iteration & Error Backpropagation", content)
        self.assertIn("Stage 6: Independent Subagent Sign-off & Gatekeeper Delivery", content)
        
        # Sandbox, UI Screenshot & Independent Subagent Audits
        self.assertIn("Mandatory Visual Screenshot Review Gate", content)
        self.assertIn("Code Inspection Is NOT Visual Proof", content)
        self.assertIn("engineering-multi-agent-systems-architect", content)
        self.assertIn("engineering-code-reviewer", content)
        self.assertIn("design-ui-finish-gate-reviewer", content)
        
        # Contrastive Few-Shot Examples, Anti-Patterns & Feedback Packet
        self.assertIn("Feedback Packet", content)
        self.assertIn("CONTRASTIVE FEW-SHOT EXAMPLES", content)
        self.assertIn("NO_ROSTER_BYPASS", content)
        self.assertIn("NO_SELF_SIGNOFF", content)
        self.assertIn("NO_SCREENSHOT_NO_UI_DELIVERY", content)
        self.assertIn("ZERO_ASSUMPTION_SANDBOX", content)

    def test_02_cursor_rule_structure(self):
        """Test Cursor MDC Multi-Agent Governance structure and frontmatter"""
        content = self.installer.get_default_rule_content("cursor")
        
        self.assertIn('globs: "*"', content)
        self.assertIn("alwaysApply: true", content)
        self.assertIn("HARD TOOL INTERCEPTION & MULTI-AGENT GOVERNANCE PROTOCOL (CURSOR MODE)", content)
        self.assertIn("MANDATORY PRE-FLIGHT GATE", content)
        self.assertIn("6-STAGE CLOSED-LOOP WORKFLOW", content)
        self.assertIn("STAGE 1 - MULTI-AGENT ARCHITECTURE & ROSTER", content)
        self.assertIn("EMPIRICAL SANDBOX & VISUAL VERIFICATION GATE", content)
        self.assertIn("INDEPENDENT SUBAGENT SIGN-OFF & DELIVERY", content)
        self.assertIn("NO_ROSTER_BYPASS", content)
        self.assertIn("NO_SELF_SIGNOFF", content)
        self.assertIn("NO_SCREENSHOT_NO_UI_DELIVERY", content)

    def test_03_installer_rule_lifecycle(self):
        """Test rule install (Triple-Lock), status check, and uninstall in a temporary project directory"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_rule_lifecycle_"))
        try:
            # Check not installed
            status = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertFalse(status["is_installed"])

            # Install (Triple-Lock)
            res = self.installer.install_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(res["success"])

            # Check primary rule and root entrypoint files
            status_after = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(status_after["is_installed"])
            self.assertIn("MULTI-AGENT ARCHITECTURE", status_after["content"])
            self.assertTrue((temp_dir / "AGENTS.md").exists())
            self.assertTrue((temp_dir / "GEMINI.md").exists())

            # Uninstall
            un_res = self.installer.uninstall_collaboration_rule(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertTrue(un_res["success"])

            # Check not installed and root files removed
            status_final = self.installer.check_rule_status(
                target_type="antigravity_project",
                project_path=str(temp_dir)
            )
            self.assertFalse(status_final["is_installed"])
            self.assertFalse((temp_dir / "AGENTS.md").exists())
            self.assertFalse((temp_dir / "GEMINI.md").exists())
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
            self.assertEqual(res.get("essential_count", 0), 6)
            self.assertIn("specialized-agents-orchestrator", res.get("installed_essential_agents", []))
            self.assertIn("engineering-multi-agent-systems-architect", res.get("installed_essential_agents", []))
            self.assertIn("engineering-prompt-engineer", res.get("installed_essential_agents", []))
            self.assertIn("engineering-code-reviewer", res.get("installed_essential_agents", []))
            self.assertIn("testing-test-automation-engineer", res.get("installed_essential_agents", []))
            self.assertIn("design-ui-finish-gate-reviewer", res.get("installed_essential_agents", []))

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
