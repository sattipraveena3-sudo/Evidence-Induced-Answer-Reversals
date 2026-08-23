from __future__ import annotations
import os, json, urllib.request, time, re
from abc import ABC, abstractmethod

class Backend(ABC):
    @abstractmethod
    def answer(self, question: str, passages: list[str]) -> str:
        raise NotImplementedError

class OpenAIBackend(Backend):
    def __init__(self, model: str, temperature: float = 0.0, base_url: str = "https://api.openai.com/v1"):
        self.model = model
        self.temperature = temperature
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

    def answer(self, question: str, passages: list[str]) -> str:
        context = "\n\n".join(f"[{i+1}] {p}" for i, p in enumerate(passages))
        prompt = (
            "Answer the question using only the evidence below. "
            "Return only a short factual answer. If the evidence is insufficient, return unknown.\n\n"
            f"Question: {question}\n\nEvidence:\n{context}"
        )
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    obj = json.loads(r.read().decode("utf-8"))
                return obj["choices"][0]["message"]["content"].strip()
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)

class MockBackend(Backend):
    answer_re = re.compile(r"\[\[answer:(.*?)\]\]", re.I)
    flip_re = re.compile(r"\[\[flip:(.*?)\]\]", re.I)

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

def make_backend(name: str, model: str | None, temperature: float = 0.0,
                 base_url: str = "https://api.openai.com/v1") -> Backend:
    if name == "mock":
        return MockBackend()
    if name == "openai":
        if not model:
            raise ValueError("--model is required for openai backend")
        return OpenAIBackend(model=model, temperature=temperature, base_url=base_url)
    raise ValueError(f"Unknown backend: {name}")
