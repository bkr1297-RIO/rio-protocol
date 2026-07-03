"""
Portable Constitutional Engine - Gate Simulator v0.1
Candidate reference implementation / developer preview / non-production.

Deterministic evaluator for the Four-Bit Crossing Code:

    Authority AND Scope AND Consequence AND Return

This module does not perform any live tool calls, live adapter calls,
network requests, or cryptographic signing. It is a local, deterministic,
falsifiable candidate demonstration only.
"""

VERDICT_PASS = "PASS"
VERDICT_DENY = "DENY"
VERDICT_HOLD = "HOLD"
VERDICT_REST_STATE_HOLD = "REST_STATE_HOLD"
VERDICT_HARD_BLOCK = "HARD_BLOCK"

REQUIRED_FIELDS = [
    "capsule_id",
    "sourcepoint_id",
    "intent",
    "scope",
    "consequence_class",
    "return_path",
    "authority_envelope_ref",
    "timestamp",
]

ALLOWED_LOW_CONSEQUENCE_SCOPES = {"draft", "read", "summarize", "internal_note", "research"}
CONSEQUENCE_BEARING_SCOPES = {"send", "execute", "transfer", "delete", "deploy", "purchase", "publish"}
KNOWN_SCOPES = ALLOWED_LOW_CONSEQUENCE_SCOPES | CONSEQUENCE_BEARING_SCOPES

VALID_CONSEQUENCE_CLASSES = {"none", "low", "medium", "high", "critical"}


def _missing_required_fields(capsule):
    return [field for field in REQUIRED_FIELDS if not capsule.get(field)]


def _check_authority(capsule):
    ref = capsule.get("authority_envelope_ref", "")
    if not isinstance(ref, str) or not ref.strip():
        return False, "missing authority_envelope_ref"
    lowered = ref.lower()
    if "revoked" in lowered or "expired" in lowered:
        return False, "authority_envelope_ref indicates revoked or expired authority"
    return True, "authority_envelope_ref present and not flagged revoked/expired"


def _check_scope(capsule):
    scope = capsule.get("scope", "")
    if not isinstance(scope, str) or scope not in KNOWN_SCOPES:
        return False, f"scope '{scope}' is not a recognized candidate scope"
    return True, f"scope '{scope}' recognized"


def _check_return(capsule):
    return_path = capsule.get("return_path", "")
    if not isinstance(return_path, str) or not return_path.startswith("receipt://"):
        return False, "return_path missing or not a recognized receipt:// path"
    return True, "return_path present and receipt-shaped"


def evaluate(capsule):
    """
    Evaluate a candidate capsule dict against the Four-Bit Crossing Code.

    Returns a dict: {"verdict": <one of the VERDICT_* constants>, "reasons": [str, ...]}

    This is a candidate, local, deterministic evaluation only. It does not
    constitute live conformance, production enforcement, or certification.
    """
    reasons = []

    missing = _missing_required_fields(capsule)
    if missing:
        reasons.append(f"missing required fields: {', '.join(missing)}")
        return {"verdict": VERDICT_HARD_BLOCK, "reasons": reasons}

    consequence_class = capsule.get("consequence_class")
    if consequence_class not in VALID_CONSEQUENCE_CLASSES:
        reasons.append(f"unrecognized consequence_class '{consequence_class}'")
        return {"verdict": VERDICT_HARD_BLOCK, "reasons": reasons}

    authority_ok, authority_reason = _check_authority(capsule)
    reasons.append(authority_reason)
    scope_ok, scope_reason = _check_scope(capsule)
    reasons.append(scope_reason)
    return_ok, return_reason = _check_return(capsule)
    reasons.append(return_reason)

    if not authority_ok:
        reasons.append("Authority bit failed")
        return {"verdict": VERDICT_DENY, "reasons": reasons}

    if not scope_ok:
        reasons.append("Scope bit failed")
        return {"verdict": VERDICT_DENY, "reasons": reasons}

    if not return_ok:
        reasons.append("Return bit failed")
        return {"verdict": VERDICT_DENY, "reasons": reasons}

    if consequence_class == "critical":
        reasons.append(
            "Consequence bit: critical consequence class is never auto-crossed "
            "in this candidate gate"
        )
        return {"verdict": VERDICT_HARD_BLOCK, "reasons": reasons}

    if consequence_class == "high":
        reasons.append("Consequence bit: high consequence class requires a human checkpoint")
        return {"verdict": VERDICT_REST_STATE_HOLD, "reasons": reasons}

    if consequence_class == "medium":
        reasons.append("Consequence bit: medium consequence class held for review")
        return {"verdict": VERDICT_HOLD, "reasons": reasons}

    if capsule.get("scope") in CONSEQUENCE_BEARING_SCOPES and consequence_class in ("none", "low"):
        reasons.append(
            "Consequence bit: consequence-bearing scope held for review despite "
            "declared low/none consequence_class"
        )
        return {"verdict": VERDICT_HOLD, "reasons": reasons}

    reasons.append("Authority AND Scope AND Consequence AND Return all satisfied")
    return {"verdict": VERDICT_PASS, "reasons": reasons}
