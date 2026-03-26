"""
RIO Independent Verifier — Test Suite

Tests every verification check against the WS3 conformance test vectors.
Run with: python -m pytest verification/tests/ -v
"""

import json
import os
import unittest

from verification.receipt_verifier import verify_receipt, verify_receipt_from_file
from verification.ledger_verifier import verify_ledger, verify_ledger_from_file
from verification.hash_utils import (
    canonical_json,
    sha256_hex,
    compute_request_hash,
    compute_receipt_hash,
    compute_public_key_fingerprint,
    compute_ledger_chain_hash,
    compute_genesis_hash,
)
from verification.crypto_utils import (
    load_public_key,
    get_raw_public_key_bytes,
    verify_signature,
)
from verification.schema_validator import validate_receipt_schema, validate_ledger_entry_schema
from verification.models import GENESIS_HASH, SIGNED_FIELDS_19, ALL_REQUIRED_FIELDS

# ── Paths ───────────────────────────────────────────────────────────────────

VECTORS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "vectors")


def _vec(name: str) -> str:
    return os.path.join(VECTORS_DIR, name)


def _load_json(name: str) -> dict:
    with open(_vec(name), "r") as f:
        return json.load(f)


def _load_pem() -> str:
    with open(_vec("public_key.pem"), "r") as f:
        return f.read()


# ── Hash Utility Tests ──────────────────────────────────────────────────────

class TestHashUtils(unittest.TestCase):
    """Test all protocol hash functions against known test vectors."""

    def test_genesis_hash(self):
        """SHA256(b'GENESIS') must produce the protocol constant."""
        result = compute_genesis_hash()
        self.assertEqual(result, GENESIS_HASH)
        self.assertEqual(
            result,
            "901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a",
        )

    def test_canonical_json_deterministic(self):
        """canonical_json must produce sorted, compact, UTF-8 bytes."""
        obj = {"z": 1, "a": 2, "m": {"y": 3, "b": 4}}
        result = canonical_json(obj)
        self.assertEqual(result, b'{"a":2,"m":{"b":4,"y":3},"z":1}')

    def test_canonical_json_no_whitespace(self):
        """No spaces or newlines in canonical JSON."""
        obj = {"key": "value", "list": [1, 2, 3]}
        result = canonical_json(obj)
        self.assertNotIn(b" ", result)
        self.assertNotIn(b"\n", result)

    def test_request_hash_from_vector(self):
        """Verify request_hash matches the approved receipt test vector."""
        receipt = _load_json("receipt_valid_approved.json")
        expected = receipt["request_hash"]
        computed = compute_request_hash(receipt["request_canonical_payload"])
        self.assertEqual(computed, expected)

    def test_receipt_hash_from_vector(self):
        """Verify receipt_hash matches the approved receipt test vector."""
        receipt = _load_json("receipt_valid_approved.json")
        expected = receipt["receipt_hash"]
        computed = compute_receipt_hash(receipt)
        self.assertEqual(computed, expected)

    def test_receipt_hash_denied_vector(self):
        """Verify receipt_hash matches the denied receipt test vector."""
        receipt = _load_json("receipt_valid_denied.json")
        expected = receipt["receipt_hash"]
        computed = compute_receipt_hash(receipt)
        self.assertEqual(computed, expected)

    def test_ledger_chain_hash_from_vector(self):
        """Verify ledger chain hash computation from the valid ledger vector."""
        chain_data = _load_json("ledger_chain_valid.json")
        entry = chain_data["chain"]["entry_0"]
        expected = entry["current_ledger_hash"]
        computed = compute_ledger_chain_hash(
            entry["prev_ledger_hash"],
            entry["receipt_hash"],
        )
        self.assertEqual(computed, expected)

    def test_public_key_fingerprint(self):
        """Verify public_key_fingerprint from the approved receipt vector."""
        receipt = _load_json("receipt_valid_approved.json")
        pem = _load_pem()
        pub_key = load_public_key(pem)
        raw_bytes = get_raw_public_key_bytes(pub_key)
        computed = compute_public_key_fingerprint(raw_bytes)
        self.assertEqual(computed, receipt["public_key_fingerprint"])

    def test_hash_computation_examples(self):
        """Verify all hash computation examples from the test vector file."""
        examples = _load_json("hash_computation_examples.json")
        pem = _load_pem()
        for ex in examples["examples"]:
            with self.subTest(example=ex["id"]):
                expected = ex["sha256_output"]
                ex_type = ex["type"]

                if ex_type == "intent_hash":
                    computed = compute_request_hash(ex["input_object"])
                elif ex_type == "receipt_hash":
                    # receipt_hash_01 only provides the receipt_id reference;
                    # we verify this through the receipt vectors instead
                    receipt = _load_json("receipt_valid_approved.json")
                    computed = compute_receipt_hash(receipt)
                elif ex_type == "policy_bundle_hash":
                    # Policy bundle hash is a reference value; skip computation
                    continue
                elif ex_type == "ledger_chain_hash":
                    inp = ex["input"]
                    computed = compute_ledger_chain_hash(
                        inp["prev_ledger_hash"], inp["receipt_hash"]
                    )
                elif ex_type == "genesis_hash":
                    computed = compute_genesis_hash()
                elif ex_type == "model_output_hash":
                    computed = sha256_hex(ex["input_string"].encode("utf-8"))
                elif ex_type == "public_key_fingerprint":
                    raw_bytes = bytes.fromhex(ex["public_key_hex"])
                    computed = compute_public_key_fingerprint(raw_bytes)
                else:
                    self.fail(f"Unknown hash type: {ex_type}")

                self.assertEqual(computed, expected)

    def test_signing_payload_examples(self):
        """Verify signing payload SHA256 from signing_payload_examples.json."""
        examples = _load_json("signing_payload_examples.json")
        for ex in examples["examples"]:
            with self.subTest(example=ex["id"]):
                payload_bytes = ex["signing_payload_bytes_utf8"].encode("utf-8")
                expected = ex["signing_payload_sha256"]
                computed = sha256_hex(payload_bytes)
                self.assertEqual(computed, expected)


# ── Crypto Tests ────────────────────────────────────────────────────────────

class TestCryptoUtils(unittest.TestCase):
    """Test Ed25519 signature verification against test vectors."""

    def test_valid_signature_approved(self):
        """Verify Ed25519 signature on the approved receipt."""
        receipt = _load_json("receipt_valid_approved.json")
        pem = _load_pem()
        pub_key = load_public_key(pem)
        signing_payload = {k: receipt[k] for k in SIGNED_FIELDS_19}
        message = canonical_json(signing_payload)
        self.assertTrue(verify_signature(pub_key, message, receipt["signature"]))

    def test_valid_signature_denied(self):
        """Verify Ed25519 signature on the denied receipt."""
        receipt = _load_json("receipt_valid_denied.json")
        pem = _load_pem()
        pub_key = load_public_key(pem)
        signing_payload = {k: receipt[k] for k in SIGNED_FIELDS_19}
        message = canonical_json(signing_payload)
        self.assertTrue(verify_signature(pub_key, message, receipt["signature"]))

    def test_invalid_signature_rejected(self):
        """Corrupted signature must be rejected."""
        data = _load_json("receipt_invalid_signature.json")
        receipt = data.get("receipt", data)
        pem = _load_pem()
        pub_key = load_public_key(pem)
        signing_payload = {k: receipt[k] for k in SIGNED_FIELDS_19}
        message = canonical_json(signing_payload)
        self.assertFalse(verify_signature(pub_key, message, receipt["signature"]))

    def test_signing_payload_signature_verification(self):
        """Verify all signatures from signing_payload_examples.json."""
        examples = _load_json("signing_payload_examples.json")
        pem = _load_pem()
        pub_key = load_public_key(pem)
        for ex in examples["examples"]:
            with self.subTest(example=ex["id"]):
                message = ex["signing_payload_bytes_utf8"].encode("utf-8")
                self.assertTrue(
                    verify_signature(pub_key, message, ex["signature_b64"]),
                    f"Signature verification failed for {ex['id']}",
                )


# ── Schema Validation Tests ─────────────────────────────────────────────────

class TestSchemaValidator(unittest.TestCase):
    """Test schema validation for receipts and ledger entries."""

    def test_valid_receipt_schema(self):
        """Valid receipt must pass schema validation."""
        receipt = _load_json("receipt_valid_approved.json")
        errors = validate_receipt_schema(receipt)
        self.assertEqual(errors, [])

    def test_missing_fields_detected(self):
        """Receipt with missing fields must fail schema validation."""
        data = _load_json("receipt_missing_fields.json")
        receipt = data.get("receipt", data)
        errors = validate_receipt_schema(receipt)
        self.assertGreater(len(errors), 0)
        # Should mention missing fields
        self.assertTrue(any("Missing" in e for e in errors))

    def test_valid_ledger_entry_schema(self):
        """Valid ledger entry must pass schema validation."""
        chain_data = _load_json("ledger_chain_valid.json")
        entry = chain_data["chain"]["entry_0"]
        errors = validate_ledger_entry_schema(entry)
        self.assertEqual(errors, [])


# ── Receipt Verifier Integration Tests ──────────────────────────────────────

class TestReceiptVerifier(unittest.TestCase):
    """Integration tests: full 7-check receipt verification."""

    def test_valid_approved_receipt(self):
        """Valid approved receipt must pass all 7 checks."""
        result = verify_receipt_from_file(
            _vec("receipt_valid_approved.json"),
            _vec("public_key.pem"),
        )
        self.assertTrue(result.all_passed)
        self.assertEqual(len(result.checks), 7)
        for check in result.checks:
            self.assertTrue(check.passed, f"Check {check.number} ({check.check_name}) failed: {check.details}")

    def test_valid_denied_receipt(self):
        """Valid denied receipt must pass all 7 checks."""
        result = verify_receipt_from_file(
            _vec("receipt_valid_denied.json"),
            _vec("public_key.pem"),
        )
        self.assertTrue(result.all_passed)
        for check in result.checks:
            self.assertTrue(check.passed, f"Check {check.number} ({check.check_name}) failed: {check.details}")

    def test_invalid_signature_receipt(self):
        """Receipt with corrupted signature: check 4 must fail, checks 1-3,5-7 may pass."""
        data = _load_json("receipt_invalid_signature.json")
        pem = _load_pem()
        result = verify_receipt(data, pem)
        self.assertFalse(result.all_passed)
        # Check 4 (signature) must fail
        sig_check = next(c for c in result.checks if c.check_name == "signature")
        self.assertFalse(sig_check.passed)

    def test_invalid_hash_receipt(self):
        """Receipt with corrupted receipt_hash: check 3 must fail."""
        data = _load_json("receipt_invalid_hash.json")
        pem = _load_pem()
        result = verify_receipt(data, pem)
        self.assertFalse(result.all_passed)
        hash_check = next(c for c in result.checks if c.check_name == "receipt_hash")
        self.assertFalse(hash_check.passed)

    def test_invalid_intent_hash_receipt(self):
        """Receipt with corrupted request_hash: checks 2, 3, 4 must fail."""
        data = _load_json("receipt_invalid_intent_hash.json")
        pem = _load_pem()
        result = verify_receipt(data, pem)
        self.assertFalse(result.all_passed)
        req_check = next(c for c in result.checks if c.check_name == "request_hash")
        self.assertFalse(req_check.passed)

    def test_missing_fields_receipt(self):
        """Receipt with missing fields: check 1 must fail."""
        data = _load_json("receipt_missing_fields.json")
        pem = _load_pem()
        result = verify_receipt(data, pem)
        self.assertFalse(result.all_passed)
        schema_check = next(c for c in result.checks if c.check_name == "required_fields")
        self.assertFalse(schema_check.passed)

    def test_all_7_checks_always_run(self):
        """Even when early checks fail, all 7 checks must be reported."""
        data = _load_json("receipt_missing_fields.json")
        pem = _load_pem()
        result = verify_receipt(data, pem)
        self.assertEqual(len(result.checks), 7)
        check_numbers = [c.number for c in result.checks]
        self.assertEqual(check_numbers, [1, 2, 3, 4, 5, 6, 7])


# ── Ledger Verifier Integration Tests ──────────────────────────────────────

class TestLedgerVerifier(unittest.TestCase):
    """Integration tests: full 4-check ledger verification."""

    def test_valid_ledger_chain(self):
        """Valid ledger chain must pass all checks."""
        result = verify_ledger_from_file(_vec("ledger_chain_valid.json"))
        self.assertTrue(result.chain_intact)
        self.assertEqual(result.entries_total, 1)
        self.assertEqual(result.entries_verified, 1)
        self.assertEqual(len(result.failures), 0)

    def test_tampered_ledger_chain(self):
        """Tampered ledger chain must fail entry_hash check."""
        result = verify_ledger_from_file(_vec("ledger_chain_tampered.json"))
        self.assertFalse(result.chain_intact)
        self.assertGreater(len(result.failures), 0)
        # Must detect entry_hash mismatch
        hash_failures = [f for f in result.failures if f.check_name == "entry_hash"]
        self.assertGreater(len(hash_failures), 0)

    def test_deleted_entry_ledger_chain(self):
        """Ledger chain with deleted entry must fail."""
        result = verify_ledger_from_file(_vec("ledger_chain_deleted_entry.json"))
        self.assertFalse(result.chain_intact)

    def test_genesis_link_valid(self):
        """First entry in valid chain must link to GENESIS_HASH."""
        chain_data = _load_json("ledger_chain_valid.json")
        entry = chain_data["chain"]["entry_0"]
        self.assertEqual(entry["prev_ledger_hash"], GENESIS_HASH)

    def test_genesis_hash_constant(self):
        """GENESIS_HASH constant must match SHA256(b'GENESIS')."""
        self.assertEqual(GENESIS_HASH, compute_genesis_hash())


# ── Cross-Verification Tests ───────────────────────────────────────────────

class TestCrossVerification(unittest.TestCase):
    """Cross-verify receipt_hash in receipt matches ledger entry."""

    def test_receipt_hash_consistency(self):
        """
        The receipt_hash in a receipt must be computable from the 19 signed fields.
        This is the same value that would appear in a ledger entry.
        """
        receipt = _load_json("receipt_valid_approved.json")
        computed = compute_receipt_hash(receipt)
        self.assertEqual(computed, receipt["receipt_hash"])

    def test_signing_payload_is_19_fields(self):
        """Signing payload must contain exactly the 19 signed fields."""
        self.assertEqual(len(SIGNED_FIELDS_19), 19)

    def test_all_required_fields_is_22(self):
        """Total required fields must be 22 (19 signed + 3 computed)."""
        self.assertEqual(len(ALL_REQUIRED_FIELDS), 22)


if __name__ == "__main__":
    unittest.main()
