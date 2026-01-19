from dataclasses import dataclass


@dataclass
class RegimeState:
    regime: str
    regime_prob: float
    signal_confidence: float
    risk_state: str


def infer_regime() -> RegimeState:
    return RegimeState(regime="neutral", regime_prob=0.5, signal_confidence=0.2, risk_state="NORMAL")
