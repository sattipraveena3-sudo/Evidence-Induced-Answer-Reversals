from __future__ import annotations

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod


class Backend(ABC):
    @abstractmethod
    def answer(self, question: str, passages: list[str]) -> str:
        raise NotImplementedError


class OpenAIBackend(Backend):
    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        base_url: str = "https://api.openai.com/v1",
    ):
        self.model = model
        self.temperature = temperature
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

    def complete(self, prompt: str, max_tokens: int = 64) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")

        last_error = None
        for attempt in range(8):
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    obj = json.loads(r.read().decode("utf-8"))
                return obj["choices"][0]["message"]["content"].strip()
            except urllib.error.HTTPError as e:
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except (OSError, UnicodeError):
                    body = ""
                retry_after = e.headers.get("Retry-After") if e.headers else None
                detail = f"OpenAI HTTP {e.code}: {body or e.reason}"
                last_error = RuntimeError(detail)
                # 401/403/404 are not transient. 429/5xx may be retried.
                if e.code not in (408, 409, 429, 500, 502, 503, 504):
                    raise last_error
                # insufficient_quota will not be fixed by retries; surface it immediately.
                if "insufficient_quota" in body or "billing" in body.lower():
                    raise last_error
                if attempt == 7:
                    raise last_error
                try:
                    wait = (
                        float(retry_after)
                        if retry_after
                        else min(60.0, (2**attempt) + random.random())
                    )
                except ValueError:
                    wait = min(60.0, (2**attempt) + random.random())
                time.sleep(wait)
            except Exception as e:
                last_error = e
                if attempt == 7:
                    raise
                time.sleep(min(60.0, (2**attempt) + random.random()))
        raise last_error or RuntimeError("OpenAI request failed")

    def answer(self, question: str, passages: list[str]) -> str:
        context = "\n\n".join(f"[{i + 1}] {p}" for i, p in enumerate(passages))
        prompt = (
            "Answer the question using only the evidence below. "
            "Return only a short factual answer. If the evidence is insufficient, return unknown.\n\n"
            f"Question: {question}\n\nEvidence:\n{context}"
        )
        return self.complete(prompt, 64)


class MockBackend(Backend):
    answer_re = re.compile(r"\[\[answer:(.*?)\]\]", re.IGNORECASE)
    flip_re = re.compile(r"\[\[flip:(.*?)\]\]", re.IGNORECASE)

    def answer(self, question: str, passages: list[str]) -> str:
        ans = "unknown"
        for p in passages:
            m = self.answer_re.search(p)
            if m:
                ans = m.group(1).strip()
            f = self.flip_re.search(p)
            if f:
                ans = f.group(1).strip()
        return ans


def make_backend(
    name: str,
    model: str | None,
    temperature: float = 0.0,
    base_url: str = "https://api.openai.com/v1",
) -> Backend:
    if name == "mock":
        return MockBackend()
    if name == "openai":
        if not model:
            raise ValueError("--model is required for openai backend")
        return OpenAIBackend(model=model, temperature=temperature, base_url=base_url)
    raise ValueError(f"Unknown backend: {name}")
