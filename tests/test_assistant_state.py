import sys
import types

import tests.requests_stub  # noqa: F401
import tests.urllib3_stub  # noqa: F401


class _LLMError(Exception):
    """Stub para erros do modelo de linguagem."""


llm_interface_stub = types.ModuleType("hermes.services.llm_interface")
llm_interface_stub.LLMError = _LLMError
llm_interface_stub.gerar_resposta = lambda prompt: {"ok": True, "response": ""}
sys.modules.setdefault("hermes.services.llm_interface", llm_interface_stub)


class _Array(list):
    def ravel(self):
        return self

    def argsort(self):
        return _Array(sorted(range(len(self)), key=self.__getitem__))


class _TfidfVectorizer:
    def fit_transform(self, docs):
        return _Array([[0.0] * 1 for _ in docs])

    def transform(self, docs):
        return _Array([[0.0] * 1 for _ in docs])


def _cosine_similarity(query_vecs, matrix):
    return _Array([0.0 for _ in matrix])


sklearn = types.ModuleType("sklearn")
feature_extraction = types.ModuleType("sklearn.feature_extraction")
text = types.ModuleType("sklearn.feature_extraction.text")
text.TfidfVectorizer = _TfidfVectorizer
feature_extraction.text = text
metrics = types.ModuleType("sklearn.metrics")
pairwise = types.ModuleType("sklearn.metrics.pairwise")
pairwise.cosine_similarity = _cosine_similarity
metrics.pairwise = pairwise
sklearn.feature_extraction = feature_extraction
sklearn.metrics = metrics
sys.modules.setdefault("sklearn", sklearn)
sys.modules.setdefault("sklearn.feature_extraction", feature_extraction)
sys.modules.setdefault("sklearn.feature_extraction.text", text)
sys.modules.setdefault("sklearn.metrics", metrics)
sys.modules.setdefault("sklearn.metrics.pairwise", pairwise)
from hermes.assistant import engine
from hermes.assistant.state import ConversationState


def test_responder_mensagem_updates_state_and_uses_history(monkeypatch):
    captured_prompt: dict[str, str] = {}

    monkeypatch.setattr(engine, "_carregar_prompt_sistema", lambda: "PROMPT", raising=False)

    def fake_responder(prompt: str):
        captured_prompt["prompt"] = prompt
        return {"ok": True, "response": "Sou um assistente."}

    monkeypatch.setattr(engine, "gerar_resposta", fake_responder, raising=False)

    state = ConversationState(
        user_id=42,
        history=[
            {"role": "user", "content": "Quem é você?"},
            {"role": "assistant", "content": "Sou o Hermes."},
        ],
    )

    resposta = engine.responder_mensagem("E qual é o seu propósito?", state=state)

    assert resposta == "Sou um assistente."
    prompt = captured_prompt["prompt"]
    assert "PROMPT" in prompt
    assert "Contexto: responda para o usuário identificado pelo id 42." in prompt
    assert "- Usuário: Quem é você?" in prompt
    assert "- Hermes: Sou o Hermes." in prompt
    assert state.history[-2:] == [
        {"role": "user", "content": "E qual é o seu propósito?"},
        {"role": "assistant", "content": "Sou um assistente."},
    ]


def test_responder_mensagem_limits_history(monkeypatch):
    monkeypatch.setattr(engine, "_carregar_prompt_sistema", lambda: "", raising=False)
    monkeypatch.setattr(
        engine, "gerar_resposta", lambda prompt: {"ok": True, "response": "nova"}, raising=False
    )

    state = ConversationState(
        user_id=None,
        history=[{"role": "user", "content": f"old {i}"} for i in range(engine._MAX_HISTORICO)],
    )

    resposta = engine.responder_mensagem("nova pergunta", state=state)

    assert resposta == "nova"
    assert len(state.history) == engine._MAX_HISTORICO
    conteudos = [entrada["content"] for entrada in state.history]
    assert "old 0" not in conteudos and "old 1" not in conteudos
    assert conteudos[-2:] == ["nova pergunta", "nova"]
