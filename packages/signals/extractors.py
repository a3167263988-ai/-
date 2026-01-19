from dataclasses import dataclass


@dataclass
class Signal:
    name: str
    value: float
    confidence: float


class SignalExtractor:
    def extract(self) -> list[Signal]:
        return [Signal(name="baseline", value=0.0, confidence=0.1)]
