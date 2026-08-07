"""Small, serialisable models used by the static audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}


@dataclass(frozen=True, slots=True)
class Finding:
    """A redacted, customer-safe audit finding.

    Evidence is deliberately limited to relative file paths and static rule
    names. It must never contain source snippets, credentials, or an absolute
    client path.
    """

    rule_id: str
    severity: str
    category: str
    title: str
    evidence: tuple[str, ...]
    recommendation: str
    status: str = "open"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data


@dataclass(slots=True)
class AuditResult:
    """The single source of truth rendered into JSON and Markdown reports."""

    audit_id: str
    generated_at: str
    repository: str
    client: str | None
    coverage: dict[str, Any]
    inventory: dict[str, Any]
    checks: list[dict[str, Any]]
    findings: list[Finding] = field(default_factory=list)
    score: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "audit_id": self.audit_id,
            "generated_at": self.generated_at,
            "repository": self.repository,
            "client": self.client,
            "coverage": self.coverage,
            "inventory": self.inventory,
            "checks": self.checks,
            "score": self.score,
            "findings": [finding.as_dict() for finding in self.findings],
            "limitations": self.limitations,
        }


def stable_findings(findings: list[Finding]) -> list[Finding]:
    """Return findings in a deterministic, customer-friendly order."""

    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item.severity, 99),
            item.category,
            item.rule_id,
            item.evidence,
        ),
    )
