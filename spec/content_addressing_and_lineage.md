# RIO Protocol Extension: Content Addressing and Lineage

**Version:** 1.0.0
**Status:** Extension Specification
**Category:** Advanced Infrastructure

---

## 1. Purpose

This extension defines how documents, models, prompts, outputs, datasets, and other digital artifacts can be content-addressed (identified by their cryptographic hash) and linked together to create verifiable provenance and lineage chains. The goal is to enable any party to answer the question: **"What inputs produced this output, and can I prove it?"**

In AI-governed systems, lineage is critical because the behavior of an AI agent depends on its model, its prompt, the data it was given, and the configuration it was operating under. If an AI agent requests a consequential action (e.g., a wire transfer), the governance system needs to know — and be able to prove — which model version, which prompt template, which input data, and which configuration produced that request. Content addressing and lineage provide this traceability.

This is a protocol extension. It does not modify the core 15-protocol stack. Implementations MAY adopt this extension to strengthen auditability and reproducibility of AI-driven actions.

---

## 2. Scope

This specification covers:

- Content addressing: computing deterministic, collision-resistant identifiers for digital artifacts.
- Lineage records: structured records that link an output artifact to its input artifacts.
- Lineage chains: sequences of lineage records that trace an artifact back to its original sources.
- Integration with the RIO Protocol's canonical request and attestation stages.
- Verification procedures for lineage claims.

This specification does not cover:

- Storage or retrieval of the artifacts themselves (only their hashes and metadata).
- Version control systems or artifact repositories.
- Model training pipelines or dataset management.

---

## 3. Terminology

| Term | Definition |
|------|-----------|
| **Artifact** | Any digital object that can be hashed: a document, a model file, a prompt template, a dataset, a configuration file, an AI-generated output, or a code module. |
| **Content Address** | A deterministic identifier derived from the cryptographic hash of an artifact's content. Two artifacts with identical content produce identical content addresses. |
| **Lineage Record** | A structured record asserting that a specific output artifact was produced from specific input artifacts by a specific process. |
| **Lineage Chain** | A directed acyclic graph (DAG) of lineage records, tracing an artifact's provenance back through its inputs, their inputs, and so on. |
| **Provenance** | The complete history of an artifact's origin and transformations. |
| **Content Identifier (CID)** | The canonical content address format used in this specification, consisting of a hash algorithm prefix and the hex-encoded hash value. |

---

## 4. Content Addressing

### 4.1 Content Identifier Format

Every artifact in the RIO lineage system is identified by a Content Identifier (CID). The CID is computed deterministically from the artifact's content.

**Format:**

```
rio-cid:<hash_algorithm>:<hex_encoded_hash>
```

**Example:**

```
rio-cid:sha256:a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4
```

### 4.2 Hash Computation

The content address MUST be computed as follows:

1. **Canonicalize** the artifact content:
   - For JSON artifacts: minified, sorted-key JSON (consistent with RIO Protocol canonicalization).
   - For binary artifacts (models, images, compiled code): raw bytes.
   - For text artifacts (prompts, documents, configuration): UTF-8 encoded bytes with normalized line endings (LF).
2. **Hash** the canonicalized content using SHA-256.
3. **Encode** the hash as lowercase hexadecimal.
4. **Prefix** with `rio-cid:sha256:`.

### 4.3 Content Address Properties

| Property | Guarantee |
|----------|-----------|
| **Deterministic** | The same content always produces the same CID. |
| **Collision-resistant** | It is computationally infeasible to find two different artifacts with the same CID. |
| **Tamper-evident** | Any modification to the artifact changes the CID. |
| **Content-independent of location** | The CID does not depend on where the artifact is stored. |

### 4.4 Supported Artifact Types

| Artifact Type | Canonicalization | Use Case |
|--------------|-----------------|----------|
| `model` | Binary (raw bytes) | AI/ML model files (weights, checkpoints) |
| `prompt_template` | Text (UTF-8, LF normalized) | Prompt templates used by AI agents |
| `prompt_instance` | Text (UTF-8, LF normalized) | Specific prompt with variables filled in |
| `dataset` | Binary or JSON (depending on format) | Training data, reference data, input data |
| `configuration` | JSON (canonicalized) | System configuration, agent configuration |
| `document` | Binary (raw bytes) | PDFs, images, contracts, reports |
| `code_module` | Text (UTF-8, LF normalized) | Source code, scripts, compiled binaries |
| `ai_output` | Text or JSON (depending on format) | AI-generated text, structured output, decisions |
| `schema` | JSON (canonicalized) | JSON schemas, data models |
| `policy` | JSON (canonicalized) | Policy rules, constraints |

---

## 5. Artifact Metadata Record

Every content-addressed artifact SHOULD have an associated metadata record that describes the artifact without containing the artifact's content.

### 5.1 Metadata Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cid` | string | Yes | Content Identifier of the artifact |
| `artifact_type` | string | Yes | Type of artifact (from Section 4.4) |
| `name` | string | Yes | Human-readable name or label |
| `version` | string | No | Version identifier (semantic version, commit hash, etc.) |
| `size_bytes` | integer | Yes | Size of the artifact in bytes |
| `media_type` | string | Yes | MIME type of the artifact |
| `created_at` | string (ISO 8601) | Yes | When the artifact was created or registered |
| `created_by` | string (DID or URI) | Yes | Identity of the creator or registrar |
| `description` | string | No | Human-readable description |
| `tags` | array of strings | No | Classification tags |
| `storage_uri` | string | No | URI where the artifact can be retrieved (not part of the CID) |
| `signature` | string (base64) | Yes | Creator's signature over the metadata record |

### 5.2 Example: Model Artifact Metadata

```json
{
  "cid": "rio-cid:sha256:a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4",
  "artifact_type": "model",
  "name": "procurement-agent-v2.3.1",
  "version": "2.3.1",
  "size_bytes": 4831920128,
  "media_type": "application/octet-stream",
  "created_at": "2026-03-01T10:00:00Z",
  "created_by": "did:web:ml-ops.example.com",
  "description": "Procurement agent model trained on Q4 2025 data, fine-tuned for vendor payment workflows",
  "tags": ["procurement", "payment", "production"],
  "storage_uri": "s3://models.example.com/procurement-agent/v2.3.1/model.bin",
  "signature": "MEUCIQD7x8f9..."
}
```

### 5.3 Example: Prompt Template Metadata

```json
{
  "cid": "rio-cid:sha256:b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
  "artifact_type": "prompt_template",
  "name": "payment-request-prompt-v1.4",
  "version": "1.4",
  "size_bytes": 2847,
  "media_type": "text/plain",
  "created_at": "2026-03-15T08:00:00Z",
  "created_by": "did:web:prompt-eng.example.com",
  "description": "System prompt for procurement agent payment request generation",
  "tags": ["procurement", "payment", "system-prompt"],
  "signature": "MEQCIGh5j6k7..."
}
```

---

## 6. Lineage Record

### 6.1 Purpose

A lineage record asserts that a specific output artifact was produced from specific input artifacts by a specific process. It is the fundamental unit of provenance in the RIO lineage system.

### 6.2 Lineage Record Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lineage_id` | string (UUID v4) | Yes | Unique identifier for this lineage record |
| `output_cid` | string | Yes | Content Identifier of the output artifact |
| `output_type` | string | Yes | Artifact type of the output |
| `inputs` | array of objects | Yes | List of input artifacts with their CIDs and roles |
| `process` | object | Yes | Description of the process that produced the output |
| `created_at` | string (ISO 8601) | Yes | When this lineage record was created |
| `created_by` | string (DID or URI) | Yes | Identity of the entity asserting this lineage |
| `signature` | string (base64) | Yes | Creator's signature over the lineage record |
| `canonical_hash` | string (hex) | Yes | SHA-256 hash of the canonicalized lineage record |

### 6.3 Input Reference Structure

Each entry in the `inputs` array describes one input artifact and its role in producing the output:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cid` | string | Yes | Content Identifier of the input artifact |
| `artifact_type` | string | Yes | Type of the input artifact |
| `role` | string | Yes | The role this input played in producing the output |
| `name` | string | No | Human-readable name of the input |

**Standard input roles:**

| Role | Description |
|------|-------------|
| `model` | The AI/ML model that generated the output |
| `system_prompt` | The system prompt that configured the model's behavior |
| `user_prompt` | The user-facing prompt or query |
| `context_data` | Reference data provided as context to the model |
| `configuration` | System or agent configuration |
| `schema` | Output schema or format specification |
| `policy` | Policy rules that constrained the output |
| `prior_output` | A previous output used as input (chaining) |
| `training_data` | Dataset used to train or fine-tune the model |
| `tool_output` | Output from a tool invocation used as input |

### 6.4 Process Description

The `process` field describes how the inputs were combined to produce the output:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `process_type` | string | Yes | Category of process (see below) |
| `process_id` | string | No | Identifier for the specific process instance |
| `executor` | string (DID or URI) | Yes | Identity of the system that executed the process |
| `parameters` | object | No | Process parameters (e.g., temperature, max_tokens for LLM inference) |
| `started_at` | string (ISO 8601) | No | When the process started |
| `completed_at` | string (ISO 8601) | No | When the process completed |

**Standard process types:**

| Process Type | Description |
|-------------|-------------|
| `llm_inference` | Large language model inference (text generation) |
| `llm_structured_output` | LLM inference with structured output (JSON, function calls) |
| `model_training` | Model training or fine-tuning |
| `data_transformation` | Data processing, filtering, or transformation |
| `code_execution` | Code execution producing an output |
| `human_authoring` | Human-created content |
| `aggregation` | Combining multiple inputs into a single output |
| `template_instantiation` | Filling variables in a template |

### 6.5 Example: AI Agent Payment Request Lineage

This example shows the lineage of a canonical request generated by an AI procurement agent:

```json
{
  "lineage_id": "lin-a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
  "output_cid": "rio-cid:sha256:c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "output_type": "ai_output",
  "inputs": [
    {
      "cid": "rio-cid:sha256:a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4",
      "artifact_type": "model",
      "role": "model",
      "name": "procurement-agent-v2.3.1"
    },
    {
      "cid": "rio-cid:sha256:b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
      "artifact_type": "prompt_template",
      "role": "system_prompt",
      "name": "payment-request-prompt-v1.4"
    },
    {
      "cid": "rio-cid:sha256:d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
      "artifact_type": "prompt_instance",
      "role": "user_prompt",
      "name": "Invoice INV-2026-0847 payment request"
    },
    {
      "cid": "rio-cid:sha256:e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
      "artifact_type": "dataset",
      "role": "context_data",
      "name": "Vendor master record: Meridian Industrial Supply LLC"
    },
    {
      "cid": "rio-cid:sha256:f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
      "artifact_type": "configuration",
      "role": "configuration",
      "name": "procurement-agent-config-prod-v3"
    }
  ],
  "process": {
    "process_type": "llm_structured_output",
    "process_id": "proc-f1a2b3c4",
    "executor": "did:web:ai-platform.example.com",
    "parameters": {
      "temperature": 0.0,
      "max_tokens": 2048,
      "response_format": "canonical_request_json"
    },
    "started_at": "2026-03-24T14:30:00Z",
    "completed_at": "2026-03-24T14:30:03Z"
  },
  "created_at": "2026-03-24T14:30:03Z",
  "created_by": "did:web:ai-platform.example.com",
  "signature": "MEUCIQD7x8f9...",
  "canonical_hash": "a9b0c1d2e3f4..."
}
```

---

## 7. Lineage Chain

### 7.1 Structure

A lineage chain is a directed acyclic graph (DAG) where:

- Each node is an artifact (identified by its CID).
- Each edge is a lineage record (asserting that an output was produced from inputs).
- The graph has no cycles (an artifact cannot be an input to its own production).

### 7.2 Chain Traversal

To trace the full provenance of an artifact, a verifier traverses the lineage chain by:

1. Start with the target artifact's CID.
2. Find all lineage records where `output_cid` matches the target CID.
3. For each input in those lineage records, recursively find lineage records for the input's CID.
4. Continue until reaching artifacts with no further lineage records (root artifacts — typically human-authored content, original datasets, or base models).

### 7.3 Chain Depth

Implementations SHOULD support a configurable maximum chain depth for traversal (default: 10 levels). This prevents unbounded traversal in deeply nested lineage chains.

### 7.4 Visualization

A lineage chain for the payment request example might look like:

```
[training_data_v4]──┐
                     ├──[model v2.3.1]──┐
[training_data_v3]──┘                   │
                                        │
[prompt_template v1.4]─────────────────├──[AI Output: canonical_request]──[RIO Decision Chain]
                                        │
[invoice INV-2026-0847]────────────────┤
                                        │
[vendor_master_record]─────────────────┤
                                        │
[agent_config_prod_v3]─────────────────┘
```

---

## 8. Integration with RIO Protocol

### 8.1 Canonical Request Lineage

When an AI agent submits a canonical request to the RIO Protocol, the request SHOULD include a `lineage_reference` field in its metadata:

```json
{
  "canonical_request": {
    "request_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
    "requester_id": "did:web:procurement-agent.example.com",
    "action_type": "transact.send_payment.wire.domestic",
    "metadata": {
      "lineage_reference": {
        "output_cid": "rio-cid:sha256:c5d6e7f8...",
        "lineage_id": "lin-a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8"
      }
    }
  }
}
```

This allows the risk evaluation engine and the authorizer to inspect the lineage of the request — understanding which model, prompt, and data produced it.

### 8.2 Risk Evaluation Integration

The risk evaluation engine (Protocol 04) MAY use lineage information as a risk factor:

| Lineage Condition | Risk Impact |
|-------------------|-------------|
| No lineage record provided | Risk increase (unknown provenance) |
| Model version is not in the approved model registry | Risk increase (unapproved model) |
| Prompt template has been modified since last audit | Risk increase (unreviewed prompt) |
| Input data is stale (older than threshold) | Risk increase (stale context) |
| Configuration differs from production baseline | Risk increase (non-standard configuration) |
| All inputs are approved and current | Risk decrease (verified provenance) |

### 8.3 Attestation Integration

The attestation record (Protocol 08) MAY include lineage hashes in its verification:

```json
{
  "attestation_record": {
    "verification_checks": [
      {
        "check": "request_lineage_verified",
        "result": "pass",
        "details": {
          "lineage_id": "lin-a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
          "model_cid_verified": true,
          "prompt_cid_verified": true,
          "config_cid_verified": true,
          "chain_depth": 2,
          "all_inputs_registered": true
        }
      }
    ]
  }
}
```

### 8.4 Receipt and Ledger Integration

The receipt and ledger entry MAY include the lineage reference, creating a permanent record that links the governed action to the specific artifacts that produced the request:

```json
{
  "receipt": {
    "lineage_summary": {
      "model": "procurement-agent-v2.3.1 (rio-cid:sha256:a3b4c5d6...)",
      "prompt": "payment-request-prompt-v1.4 (rio-cid:sha256:b4c5d6e7...)",
      "lineage_chain_verified": true,
      "lineage_chain_depth": 2
    }
  }
}
```

---

## 9. Lineage Verification

### 9.1 Verification Procedure

To verify a lineage claim, a verifier MUST perform the following checks:

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 1 | Lineage record structure valid | All required fields present | Reject lineage claim |
| 2 | Output CID valid | Recomputed hash of the output artifact matches `output_cid` | Reject lineage claim |
| 3 | All input CIDs valid | Recomputed hash of each input artifact matches its stated CID | Reject lineage claim |
| 4 | Lineage record signature valid | `signature` verifies against the creator's public key | Reject lineage claim |
| 5 | Lineage record hash valid | Recomputed canonical hash matches `canonical_hash` | Reject lineage claim |
| 6 | No cycles | The lineage chain forms a DAG (no artifact is an input to its own production) | Reject lineage claim |
| 7 | Process plausible | The stated process type is consistent with the input and output artifact types | Flag as suspicious |

### 9.2 Limitations

Lineage verification proves that:
- The output artifact has the stated content (via CID).
- The input artifacts have the stated content (via CIDs).
- The lineage creator signed the assertion that these inputs produced this output.

Lineage verification does NOT prove that:
- The stated process was actually used (the creator could lie about the process).
- No other inputs were used (the creator could omit inputs).
- The output is correct or desirable (lineage is about provenance, not quality).

For stronger guarantees, lineage records SHOULD be produced by trusted execution environments or attested by independent observers.

---

## 10. Artifact Registry

### 10.1 Purpose

An artifact registry is an optional component that maintains a catalog of known, approved artifacts and their metadata. It enables policy rules like "only approved models may generate canonical requests" and "only reviewed prompt templates may be used in production."

### 10.2 Registry Structure

| Field | Type | Description |
|-------|------|-------------|
| `cid` | string | Content Identifier of the artifact |
| `artifact_type` | string | Type of artifact |
| `name` | string | Human-readable name |
| `version` | string | Version identifier |
| `status` | string | `approved`, `pending_review`, `deprecated`, `revoked` |
| `approved_by` | string (DID) | Identity of the approver |
| `approved_at` | string (ISO 8601) | When the artifact was approved |
| `approval_ledger_entry` | string | Ledger entry ID for the approval decision |
| `expiration` | string (ISO 8601) | When the approval expires |

### 10.3 Registry Governance

Changes to the artifact registry (approving, deprecating, or revoking artifacts) MUST be processed through the RIO Protocol. Approving a new model for production use is itself a governed action that requires authorization and produces a ledger entry.

---

## 11. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Lineage forgery | Lineage records are cryptographically signed. Verification requires signature validation. |
| Input omission | Lineage verification cannot detect omitted inputs. Trusted execution environments or independent attestation provide stronger guarantees. |
| Model substitution | The artifact registry and CID verification ensure that only approved, hash-verified models are used. |
| Prompt injection via lineage | Lineage records describe provenance, not content safety. Prompt content must be reviewed independently. |
| Hash collision | SHA-256 provides 128-bit collision resistance, which is sufficient for current threat models. |
| Storage of large artifacts | This specification addresses hashes and metadata only. Artifact storage is out of scope. |

---

## 12. Dependencies

| Document | Relationship |
|----------|-------------|
| Canonical Request Protocol (03) | Canonical requests may include lineage references |
| Risk Evaluation Protocol (04) | Lineage information is a risk input |
| Attestation Protocol (08) | Attestation may verify lineage claims |
| Audit Ledger Protocol (09) | Lineage references are recorded in ledger entries |
| Meta-Governance Protocol (13) | Artifact registry changes are governed by meta-governance |
| Identity and Credentials Extension | DID-based identity for artifact creators and lineage asserters |
