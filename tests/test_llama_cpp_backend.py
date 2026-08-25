import hashlib
import sys
from types import SimpleNamespace

from ear.backends import LlamaCppBackend


def test_llama_cpp_backend_uses_local_model_and_records_provenance(
    tmp_path, monkeypatch
):
    calls = {}

    class FakeLlama:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def create_chat_completion(self, **kwargs):
            calls["chat"] = kwargs
            return {
                "choices": [{"message": {"content": "Paris"}}],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 1,
                    "total_tokens": 21,
                },
            }

    monkeypatch.setitem(
        sys.modules,
        "llama_cpp",
        SimpleNamespace(Llama=FakeLlama, __version__="test-version"),
    )
    model = tmp_path / "model.gguf"
    model.write_bytes(b"test model")

    backend = LlamaCppBackend(
        str(model), context_size=2048, threads=2, batch_size=64, seed=7
    )
    answer = backend.answer(
        "What is the capital of France?", ["The capital of France is Paris."]
    )

    assert answer == "Paris"
    assert calls["init"]["model_path"] == str(model)
    assert calls["init"]["n_ctx"] == 2048
    assert calls["chat"]["temperature"] == 0.0
    assert calls["chat"]["seed"] == 7
    assert "Evidence:" in calls["chat"]["messages"][1]["content"]
    assert calls["chat"]["messages"][0]["content"] == backend.system_prompt
    assert backend.last_usage == {
        "prompt_tokens": 20,
        "completion_tokens": 1,
        "total_tokens": 21,
    }
    assert (
        backend.metadata()["model_sha256"] == hashlib.sha256(b"test model").hexdigest()
    )

    backend.complete("Return strict JSON", max_tokens=8)
    assert calls["chat"]["max_tokens"] == 8
    assert calls["chat"]["messages"][0]["content"] == backend.completion_system_prompt
