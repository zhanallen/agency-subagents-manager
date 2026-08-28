---
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
