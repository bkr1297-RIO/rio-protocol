"""
RIO Runtime — Identity and Access Management (IAM)

Provides user identity, role-based access control, permissions enforcement,
session management, and approval authority for the governed execution system.

Modules:
    users.py        — User registry (load, lookup, validate)
    roles.py        — Role definitions and hierarchy
    permissions.py  — Permission checks (can_request, can_approve, approval_limits)
    sessions.py     — Session token issuance, validation, and user attachment
    approval_workflow.py — Authority-aware approval workflow
"""
