from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TrendsSnapshot:
    ts: str
    keyword: str
    score: float
    confidence: float


class TrendsAdapter:
    def fetch_trends(self, keywords: list[str]) -> list[TrendsSnapshot]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            TrendsSnapshot(ts=now, keyword=kw, score=0.0, confidence=0.0)
            for kw in keywords
        ]
