from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class Example:
    id: str
    question: str
    answers: list[str]
    passages: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Example":
        missing = [k for k in ("id", "question", "answers", "passages") if k not in d]
        if missing:
            raise ValueError(f"Missing fields: {missing}")
        if not isinstance(d["answers"], list) or not d["answers"]:
            raise ValueError("answers must be a non-empty list")
        if not isinstance(d["passages"], list) or not d["passages"]:
            raise ValueError("passages must be a non-empty list")
        return cls(str(d["id"]), str(d["question"]), [str(x) for x in d["answers"]], [str(x) for x in d["passages"]])
