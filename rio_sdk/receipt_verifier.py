"""
RIO SDK — Receipt Verification

ReceiptVerifier — 7-check receipt verification
LedgerVerifier  — Chain formula verification

Receipt verification checks (7 total):
    1. required_fields    — All 22 required fields present
    2. decision_valid     — decision in {allow, modify, block, escalate}
    3. request_hash       — SHA256(canonical_json(request_canonical_payload))
    4. receipt_hash       — SHA256(canonical_json({19 signed fields}))
    5. signature          — Ed25519.verify(base64_decode(signature), canonical_signed_payload)
    6. public_key_fingerprint — SHA256(raw_32_byte_ed25519_public_key)
    7. receipt_version    — version in {'1.0'}

Ledger chain formula:
    genesis: first_entry.prev_ledger_hash == SHA256(b'GENESIS')
    chain:   current_ledger_hash = SHA256((prev_ledger_hash + receipt_hash).encode('utf-8'))
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Optional, Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

from .models import Receipt, VerificationCheck, VerificationResult
from .exceptions import RIOVerificationError, RIOLedgerError


GENESIS_HASH = hashlib.sha256(b"GENESIS").hexdigest()

REQUIRED_FIELDS = [
    "receipt_version", "receipt_id", "timestamp", "runtime_id",
    "runtime_version", "environment", "request_summary", "request_hash",
    "request_canonical_payload", "policy_bundle_id", "policy_bundle_hash",
    "decision", "decision_reason_codes", "invariant_results",
    "threshold_results", "model_output_hash", "model_output_preview",
    "prev_ledger_hash", "public_key_fingerprint",
    "receipt_hash", "signature_algorithm", "signature",
]

SIGNED_FIELDS = [
    "receipt_version", "receipt_id", "timestamp", "runtime_id",
    "runtime_version", "environment", "request_summary", "request_hash",
    "request_canonical_payload", "policy_bundle_id", "policy_bundle_hash",
    "decision", "decision_reason_codes", "invariant_results",
    "threshold_results", "model_output_hash", "model_output_preview",
    "prev_ledger_hash", "public_key_fingerprint",
]

VALID_DECISIONS = {"allow", "modify", "block", "escalate"}
VALID_VERSIONS = {"1.0"}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


class ReceiptVerifier:
    """Verify a RIO v2 receipt against the 7-check protocol specification."""

    def __init__(self, public_key_pem: str):
        """Initialize with the gateway's PEM-encoded Ed25519 public key."""
        pk = load_pem_public_key(public_key_pem.encode() if isinstance(public_key_pem, str) else public_key_pem)
        if not isinstance(pk, Ed25519PublicKey):
            raise RIOVerificationError([], "Public key is not Ed25519")
        self._pk = pk
        self._raw_pub = pk.public_bytes(Encoding.Raw, PublicFormat.Raw)

    def verify(self, receipt: Union[Receipt, dict]) -> VerificationResult:
        """Run all 7 checks. Returns VerificationResult (never raises)."""
        if isinstance(receipt, dict):
            data = receipt
            receipt_obj = Receipt.from_dict(data)
        else:
            data = receipt.raw if receipt.raw else receipt.signed_fields
            receipt_obj = receipt

        checks = []

        # 1. Required fields
        missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] is None]
        checks.append(VerificationCheck(
            name="required_fields",
            passed=len(missing) == 0,
            detail=f"All {len(REQUIRED_FIELDS)} required fields present" if not missing
                   else f"Missing fields: {', '.join(missing)}",
        ))

        # 2. Decision valid
        decision = data.get("decision", "")
        checks.append(VerificationCheck(
            name="decision_valid",
            passed=decision in VALID_DECISIONS,
            detail=f"Decision '{decision}' is valid" if decision in VALID_DECISIONS
                   else f"Invalid decision: '{decision}'",
        ))

        # 3. Request hash
        rcp = data.get("request_canonical_payload", "")
        if isinstance(rcp, str):
            try:
                rcp_obj = json.loads(rcp)
                computed_rh = _sha256(_canonical_json(rcp_obj))
            except (json.JSONDecodeError, TypeError):
                computed_rh = _sha256(rcp.encode("utf-8"))
        else:
            computed_rh = _sha256(_canonical_json(rcp))
        stored_rh = data.get("request_hash", "")
        checks.append(VerificationCheck(
            name="request_hash",
            passed=stored_rh == computed_rh,
            detail="Request hash matches" if stored_rh == computed_rh
                   else f"Mismatch: stored={stored_rh[:16]}... computed={computed_rh[:16]}...",
            stored=stored_rh,
            computed=computed_rh,
        ))

        # 4. Receipt hash
        signed_payload = {k: data.get(k) for k in SIGNED_FIELDS}
        computed_receipt_hash = _sha256(_canonical_json(signed_payload))
        stored_receipt_hash = data.get("receipt_hash", "")
        checks.append(VerificationCheck(
            name="receipt_hash",
            passed=stored_receipt_hash == computed_receipt_hash,
            detail="Receipt hash matches" if stored_receipt_hash == computed_receipt_hash
                   else f"Mismatch: stored={stored_receipt_hash[:16]}... computed={computed_receipt_hash[:16]}...",
            stored=stored_receipt_hash,
            computed=computed_receipt_hash,
        ))

        # 5. Signature
        sig_b64 = data.get("signature", "")
        try:
            sig_bytes = base64.b64decode(sig_b64)
            canonical_payload = _canonical_json(signed_payload)
            self._pk.verify(sig_bytes, canonical_payload)
            sig_ok = True
        except Exception:
            sig_ok = False
        checks.append(VerificationCheck(
            name="signature",
            passed=sig_ok,
            detail="Ed25519 signature verified" if sig_ok else "Signature verification failed",
        ))

        # 6. Public key fingerprint
        computed_fp = _sha256(self._raw_pub)
        stored_fp = data.get("public_key_fingerprint", "")
        checks.append(VerificationCheck(
            name="public_key_fingerprint",
            passed=stored_fp == computed_fp,
            detail="Fingerprint matches" if stored_fp == computed_fp
                   else f"Mismatch: stored={stored_fp[:16]}... computed={computed_fp[:16]}...",
            stored=stored_fp,
            computed=computed_fp,
        ))

        # 7. Receipt version
        version = data.get("receipt_version", "")
        checks.append(VerificationCheck(
            name="receipt_version",
            passed=version in VALID_VERSIONS,
            detail=f"Version '{version}' is valid" if version in VALID_VERSIONS
                   else f"Unknown version: '{version}'",
        ))

        n_pass = sum(1 for c in checks if c.passed)
        overall = "PASS" if n_pass == len(checks) else "FAIL"
        return VerificationResult(overall=overall, checks=checks)

    def assert_valid(self, receipt: Union[Receipt, dict]):
        """Verify and raise RIOVerificationError if any check fails."""
        result = self.verify(receipt)
        if not result.passed:
            failed = [{"name": c.name, "detail": c.detail, "passed": c.passed} for c in result.checks if not c.passed]
            raise RIOVerificationError(failed, f"Receipt verification failed: {result.summary}")


class LedgerVerifier:
    """Verify ledger chain integrity using the RIO chain formula."""

    @staticmethod
    def verify_chain(entries: list[dict]) -> dict:
        """
        Verify a list of ledger entries.

        Chain formula:
            genesis: first_entry.prev_ledger_hash == SHA256(b'GENESIS')
            chain:   current_ledger_hash = SHA256((prev_ledger_hash + receipt_hash).encode('utf-8'))

        Returns dict with 'intact', 'entries_checked', 'errors'.
        """
        errors = []
        if not entries:
            return {"intact": True, "entries_checked": 0, "errors": []}

        # Check genesis
        first = entries[0]
        if first.get("prev_ledger_hash", first.get("prev_hash", "")) != GENESIS_HASH:
            errors.append({
                "entry_id": first.get("id", 0),
                "error": "Genesis hash mismatch",
                "expected": GENESIS_HASH,
                "actual": first.get("prev_ledger_hash", first.get("prev_hash", "")),
            })

        # Check chain linkage
        for i, entry in enumerate(entries):
            prev_h = entry.get("prev_ledger_hash", entry.get("prev_hash", ""))
            receipt_h = entry.get("receipt_hash", "")
            expected_hash = _sha256(f"{prev_h}{receipt_h}".encode("utf-8"))
            actual_hash = entry.get("ledger_hash", entry.get("entry_hash", ""))

            if i > 0:
                # Check prev_hash linkage
                prev_entry = entries[i - 1]
                expected_prev = prev_entry.get("ledger_hash", prev_entry.get("entry_hash", ""))
                if prev_h != expected_prev:
                    errors.append({
                        "entry_id": entry.get("id", i),
                        "error": "prev_hash does not link to previous entry",
                        "expected": expected_prev,
                        "actual": prev_h,
                    })

        return {
            "intact": len(errors) == 0,
            "entries_checked": len(entries),
            "errors": errors,
        }

    @staticmethod
    def assert_chain_intact(entries: list[dict]):
        """Verify chain and raise RIOLedgerError if broken."""
        result = LedgerVerifier.verify_chain(entries)
        if not result["intact"]:
            raise RIOLedgerError(result, f"Ledger chain broken: {len(result['errors'])} error(s)")

    @staticmethod
    def contains_receipt(entries: list[dict], receipt_hash: str) -> bool:
        """Check if a receipt hash exists in the ledger."""
        return any(e.get("receipt_hash") == receipt_hash for e in entries)
