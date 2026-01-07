from __future__ import annotations

from app.models.schemas import ExitPlan, LossExit, SidewaysExit
from app.spreads.constants import LOSS_EXIT_MULTIPLE, PROFIT_TAKE_PCT, THETA_STALL_THRESHOLD


def build_exit_plan(width: float, credit: float) -> ExitPlan:
    return ExitPlan(
        profitTakePct=PROFIT_TAKE_PCT,
        sidewaysExit=SidewaysExit(enabled=True, thetaStallThreshold=THETA_STALL_THRESHOLD),
        lossExit=LossExit(mode="creditMultiple", value=LOSS_EXIT_MULTIPLE),
    )
