# Registers

Status: Candidate register directory rules. No live entries are created by this PR.

## Rule

The register is the only live-law read surface.

Drive documents, Chronicle entries, model outputs, memory, branch names, tags, and conversation text are not live-law read surfaces.

## MUSS / MUS separation

- MUSS is the sovereignty, consent, and human-boundary container.
- MUS is the receipt / ledger unit that records proof of crossings.

This directory supports register references and future receipt integration. It does not collapse MUSS into MUS.

## Infrastructure vectors

Native hooks and third-party providers may be named only as authorized infrastructure vectors inside a ratification or revocation entry.

No native hook or provider may be triggered by register narration alone.

No infrastructure vector is active merely because it appears in an example file.

Unlisted vectors fail closed.

Allowed vector families are currently:

- native OS hooks: OS_REMINDERS, LOCAL_CRON_SCHEDULER, FILE_SYSTEM_WATCHER, CLIPBOARD_AIR_GAP_BUFFER
- providers: GITHUB_REPOSITORIES, NOTION_WORKSPACE, TWILIO_SIGNALING, AZURE_RESOURCES, RENDER_CONTAINERS

A future runtime action involving any vector must still require an atomically bound MUS receipt or equivalent receipt-return path.

## Bootstrap boundary

During candidate PR review, this directory may include README files, schemas, examples, and fixtures.

It must not include live ratification entries until the target canonical artifact already exists at a merged commit.

## Future layout

```text
registers/
  ratifications.jsonl
  revocations.jsonl
  ratifications.example.jsonl
  revocations.example.jsonl
```

Example JSONL files are non-authoritative and illustrate shape only.

A live entry must reference repository, path, full commit SHA, SHA-256 content hash, tier granted, scope, non-claims, infrastructure vector bounds, signature block, and inference basis.

Invalid targets include `main`, `PENDING_MERGE`, branch names, mutable Drive-only references, Chronicle narrative, conversation text, nonexistent commits, and unlisted infrastructure vectors.

## Keeper

Git freezes the artifact. The register identifies live law. The receipt proves the crossing.
