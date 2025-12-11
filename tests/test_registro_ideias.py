import unittest
from pathlib import Path
from unittest.mock import patch

from hermes.core import app
from hermes.core.registro_ideias import analisar_ideia_com_llm


class TestRegistrarIdeiaComLLM(unittest.TestCase):
    def test_registra_ideia_usa_llm_e_salva(self):
        usuario_id = 1
        titulo = "Titulo"
        descricao = "Descricao"
        url = "http://mock"
        model = "fake-model"

        with (
            patch(
                "hermes.core.registro_ideias.gerar_resposta",
                return_value={
                    "ok": True,
                    "response": "Tema: X\nResumo: Y\nTags: a,b",
                },
            ) as mock_llm,
            patch("hermes.core.app.add_idea") as mock_add,
            patch(
                "hermes.core.registro_ideias.PROMPT_PATH",
                Path(__file__).resolve().parents[1]
                / "prompts"
                / "resumo_classificar.md",
            ),
            patch("builtins.print"),
        ):
            resposta = app.registrar_ideia(
                usuario_id, titulo, descricao, usar_llm=True, url=url, model=model
            )

        mock_llm.assert_called_once()
        prompt = mock_llm.call_args.args[0]
        self.assertIn(titulo, prompt)
        self.assertIn(descricao, prompt)
        self.assertEqual(mock_llm.call_args.kwargs["url"], url)
        self.assertEqual(mock_llm.call_args.kwargs["model"], model)

        mock_add.assert_called_once_with(
            usuario_id,
            titulo,
            descricao,
            source=url,
            llm_summary="Y",
            llm_topic="X",
            tags="a,b",
        )
        self.assertEqual(
            resposta,
            {
                "id": mock_add.return_value,
                "llm_response": "Tema: X\nResumo: Y\nTags: a,b",
                "llm_summary": "Y",
                "llm_topic": "X",
                "tags": "a,b",
            },
        )

    def test_falha_llm_gera_excecao(self):
        usuario_id = 1
        titulo = "Titulo"
        descricao = "Descricao"

        with (
            patch(
                "hermes.core.registro_ideias.gerar_resposta",
                return_value={"ok": False, "message": "erro"},
            ) as mock_llm,
            patch("hermes.core.app.add_idea") as mock_add,
            patch(
                "hermes.core.registro_ideias.PROMPT_PATH",
                Path(__file__).resolve().parents[1]
                / "prompts"
                / "resumo_classificar.md",
            ),
            patch("builtins.print"),
        ):
            with self.assertRaises(RuntimeError):
                app.registrar_ideia(usuario_id, titulo, descricao, usar_llm=True)

        mock_llm.assert_called_once()
        mock_add.assert_not_called()


def test_modificar_prompt_reflete_no_texto(tmp_path):
    temp_prompt = tmp_path / "resumo_classificar.md"
    temp_prompt.write_text("Primeiro {titulo} - {descricao}", encoding="utf-8")

    with patch("hermes.core.registro_ideias.PROMPT_PATH", temp_prompt):
        with patch(
            "hermes.core.registro_ideias.gerar_resposta",
            return_value={"ok": True, "response": ""},
        ) as mock_llm:
            analisar_ideia_com_llm("T1", "D1")
            primeiro = mock_llm.call_args_list[-1].args[0]

        temp_prompt.write_text("Segundo {titulo} - {descricao}", encoding="utf-8")
        with patch(
            "hermes.core.registro_ideias.gerar_resposta",
            return_value={"ok": True, "response": ""},
        ) as mock_llm:
            analisar_ideia_com_llm("T2", "D2")
            segundo = mock_llm.call_args_list[-1].args[0]

    assert "Primeiro" in primeiro
    assert "Segundo" in segundo
    assert primeiro != segundo


if __name__ == "__main__":
    unittest.main()
