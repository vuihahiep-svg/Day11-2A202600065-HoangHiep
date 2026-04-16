"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money",
    "close_account",
    "change_password",
    "delete_data",
    "update_personal_info",
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool
    hitl_model: str      # e.g. none, human-in-the-loop, human-on-the-loop


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        if action_type in HIGH_RISK_ACTIONS:
            return RoutingDecision(
                action="escalate",
                confidence=confidence,
                reason=f"High-risk action: {action_type}",
                priority="high",
                requires_human=True,
                hitl_model="human-in-the-loop",
            )

        if confidence >= self.HIGH_THRESHOLD:
            return RoutingDecision(
                action="auto_send",
                confidence=confidence,
                reason="High confidence",
                priority="low",
                requires_human=False,
                hitl_model="none",
            )
        if confidence >= self.MEDIUM_THRESHOLD:
            return RoutingDecision(
                action="queue_review",
                confidence=confidence,
                reason="Medium confidence — needs review",
                priority="normal",
                requires_human=True,
                hitl_model="human-on-the-loop",
            )
        return RoutingDecision(
            action="escalate",
            confidence=confidence,
            reason="Low confidence — escalating",
            priority="high",
            requires_human=True,
            hitl_model="human-in-the-loop",
        )


# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "name": "High-value outbound transfer",
        "scenario": "Large or unusual transfer to a new or high-risk beneficiary.",
        "trigger": "Customer requests a transfer above policy threshold (e.g. > 50M VND) or to a new payee.",
        "hitl_model": "human-in-the-loop",
        "context_for_human": "Source account, payee KYC status, transfer history, device/session risk score.",
        "expected_response_time": "< 5 minutes",
        "context_needed": "Source account, payee KYC status, transfer history, device/session risk score.",
        "example": "User asks to wire 80M VND to a first-time beneficiary while abroad.",
    },
    {
        "id": 2,
        "name": "Account closure or credential reset",
        "scenario": "Irreversible product closure or credential recovery.",
        "trigger": "Closure of all products, password reset, or token issuance for high-privilege actions.",
        "hitl_model": "human-in-the-loop",
        "context_for_human": "Identity verification result, recent alerts, duplicate requests, branch notes.",
        "expected_response_time": "< 15 minutes",
        "context_needed": "Identity verification result, recent alerts, duplicate requests, branch notes.",
        "example": "Chatbot schedules full account closure after suspected social-engineering cues.",
    },
    {
        "id": 3,
        "name": "Model disagreement / low confidence",
        "scenario": "Policy or judge disagrees with the draft answer.",
        "trigger": "Safety judge conflicts with policy engine, or confidence score below routing threshold.",
        "hitl_model": "human-as-tiebreaker",
        "context_for_human": "Draft reply, judge rationale, triggered rules, customer segment.",
        "expected_response_time": "< 10 minutes",
        "context_needed": "Draft reply, judge rationale, triggered rules, customer segment.",
        "example": "Ambiguous fee dispute where the model is 62% confident and judges disagree.",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Balance inquiry", 0.95, "general"),
        ("Interest rate question", 0.82, "general"),
        ("Ambiguous request", 0.55, "general"),
        ("Transfer $50,000", 0.98, "transfer_money"),
        ("Close my account", 0.91, "close_account"),
    ]

    print("Testing ConfidenceRouter:")
    print("=" * 80)
    print(
        f"{'Scenario':<22} {'Conf':<6} {'Action Type':<16} {'Decision':<14} "
        f"{'HITL model':<22} {'Human?'}"
    )
    print("-" * 80)

    for scenario, conf, action_type in test_cases:
        decision = router.route(scenario, conf, action_type)
        print(
            f"{scenario:<22} {conf:<6.2f} {action_type:<16} "
            f"{decision.action:<14} {decision.hitl_model:<22} "
            f"{'Yes' if decision.requires_human else 'No'}"
        )

    print("=" * 80)


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points:")
    print("=" * 60)
    for point in hitl_decision_points:
        print(f"\n  Decision Point #{point['id']}: {point['name']}")
        if point.get("scenario"):
            print(f"    Scenario: {point['scenario']}")
        print(f"    Trigger:  {point['trigger']}")
        print(f"    Model:    {point['hitl_model']}")
        print(f"    Context:  {point.get('context_for_human') or point['context_needed']}")
        print(f"    SLA:      {point.get('expected_response_time', 'n/a')}")
        print(f"    Example:  {point['example']}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
