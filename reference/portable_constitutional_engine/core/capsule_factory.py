"""
  Portable Constitutional Engine - Capsule Factory v0.1
  Candidate reference implementation / developer preview / non-production.

  Turns a plain text prompt into a sample candidate Capsule using
  deterministic heuristics only. Does not call an external LLM.

  Any hash values produced here are deterministic receipt hashes used only
  to derive a stable candidate_id from input text. They are NOT a
  cryptographic authority proof.
  """
  import hashlib
  from datetime import datetime, timezone

  CONSEQUENCE_KEYWORDS = {
      "critical": ["delete everything", "wire transfer", "wire funds", "shut down production", "delete all"],
      "high": ["send payment", "transfer funds", "deploy to production", "delete account", "purchase"],
      "medium": ["send email", "send message", "publish", "post publicly", "execute"],
      "low": ["draft", "summarize", "read", "review", "research"],
  }

  SCOPE_KEYWORDS = {
      "transfer": ["transfer", "wire"],
      "delete": ["delete", "remove"],
      "deploy": ["deploy"],
      "purchase": ["purchase", "buy"],
      "publish": ["publish", "post"],
      "send": ["send"],
      "execute": ["execute", "run"],
      "summarize": ["summarize", "summarise"],
      "internal_note": ["note to self", "internal note"],
      "research": ["research", "look up"],
      "read": ["read", "review", "look at"],
      "draft": ["draft", "write"],
  }


  def _classify(text, mapping, default):
      lowered = text.lower()
      for key, keywords in mapping.items():
          for keyword in keywords:
              if keyword in lowered:
                  return key
      return default


  def _consequence_class(text):
      lowered = text.lower()
      for level in ("critical", "high", "medium", "low"):
          for keyword in CONSEQUENCE_KEYWORDS[level]:
              if keyword in lowered:
                  return level
      return "low"


  def _scope(text):
      return _classify(text, SCOPE_KEYWORDS, default="draft")


  def make_capsule(prompt, sourcepoint_id="sourcepoint-cli", authority_envelope_ref="env-candidate-local"):
      """
      Build a candidate Capsule dict from a plain text prompt using
      deterministic, local, standard-library-only heuristics.
      """
      if not isinstance(prompt, str) or not prompt.strip():
          raise ValueError("prompt must be a non-empty string")

      # Deterministic receipt hash used only to derive a stable id; not a
      # cryptographic authority proof.
      receipt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
      timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

      return {
          "capsule_id": f"caps-{receipt_hash}",
          "sourcepoint_id": sourcepoint_id,
          "intent": prompt.strip(),
          "scope": _scope(prompt),
          "consequence_class": _consequence_class(prompt),
          "return_path": "receipt://mus/ledger/local",
          "authority_envelope_ref": authority_envelope_ref,
          "timestamp": timestamp,
          "metadata": {
              "register": "developer_preview",
              "model_office": "Scribe-Compiler",
              "coherence_warning": "",
          },
      }
  