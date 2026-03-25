"""
RIO Runtime — Governance Learning (Asynchronous)

Reads from the audit ledger and governed corpus to produce policy and risk
model update recommendations. The learning loop operates on historical data
and does not bypass runtime enforcement.

Safety constraints (INV-05):
- Cannot execute actions.
- Cannot issue authorization tokens.
- Cannot write to the ledger.
- Cannot bypass the execution gate.
- Cannot access or modify the kill switch.
- Cannot change invariants without governance approval.

Spec reference: /spec/governance_learning_protocol.md, /spec/10_learning.md
Protocol stage: Step 9 (asynchronous) of the Governed Execution Protocol
Related invariants: INV-05 (Learning Separation)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .models import Decision, ExecutionStatus, LedgerEntry, Receipt
from . import ledger as ledger_module

logger = logging.getLogger("rio.governance_learning")


@dataclass
class LearningRecommendation:
    """
    A recommendation produced by the governance learning loop.

    Recommendations are proposals only. They must be reviewed and approved
    through the governance change process before being deployed to the runtime.
    """
    recommendation_id: str = ""
    recommendation_type: str = ""  # "risk_model" | "policy_rule" | "threshold" | "classification"
    description: str = ""
    proposed_change: dict[str, Any] = field(default_factory=dict)
    supporting_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class LearningReport:
    """Summary report from a governance learning analysis run."""
    total_entries_analyzed: int = 0
    denial_count: int = 0
    execution_count: int = 0
    failure_count: int = 0
    kill_switch_count: int = 0
    recommendations: list[LearningRecommendation] = field(default_factory=list)


def analyze_ledger(receipts: list[Receipt]) -> LearningReport:
    """
    Analyze historical receipts to produce governance recommendations.

    This function reads from the governed corpus (receipts and ledger entries)
    and produces recommendations for policy and risk model updates. It does
    not execute any actions or modify the runtime state.

    Args:
        receipts: Historical receipts to analyze.

    Returns:
        A LearningReport containing analysis results and recommendations.
    """
    report = LearningReport(total_entries_analyzed=len(receipts))

    # Count outcomes
    for receipt in receipts:
        if receipt.decision == Decision.DENY:
            report.denial_count += 1
        elif receipt.execution_status == ExecutionStatus.EXECUTED:
            report.execution_count += 1
        elif receipt.execution_status == ExecutionStatus.FAILED:
            report.failure_count += 1
        elif receipt.execution_status == ExecutionStatus.KILL_SWITCH_BLOCKED:
            report.kill_switch_count += 1

    # Generate recommendations based on patterns (reference skeleton)
    report.recommendations = _generate_recommendations(receipts, report)

    logger.info(
        "Learning analysis complete: %d entries, %d executions, %d denials, "
        "%d failures, %d kill switch blocks, %d recommendations",
        report.total_entries_analyzed,
        report.execution_count,
        report.denial_count,
        report.failure_count,
        report.kill_switch_count,
        len(report.recommendations),
    )

    return report


def _generate_recommendations(
    receipts: list[Receipt],
    report: LearningReport,
) -> list[LearningRecommendation]:
    """
    Generate policy and risk model recommendations based on observed patterns.

    In a production implementation, this would use statistical analysis,
    anomaly detection, and machine learning models trained on the governed corpus.
    This reference skeleton provides placeholder recommendation logic.

    Args:
        receipts: Historical receipts.
        report: The current learning report with aggregate counts.

    Returns:
        A list of LearningRecommendations.
    """
    recommendations: list[LearningRecommendation] = []

    # Example: High failure rate recommendation
    if report.total_entries_analyzed > 0:
        failure_rate = report.failure_count / report.total_entries_analyzed
        if failure_rate > 0.1:
            recommendations.append(
                LearningRecommendation(
                    recommendation_id="REC-FAILURE-RATE",
                    recommendation_type="risk_model",
                    description=(
                        f"Failure rate is {failure_rate:.1%}, exceeding 10% threshold. "
                        "Consider reviewing execution handlers and risk scoring."
                    ),
                    proposed_change={
                        "action": "increase_risk_score",
                        "scope": "failed_action_types",
                        "adjustment": 0.1,
                    },
                    supporting_evidence=[
                        f"{report.failure_count} failures out of "
                        f"{report.total_entries_analyzed} total entries"
                    ],
                    confidence=0.7,
                )
            )

    # Example: High denial rate recommendation
    if report.total_entries_analyzed > 0:
        denial_rate = report.denial_count / report.total_entries_analyzed
        if denial_rate > 0.3:
            recommendations.append(
                LearningRecommendation(
                    recommendation_id="REC-DENIAL-RATE",
                    recommendation_type="policy_rule",
                    description=(
                        f"Denial rate is {denial_rate:.1%}, exceeding 30% threshold. "
                        "Consider reviewing policy rules for over-restriction."
                    ),
                    proposed_change={
                        "action": "review_policy_thresholds",
                        "scope": "high_denial_actions",
                    },
                    supporting_evidence=[
                        f"{report.denial_count} denials out of "
                        f"{report.total_entries_analyzed} total entries"
                    ],
                    confidence=0.6,
                )
            )

    return recommendations
