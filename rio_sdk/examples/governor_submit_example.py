#!/usr/bin/env python3
"""
RIO SDK — Governor Submit Example

AWAITING_HUMAN_SIGNATURE flow with approval token.

Usage:
    export RIO_GATEWAY_URL=http://localhost:5000
    python governor_submit_example.py
"""

import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rio_sdk import RIOClient, IntentBuilder, Ed25519Key
from rio_sdk.exceptions import RIOApprovalError

GATEWAY = os.environ.get("RIO_GATEWAY_URL", "http://localhost:5000")

# 1. Build a high-risk intent that requires human approval
key = Ed25519Key.generate()
intent = (
    IntentBuilder("Transfer $50,000 from account A to account B", key=key)
    .with_context(user_id="u-42", environment="production")
    .with_metadata(risk_level="high", requires_approval=True)
    .build()
)
print(f"Intent ID: {intent.intent_id}")

# 2. Submit to the governor for human approval
client = RIOClient(GATEWAY)
submission = client.submit(intent)
print(f"Submission ID: {submission.submission_id}")
print(f"Status: {submission.status}")  # AWAITING_HUMAN_SIGNATURE

# 3. Poll for approval (in production, use webhooks)
print("Waiting for human approval...")
# In a real scenario, a human would approve via the gateway UI
# client.gate_approve(submission.submission_id)

# 4. Check pending approvals
pending = client.gate_pending()
print(f"Pending approvals: {len(pending)}")
