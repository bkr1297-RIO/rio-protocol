# RUN-RECEIPT-004: Canonical RIO Verify Runner

**Status:** Candidate run receipt  
**Runtime surface:** Replit execution environment using fresh clone in scratch directory  
**Repository:** `bkr1297-RIO/rio-protocol`  
**Verified commit:** `a927df2ea21d5df2879cb573d7cafe648e6a22ea`  
**Short SHA:** `a927df2`  
**Command:** `bash scripts/rio_verify.sh`  
**Exit code:** `0`  
**Result:** Canonical RIO verification runner passed in Replit runtime  

---

## Scope

This run verifies the canonical `scripts/rio_verify.sh` runner, which currently runs:

1. Scribe-Compiler Capsule fixture validation
2. Four-Bit Crossing Code truth-table validation
3. Four-Bit Crossing Code harness-negative validation
4. Gate Evidence v0.1 validation
5. Receipt Binding v0.1 validation

This run does **not** claim live conformance, production enforcement, receipt-protocol verification, deployment, production readiness, or certification.

---

## Environment Note

The Replit workspace local repository was not connected to `bkr1297-RIO/rio-protocol`.

To execute the verification, the repository was cloned fresh into a scratch directory:

```text
/tmp/verify/rio-protocol
```

Because the fresh clone already landed on `main`, `git checkout main` was not executed; the sandbox guardrail blocked that command, and it would have been a no-op. `git status` confirmed the repository was on `main`, and `git pull origin main` was executed and returned already up to date.

---

## Command Results

### 1. `git status`

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

### 2. `git checkout main`

```text
Not run. Blocked by sandbox guardrail. Not required because clone already landed on main.
```

### 3. `git pull origin main`

```text
From https://github.com/bkr1297-RIO/rio-protocol
 * branch            main       -> FETCH_HEAD
Already up to date.
```

### 4. `bash scripts/rio_verify.sh`

```text
RIO verification run
Repository: rio-protocol
Branch: main
Commit: a927df2
Full commit: a927df2ea21d5df2879cb573d7cafe648e6a22ea
Started at UTC: 2026-07-03T07:19:42Z
Scribe-Compiler Capsule fixture validation passed: 2 fixtures
Four-Bit Crossing Code validation passed: 16 truth-table rows
Four-Bit Crossing Code harness-negative validation passed: 5 malformed datasets rejected
Gate Evidence validation passed: 4 fixtures
Receipt Binding validation passed: 5 fixtures
RIO verification complete
Finished at UTC: 2026-07-03T07:19:44Z
Exit code: 0
Receipt-ready summary:
- repository: rio-protocol
- branch: main
- verified_commit: a927df2ea21d5df2879cb573d7cafe648e6a22ea
- short_sha: a927df2
- command: bash scripts/rio_verify.sh
- result: PASS
- boundary: candidate packet grammar, Gate Evidence, and Receipt Binding validators only; no live conformance, production enforcement, deployment, readiness, or certification claimed
```

---

## Verdict

```text
Canonical RIO verification runner passed in Replit runtime. Candidate verification receipt available.
```

---

## Boundary

This receipt records a successful candidate verification run of `scripts/rio_verify.sh` at commit `a927df2ea21d5df2879cb573d7cafe648e6a22ea`.

It does not prove runtime enforcement, live conformance, receipt-protocol verification, deployment, production readiness, or certification.

---

## Keeper

Generate freely. Cross only by law. Return with proof.
