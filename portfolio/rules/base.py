from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class EvaluationResult:
    """The persisted outcome of evaluating one rule for one stock."""

    score: float
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError("Rule scores must be between 0 and 100.")


class RuleEvaluator(ABC):
    """Contract implemented by every portfolio scoring rule."""

    rule_type: str

    @abstractmethod
    def evaluate(self, stock: Mapping[str, Any]) -> EvaluationResult:
        """Evaluate a stock snapshot and return a normalized 0-100 result."""
