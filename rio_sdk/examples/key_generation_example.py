#!/usr/bin/env python3
"""
RIO SDK — Key Generation Example

Ed25519 keygen, save/load, sign/verify, JSON signing.

Usage:
    python key_generation_example.py
"""

import json
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rio_sdk import Ed25519Key, Ed25519Signer, ECDSAKey, ECDSASigner

# ─── Ed25519 ──────────────────────────────────────────────────────

print("=== Ed25519 Key Generation ===")
key = Ed25519Key.generate()
print(f"Public key (b64): {key.public_key_b64}")
print(f"Public key (hex): {key.public_key_hex}")
print(f"Fingerprint:      {key.fingerprint}")
print(f"Approver ID:      {key.approver_id}")

# Save and reload
with tempfile.TemporaryDirectory() as tmpdir:
    priv_path = os.path.join(tmpdir, "ed25519_private.pem")
    pub_path = os.path.join(tmpdir, "ed25519_public.pem")
    key.save(priv_path, pub_path)
    print(f"\nSaved to: {priv_path}")

    loaded = Ed25519Key.from_file(priv_path)
    assert loaded.public_key_hex == key.public_key_hex
    print("Loaded and verified: keys match ✓")

# Sign and verify
signer = Ed25519Signer(key)
message = "Hello, RIO Protocol!"
signature = signer.sign(message)
print(f"\nMessage:   {message}")
print(f"Signature: {signature[:40]}...")
print(f"Valid:     {signer.verify(message, signature)} ✓")
print(f"Tampered:  {signer.verify(message + '!', signature)} ✗")

# JSON signing
payload = {"action": "transfer", "amount": 50000, "currency": "USD"}
json_sig = signer.sign_json(payload)
print(f"\nJSON payload: {json.dumps(payload)}")
print(f"JSON sig:     {json_sig[:40]}...")

# ─── ECDSA (secp256k1) ───────────────────────────────────────────

print("\n=== ECDSA secp256k1 Key Generation ===")
ecdsa_key = ECDSAKey.generate()
print(f"Public key (PEM): {ecdsa_key.public_key_pem[:60]}...")

ecdsa_signer = ECDSASigner(ecdsa_key)
ecdsa_sig = ecdsa_signer.sign(message)
print(f"Signature: {ecdsa_sig[:40]}...")
print(f"Valid:     {ecdsa_signer.verify(message, ecdsa_sig)} ✓")
print(f"Tampered:  {ecdsa_signer.verify(message + '!', ecdsa_sig)} ✗")

print("\n=== All key operations completed successfully ===")
