# RIO Repository License Matrix

> Last updated: 2026-05-10
> Maintainer: Brian Rasmussen

This matrix documents the license posture for every repository in the bkr1297-RIO organization. It is the single source of truth for what others may and may not use.

---

## License Matrix

| Repo | Visibility | License | Use Permission Summary | Canonical Role | Current Status | Notes / Cleanup Needed |
|------|-----------|---------|----------------------|---------------|---------------|----------------------|
| `rio-protocol` | Public | All Rights Reserved (Apache 2.0 pending) | No use without written permission; will become Apache 2.0 in future release | Canonical protocol spec | Active | License is intentionally restrictive until formal release |
| `rio-receipt-protocol` | Public | MIT | Free use under MIT terms | Proof primitive / receipt engine | Active | Root LICENSE file added via PR (was missing) |
| `rio-system` | Public | MIT | Free use under MIT terms | Observation / MANTIS layer | Active | Clean |
| `language-intake-mvp` | Public | None (no root LICENSE) | Unclear — no explicit license grant | Language governance prototype | Active | Needs root LICENSE file (recommend MIT) |
| `one-consent` | Public | None (no root LICENSE) | Unclear — no explicit license grant | SMS consent utility | Active | Needs license decision |
| `sovereignty-stack-demo` | Public | None (no root LICENSE) | Unclear — no explicit license grant | Demo | Legacy | Needs license decision or archive |
| `rio-legacy-protocol` | Public | Unknown | Unclear | Legacy receipt protocol | Superseded | Superseded by rio-receipt-protocol; recommend archive notice |
| `rio-hash-interlock-hash-system` | Public | Unknown | Unclear | Legacy interlock | Superseded | Superseded by rio-protocol; recommend archive notice |
| `RIO-Interlock-System` | Public | Unknown | Unclear | Legacy interlock spec | Superseded | Concepts absorbed into rio-protocol; recommend archive notice |
| `AI-Structural-Limitations-of-the-dyad` | Public | Unknown | Unclear | Research position paper | Active | Standalone research; may need license clarification |
| `rio-interlock` | Public | Unknown | Unclear | Legacy interlock | Superseded | Superseded by rio-protocol; recommend archive notice |
| `rio-proxy` | Private | Proprietary | No external use | Governed execution runtime | Active | N/A |
| `rio-proxy-manus` | Private | Proprietary | No external use | Manus mirror (not canonical) | Active | N/A |
| `rio-reference-impl` | Private | Proprietary | No external use | Reference implementation | Active | N/A |
| `rio-tools` | Private | Proprietary | No external use | Developer tooling | Active | N/A |
| `rio-programs` | Private | Proprietary | No external use | Coordination layer | Active | N/A |
| `rio-protocol-v1` | Private | Proprietary | No external use | Legacy private protocol | Superseded | Superseded by public rio-protocol |
| `rio-demo-site` | Private | Proprietary | No external use | Internal demo | Active | N/A |
| `email-compliance-wrapper` | Private | Proprietary | No external use | Email utility | Active | N/A |

---

## Key Principles

1. **Public does not mean open-source.** A public repository without a LICENSE file grants no usage rights under copyright law.
2. **`rio-protocol` is intentionally All Rights Reserved** until Brian decides to release under Apache 2.0.
3. **MIT repos** (`rio-receipt-protocol`, `rio-system`) are genuinely open — anyone may use, modify, and distribute under MIT terms.
4. **Private repos are proprietary.** No external use, no external access.
5. **Legacy repos** should be evaluated for archiving or notice addition to prevent confusion.

---

## Cleanup Actions Needed

| Repo | Action | Priority |
|------|--------|----------|
| `rio-receipt-protocol` | Add root MIT LICENSE file | High — PR A in progress |
| `language-intake-mvp` | Add root LICENSE file (recommend MIT) | Medium |
| `one-consent` | Decide license posture | Low |
| `sovereignty-stack-demo` | Decide: archive or add legacy notice | Low |
| `rio-legacy-protocol` | Add "superseded" notice to README | Medium |
| `rio-hash-interlock-hash-system` | Add "superseded" notice or archive | Low |
| `RIO-Interlock-System` | Add "superseded" notice or archive | Low |
| `rio-interlock` | Add "superseded" notice or archive | Low |
| `AI-Structural-Limitations-of-the-dyad` | Clarify license (standalone research) | Low |
