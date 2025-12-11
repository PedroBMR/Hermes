import logging
from pathlib import Path

from hermes.core import prompts


def reset_cache(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(prompts, "SYSTEM_PROMPT_PATH", path)
    monkeypatch.setattr(prompts, "_SYSTEM_PROMPT_CACHE", None)


def test_carregar_prompt_sistema_retorna_conteudo(monkeypatch, tmp_path):
    prompt_file = tmp_path / "assistant_system.md"
    prompt_file.write_text("conteudo do prompt", encoding="utf-8")
    reset_cache(monkeypatch, prompt_file)

    resultado = prompts.carregar_prompt_sistema()

    assert resultado == "conteudo do prompt"


def test_carregar_prompt_sistema_usando_cache(monkeypatch, tmp_path):
    prompt_file = tmp_path / "assistant_system.md"
    prompt_file.write_text("primeiro conteudo", encoding="utf-8")
    reset_cache(monkeypatch, prompt_file)

    primeira_leitura = prompts.carregar_prompt_sistema()
    prompt_file.write_text("segundo conteudo", encoding="utf-8")
    segunda_leitura = prompts.carregar_prompt_sistema()

    assert primeira_leitura == "primeiro conteudo"
    assert segunda_leitura == "primeiro conteudo"


def test_carregar_prompt_sistema_arquivo_inexistente(monkeypatch, tmp_path, caplog):
    caminho_inexistente = tmp_path / "nao_existe.md"
    reset_cache(monkeypatch, caminho_inexistente)

    with caplog.at_level(logging.ERROR):
        resultado = prompts.carregar_prompt_sistema()

    assert resultado == ""
    assert any("prompt do sistema" in registro.message for registro in caplog.records)
