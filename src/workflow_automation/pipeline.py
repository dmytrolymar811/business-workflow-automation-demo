from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


class TransientStepError(RuntimeError):
    """An integration error that may succeed when retried."""


@dataclass(frozen=True)
class Step:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    retries: int = 0


@dataclass(frozen=True)
class ExecutionRecord:
    step: str
    status: str
    attempt: int
    timestamp: str
    detail: str = ""


@dataclass
class Pipeline:
    steps: list[Step]
    processed_keys: set[str] = field(default_factory=set)
    history: list[ExecutionRecord] = field(default_factory=list)

    @staticmethod
    def idempotency_key(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _record(self, step: str, status: str, attempt: int, detail: str = "") -> None:
        self.history.append(
            ExecutionRecord(step, status, attempt, datetime.now(timezone.utc).isoformat(), detail)
        )

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        key = self.idempotency_key(payload)
        if key in self.processed_keys:
            self._record("pipeline", "skipped_duplicate", 0)
            return {**payload, "workflow_status": "duplicate_skipped"}

        state = dict(payload)
        for step in self.steps:
            for attempt in range(1, step.retries + 2):
                try:
                    state = step.handler(dict(state))
                    self._record(step.name, "completed", attempt)
                    break
                except TransientStepError as error:
                    self._record(step.name, "retry", attempt, str(error))
                    if attempt > step.retries:
                        self._record(step.name, "failed", attempt, str(error))
                        raise
                except Exception as error:
                    self._record(step.name, "failed", attempt, str(error))
                    raise
        self.processed_keys.add(key)
        return {**state, "workflow_status": "completed"}
