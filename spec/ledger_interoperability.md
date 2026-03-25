# RIO Protocol — Ledger Interoperability Specification

## 1. Overview

The RIO Protocol ledger is a tamper-evident, append-only hash-chain that records every decision and action governed by the protocol. This specification defines the mechanisms by which external systems can verify the integrity of the ledger, prove the inclusion and consistency of records, and integrate with the RIO Protocol for enhanced auditability and interoperability.

This document is intended for developers, auditors, and system integrators who need to build tools, processes, or independent verification systems that interact with the RIO ledger. Adherence to this specification ensures that all parties can trust the immutability and accuracy of the recorded information.

## 2. Ledger Entry Structure

Each entry in the RIO ledger is a structured JSON object containing the following fields. The canonicalization of this entry (excluding `entry_hash` and `previous_hash`) is used to compute the entry's hash.

| Field             | Type   | Description                                                                                             |
| ----------------- | ------ | ------------------------------------------------------------------------------------------------------- |
| `entry_id`        | String | A unique identifier for the ledger entry (e.g., a UUID).                                                |
| `sequence_number` | Integer| A monotonically increasing integer, starting from 1, indicating the entry's position in the chain.       |
| `previous_hash`   | String | The SHA-256 hash of the preceding ledger entry. For the first entry, this SHALL be a zero-filled string. |
| `entry_hash`      | String | The SHA-256 hash of the current entry, computed as described in Section 3.                              |
| `entry_type`      | String | The type of record being recorded (e.g., `authorization_record`, `execution_record`).                   |
| `record_id`       | String | The unique identifier of the underlying RIO record being referenced.                                    |
| `record_hash`     | String | The SHA-256 hash of the canonicalized RIO record.                                                       |
| `recorded_at`     | String | The ISO 8601 timestamp indicating when the entry was recorded.                                          |
| `recorded_by`     | String | The identifier of the system or agent that recorded the entry.                                          |

Below is an example of a ledger entry in JSON format:

```json
{
  "entry_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "sequence_number": 123,
  "previous_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "entry_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
  "entry_type": "authorization_record",
  "record_id": "c4a1b2c3-d4e5-f6a1-b2c3-d4e5f6a1b2c3",
  "record_hash": "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3",
  "recorded_at": "2023-10-27T10:00:00Z",
  "recorded_by": "rio-system-abcde"
}
```

## 3. Hash Chain Verification

The integrity of the RIO ledger is maintained through a chain of cryptographic hashes. Each entry is linked to the previous one, forming an unbroken sequence. Verification ensures that no entry has been altered or inserted out of order.

### Full-Chain Verification

Full-chain verification MUST be performed by iterating through the entire ledger from the first entry to the last. For each entry `E_n` (where `n` is the `sequence_number`):

1.  The `previous_hash` of `E_n` MUST match the `entry_hash` of the preceding entry, `E_{n-1}`.
2.  The `entry_hash` of `E_n` MUST be equal to `SHA-256(E_{n-1}.entry_hash + canonicalize(E_n.body))`, where `E_n.body` is the minified, sorted JSON representation of the entry, excluding the `entry_hash` field itself.

### Partial-Chain Verification

Partial-chain verification MAY be used to verify a segment of the ledger. This requires a trusted entry (a "checkpoint") from which to start the verification process. The same iterative hashing process is applied from the checkpoint to the desired entry.

## 4. Inclusion Proofs

To prove that a specific record (e.g., an `authorization_record`) is included in the ledger, a system MUST provide the following:

1.  The full ledger entry (`E_n`) corresponding to the record.
2.  The `sequence_number` of the entry.
3.  The hash chain path from `E_n` to the current head of the ledger. This consists of the sequence of `entry_hash` values from `E_{n+1}` to the final entry.

An external verifier can then use this information to perform a partial-chain verification from the provided entry to the chain head, confirming the record's inclusion.

## 5. Consistency Proofs

A consistency proof demonstrates that a newer version of the ledger is a valid continuation of an older version. Given two ledger chain heads, `H_1` at time `t_1` and `H_2` at time `t_2` (where `t_2 > t_1`), the proof is constructed by demonstrating that the ledger at `t_1` is a prefix of the ledger at `t_2`. This is achieved by recomputing the hash chain from the entry corresponding to `H_1` up to the entry corresponding to `H_2`.

## 6. External Anchoring

To provide stronger, publicly verifiable proof of the ledger's integrity and existence at a certain point in time, the RIO ledger supports optional anchoring to external timestamping services. This process does not depend on a specific implementation.

*   **Periodic Hash Publication**: The hash of the latest ledger entry MAY be periodically published to a trusted third-party service (e.g., a public notary or a dedicated timestamping authority).
*   **Blockchain Anchoring**: For higher security, the ledger hash MAY be embedded into a transaction on a public blockchain (e.g., Bitcoin, Ethereum). This provides decentralized, immutable timestamping.
*   **RFC 3161 Timestamping**: The ledger hash MAY be sent to a Time-Stamp Authority (TSA) compliant with RFC 3161 to obtain a trusted timestamp token.

## 7. Export Formats

The RIO ledger SHALL support export in the following standard formats to ensure broad compatibility:

*   **JSON Lines**: Each line is a complete JSON object representing a single ledger entry. This format is ideal for stream processing.
*   **CSV**: A comma-separated values format where each row represents a ledger entry. The first row MUST be a header defining the fields.
*   **Binary Compact Format**: A custom, space-efficient binary format MAY be defined for performance-critical applications. The specification for this format is outside the scope of this document.

## 8. Cross-System Integration

RIO ledger entries are designed for easy ingestion into various external systems for monitoring, compliance, and analysis.

*   **SIEM Systems**: Ledger entries in JSON Lines format can be streamed into Security Information and Event Management (SIEM) systems like Splunk or Elastic Stack. This allows for real-time monitoring and alerting on critical RIO events.
*   **Compliance Platforms**: Exported ledgers can be imported into compliance and GRC (Governance, Risk, and Compliance) platforms to automate audit evidence collection.
*   **External Audit Tools**: Auditors can use the verification algorithms defined in this specification to independently validate the integrity of the ledger.

## 9. Retention and Archival

Clear policies MUST be established for ledger retention and archival to ensure long-term auditability while managing storage costs.

*   **Retention Policies**: The active ledger SHOULD be retained online for a defined period (e.g., 12 months). The retention period MUST comply with relevant legal and regulatory requirements.
*   **Archival Procedures**: After the retention period, the ledger SHOULD be archived to a secure, long-term storage medium. The archival process MUST ensure chain continuity by linking the last entry of the archived ledger to the first entry of the new one.

## 10. Security Considerations

*   **Tamper Detection**: The primary security feature of the hash chain is tamper detection. Any modification to a past entry will invalidate the entire chain from that point forward. Regular verification (see Section 3) is critical.
*   **Split-Brain Prevention**: In a distributed deployment, measures MUST be taken to prevent a "split-brain" scenario where multiple, conflicting versions of the ledger could be created. A consensus mechanism or a single, authoritative ledger service SHOULD be used.
*   **Recovery Procedures**: In the event of data corruption, a recovery procedure MUST be initiated from the last known valid backup. The ledger SHOULD be re-validated against any available external anchors to ensure it is restored to a correct state.

This specification provides a framework for ensuring the integrity and interoperability of the RIO Protocol ledger. By adhering to these guidelines, developers and auditors can build and verify systems that meet the highest standards of trust and accountability.

Further details on the canonicalization algorithm and the specific record types can be found in the RIO Protocol Core Specification.
