"""
RIO SDK — Typed Exception Hierarchy

    RIOError (base)
    ├── RIOConnectionError   — Cannot reach gateway
    ├── RIOHTTPError         — HTTP error with .status_code + .body
    ├── RIOIntentBlockedError — .receipt contains signed denial receipt
    ├── RIOVerificationError — 7-check verification failed
    ├── RIOLedgerError       — Chain formula verification failed
    ├── RIOApprovalError     — Human approval rejected or timed out
    ├── RIOKeyError          — Key management error
    └── RIOConfigError       — SDK configuration error
"""


class RIOError(Exception):
    """Base exception for all RIO SDK errors."""
    pass


class RIOConnectionError(RIOError):
    """Cannot reach the RIO gateway."""
    pass


class RIOHTTPError(RIOError):
    """HTTP-level error from the gateway."""

    def __init__(self, status_code: int, body: str, message: str = ""):
        self.status_code = status_code
        self.body = body
        super().__init__(message or f"HTTP {status_code}: {body[:200]}")


class RIOIntentBlockedError(RIOError):
    """Intent was blocked by governance. The signed denial receipt is attached."""

    def __init__(self, receipt: dict, message: str = ""):
        self.receipt = receipt
        super().__init__(message or f"Intent blocked: {receipt.get('decision', 'unknown')}")


class RIOVerificationError(RIOError):
    """One or more of the 7 verification checks failed."""

    def __init__(self, results: list, message: str = ""):
        self.results = results
        failed = [r for r in results if not r.get("passed")]
        super().__init__(message or f"Verification failed: {len(failed)} check(s) did not pass")


class RIOLedgerError(RIOError):
    """Ledger chain formula verification failed."""

    def __init__(self, details: dict = None, message: str = ""):
        self.details = details or {}
        super().__init__(message or "Ledger chain integrity verification failed")


class RIOApprovalError(RIOError):
    """Human approval was rejected or timed out."""

    def __init__(self, approval_id: str = "", reason: str = "", message: str = ""):
        self.approval_id = approval_id
        self.reason = reason
        super().__init__(message or f"Approval {approval_id} failed: {reason}")


class RIOKeyError(RIOError):
    """Key management error (generation, loading, signing)."""
    pass


class RIOConfigError(RIOError):
    """SDK configuration error."""
    pass
