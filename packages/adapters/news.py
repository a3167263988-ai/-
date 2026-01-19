from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Event:
    source: str
    ts: str
    headline: str
    keywords: list[str]
    topic: str
    sentiment_score: float
    impact_score: float
    confidence: float


class NewsAdapter:
    def fetch_events(self) -> list[Event]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            Event(
                source="crypto_panic",
                ts=now,
                headline="No major headlines",
                keywords=[],
                topic="general",
                sentiment_score=0.0,
                impact_score=0.0,
                confidence=0.0,
            )
        ]
