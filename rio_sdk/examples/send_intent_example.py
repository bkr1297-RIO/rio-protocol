#!/usr/bin/env python3
"""
RIO SDK — Send Intent Example

Full flow in <20 lines: evaluate → 7-check verify → ledger proof.

Usage:
    export RIO_GATEWAY_URL=http://localhost:5000
    python send_intent_example.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rio_sdk import RIOClient, IntentBuilder, ReceiptVerifier, Ed25519Key

GATEWAY = os.environ.get("RIO_GATEWAY_URL", "http://localhost:5000")

# 1. Generate a key pair and build a signed intent
key = Ed25519Key.generate()
intent = (
    IntentBuilder("Summarise the Q3 financial report", key=key)
    .with_context(user_id="u-42", environment="staging")
    .build()
)
print(f"Intent ID: {intent.intent_id}")

# 2. Submit to the governance gateway
client = RIOClient(GATEWAY)
result = client.evaluate(intent)
print(f"Decision: {result.receipt.decision}")

# 3. Verify the receipt (7 checks)
verifier = ReceiptVerifier(client.public_key_pem())
verification = verifier.verify(result.receipt)
print(f"Verification: {verification.summary}")

# 4. Confirm ledger inclusion
latest = client.ledger_latest()
print(f"Latest ledger entry: {latest.entry_hash[:16]}...")
