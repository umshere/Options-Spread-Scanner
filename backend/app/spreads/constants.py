"""Shared scoring and risk constants.

These values centralize the configuration used across spread construction,
scoring, and exit planning to avoid magic numbers sprinkled through the codebase.
"""

from __future__ import annotations

CREDIT_HAIRCUT = 0.85
CONTRACT_MULTIPLIER = 100

PROFIT_TAKE_PCT = 0.70
LOSS_EXIT_MULTIPLE = 1.50
THETA_STALL_THRESHOLD = 0.10

EV_WEIGHT = 0.40
ROR_WEIGHT = 0.25
LIQUIDITY_WEIGHT = 0.20
BIAS_WEIGHT = 0.10
EARNINGS_WEIGHT = 0.05

BIAS_ALIGNMENT_BONUS = 0.10
BIAS_MISALIGNMENT_PENALTY = -0.05

EARNINGS_SCORE_PENALTY = -0.10

