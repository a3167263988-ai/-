from dataclasses import dataclass


@dataclass
class DataQualityResult:
    ok: bool
    issues: list[str]


def check_snapshot(snapshot: dict) -> DataQualityResult:
    issues: list[str] = []
    if not snapshot:
        issues.append("empty_snapshot")
    return DataQualityResult(ok=len(issues) == 0, issues=issues)
