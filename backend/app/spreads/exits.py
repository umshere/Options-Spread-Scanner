from __future__ import annotations

from app.models.schemas import ExitPlan, LossExit, SidewaysExit


def build_exit_plan(width: float, credit: float) -> ExitPlan:
    profit_take_pct = 0.7
    sideways_threshold = 0.10
    loss_exit_multiple = 1.5

    return ExitPlan(
        profitTakePct=profit_take_pct,
        sidewaysExit=SidewaysExit(enabled=True, thetaStallThreshold=sideways_threshold),
        lossExit=LossExit(mode="creditMultiple", value=loss_exit_multiple),
    )
