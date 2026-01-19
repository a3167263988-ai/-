from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class OnchainSnapshot:
    ts: str
    metrics: dict
    confidence: float


class OnchainAdapter:
    def fetch_snapshot(self, symbol: str) -> OnchainSnapshot:
        now = datetime.now(timezone.utc).isoformat()
        return OnchainSnapshot(ts=now, metrics={}, confidence=0.0)
