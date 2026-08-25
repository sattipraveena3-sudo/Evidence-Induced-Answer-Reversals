from __future__ import annotations

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path


class Backend(ABC):
    @abstractmethod
    def answer(self, question: str, passages: list[str]) -> str:
        raise NotImplementedError

    def metadata(self) -> dict[str, object]:
        return {"backend": self.__class__.__name__}


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

    def metadata(self) -> dict[str, object]:
        return {
            "backend": "openai",
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }


class LlamaCppBackend(Backend):
    """Run a local GGUF instruction model without a hosted API."""

    system_prompt = (
        "Answer only from the supplied evidence. Return only a short factual answer. "
        "If the evidence is insufficient, return unknown."
    )
    completion_system_prompt = "Follow the user's instructions exactly."

    def __init__(
        self,
        model_path: str,
        temperature: float = 0.0,
        context_size: int = 4096,
        threads: int | None = None,
        batch_size: int = 512,
        seed: int = 7,
        max_tokens: int = 32,
    ):
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"GGUF model not found: {path}")
        try:
            import llama_cpp
        except ImportError as exc:
            raise RuntimeError(
                "llama-cpp-python is required for --backend llama-cpp; "
                "install the local extra with `python -m pip install -e '.[local]'`"
            ) from exc

        self.model_path = path
        self.temperature = temperature
        self.context_size = context_size
        self.threads = threads or max(1, min(8, os.cpu_count() or 1))
        self.batch_size = batch_size
        self.seed = seed
        self.max_tokens = max_tokens
        self.llama_cpp_version = getattr(llama_cpp, "__version__", "unknown")
        self.last_usage: dict[str, int] | None = None
        self._model_sha256 = self._sha256(path)
        self._llm = llama_cpp.Llama(
            model_path=str(path),
            n_ctx=context_size,
            n_threads=self.threads,
            n_threads_batch=self.threads,
            n_batch=batch_size,
            seed=seed,
            verbose=False,
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _chat(self, prompt: str, max_tokens: int, system_prompt: str) -> str:
        result = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=max_tokens,
            seed=self.seed,
        )
        usage = result.get("usage")
        self.last_usage = dict(usage) if isinstance(usage, dict) else None
        content = result["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("Local model returned no text content")
        return content.strip()

    def complete(self, prompt: str, max_tokens: int = 64) -> str:
        return self._chat(prompt, max_tokens, self.completion_system_prompt)

    def answer(self, question: str, passages: list[str]) -> str:
        context = "\n\n".join(f"[{i + 1}] {p}" for i, p in enumerate(passages))
        prompt = f"Question: {question}\n\nEvidence:\n{context}"
        return self._chat(prompt, self.max_tokens, self.system_prompt)

    def metadata(self) -> dict[str, object]:
        return {
            "backend": "llama-cpp",
            "model_file": self.model_path.name,
            "model_sha256": self._model_sha256,
            "llama_cpp_version": self.llama_cpp_version,
            "temperature": self.temperature,
            "context_size": self.context_size,
            "threads": self.threads,
            "batch_size": self.batch_size,
            "seed": self.seed,
            "max_tokens": self.max_tokens,
        }


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

    def metadata(self) -> dict[str, object]:
        return {"backend": "mock", "research_result": False}


def make_backend(
    name: str,
    model: str | None,
    temperature: float = 0.0,
    base_url: str = "https://api.openai.com/v1",
    context_size: int = 4096,
    threads: int | None = None,
    batch_size: int = 512,
    seed: int = 7,
    max_tokens: int = 32,
) -> Backend:
    if name == "mock":
        return MockBackend()
    if name == "openai":
        if not model:
            raise ValueError("--model is required for openai backend")
        return OpenAIBackend(model=model, temperature=temperature, base_url=base_url)
    if name == "llama-cpp":
        if not model:
            raise ValueError("--model must point to a GGUF file for llama-cpp backend")
        return LlamaCppBackend(
            model_path=model,
            temperature=temperature,
            context_size=context_size,
            threads=threads,
            batch_size=batch_size,
            seed=seed,
            max_tokens=max_tokens,
        )
    raise ValueError(f"Unknown backend: {name}")
