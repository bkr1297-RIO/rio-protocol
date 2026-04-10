# RIO Repository Boundaries

> Established by consensus between Manny (Builder) and Bondi (Strategist), authorized by Brian (Sovereign Authority).

## Active Repositories

| Repository | Purpose | Lane Owner |
|---|---|---|
| `bkr1297-RIO/rio-system` | Running system. Gateway, API, deployment configs, `rio_monitor.py`, `GOVERNANCE.md`, all operational code. Deployed at rio-gateway.onrender.com. | Manny (Builder) commits on Brian's instruction |
| `bkr1297-RIO/rio-protocol` | Protocol specification. Reference architecture, conformance tests, SDK examples, JSON schemas, whitepaper. | Bondi (Strategist) may commit spec artifacts |
| Google Drive `/RIO/` | Shared corpus. Dashboards, courier logs, memos, architecture docs. Mobile-accessible backup that stays current because the workflow requires it. | Gemini (Librarian) organizes; all agents contribute |

## Key Rules

1. **No cross-lane modification without Brian's direction.** Manny does not commit to `rio-protocol` without instruction. Bondi does not commit to `rio-system` without instruction.

2. **Spec artifacts vs. runtime artifacts.** Files in `rio-protocol/config/` (e.g., `policies.json`, `policies.schema.json`) are specification artifacts. They describe what the system *should* enforce. Runtime wiring for `rio_monitor.py` belongs in `rio-system` and will be migrated there when the core loop is ready for dynamic config.

3. **Google Drive is the backup that is also the workflow.** Every handoff between agents creates an artifact in Drive. The backup stays current because the governance architecture forces every action through a path that creates records.

4. **GitHub is the source of truth for code.** Drive is the source of truth for context and memory. Neither replaces the other.

## Established Commits

- `rio-system` commit `2a041fd` — GOVERNANCE.md (Sandbox Invariant, Two-Gate Architecture, Role Assignments)
- `rio-system` commit `e845355` — rio_monitor.py (SHA-256 Mechanical Guard)
- `rio-protocol` commit `aecf0f7` — config/policies.schema.json (JSON Schema for policy validation)
- `rio-protocol` commit `ced7d1b` — config/policies.json (enforcement config specification)

---

*Governance is the floor, not the ceiling.*
