import unittest
from pathlib import Path
from unittest.mock import patch

from hermes.assistant import engine
from hermes.assistant.state import ConversationState
from hermes.core import prompts


class AssistantEngineTests(unittest.TestCase):
    def test_carregar_prompt_sistema_ler_arquivo(self):
        prompts._SYSTEM_PROMPT_CACHE = None
        prompt = engine.carregar_prompt_sistema()
        conteudo_arquivo = Path(prompts.SYSTEM_PROMPT_PATH).read_text(encoding="utf-8")
        self.assertEqual(prompt, conteudo_arquivo)
        self.assertIsInstance(prompt, str)

    @patch("hermes.assistant.engine.gerar_resposta")
    def test_responder_mensagem_sem_historico(self, mock_gerar_resposta):
        mock_gerar_resposta.return_value = {"ok": True, "response": " resposta gerada "}
        state = ConversationState(user_id=None, history=[])

        resposta = engine.responder_mensagem("Olá, Hermes", state)

        self.assertEqual(resposta, "resposta gerada")
        mock_gerar_resposta.assert_called_once()
        prompt_enviado = mock_gerar_resposta.call_args[0][0]
        self.assertIn("Usuário: Olá, Hermes", prompt_enviado)
        self.assertIn("Hermes:", prompt_enviado)
        self.assertEqual(
            state.history,
            [
                {"role": "user", "content": "Olá, Hermes"},
                {"role": "assistant", "content": "resposta gerada"},
            ],
        )

    @patch("hermes.assistant.engine.gerar_resposta")
    def test_responder_mensagem_limita_historico(self, mock_gerar_resposta):
        mock_gerar_resposta.return_value = {"ok": True, "response": "nova resposta"}
        historico_existente = [
            {"role": "user", "content": f"old {i}"} for i in range(engine._MAX_HISTORICO)
        ]
        state = ConversationState(user_id=None, history=historico_existente)

        engine.responder_mensagem("pergunta recente", state)

        self.assertEqual(len(state.history), engine._MAX_HISTORICO)
        conteudos = [entrada["content"] for entrada in state.history]
        self.assertNotIn("old 0", conteudos)
        self.assertNotIn("old 1", conteudos)
        self.assertEqual(conteudos[-2:], ["pergunta recente", "nova resposta"])

    @patch("hermes.assistant.engine.coletar_contexto_ideias")
    @patch("hermes.assistant.engine.gerar_resposta")
    def test_responder_mensagem_inclui_contexto_ideias(
        self, mock_gerar_resposta, mock_coletar_contexto
    ):
        mock_gerar_resposta.return_value = {"ok": True, "response": "com contexto"}
        mock_coletar_contexto.return_value = {
            "contexto": "Contexto de ideias relevante",
            "ideias": ["ideia"],
        }
        state = ConversationState(user_id=42, history=[])

        resposta = engine.responder_mensagem("Pergunta sobre ideias", state)

        self.assertEqual(resposta, "com contexto")
        prompt_enviado = mock_gerar_resposta.call_args[0][0]
        self.assertIn("Contexto: responda para o usuário identificado pelo id 42.", prompt_enviado)
        self.assertIn("Contexto de ideias relevante", prompt_enviado)
        self.assertIn("Pergunta sobre ideias", prompt_enviado)
        self.assertEqual(mock_coletar_contexto.call_args[0], (42, "Pergunta sobre ideias"))
        self.assertEqual(
            state.history[-2:],
            [
                {"role": "user", "content": "Pergunta sobre ideias"},
                {"role": "assistant", "content": "com contexto"},
            ],
        )

    @patch("hermes.assistant.engine.coletar_contexto_ideias")
    @patch("hermes.assistant.engine.gerar_resposta")
    def test_responder_mensagem_sem_contexto_irrelevante(
        self, mock_gerar_resposta, mock_coletar_contexto
    ):
        mock_gerar_resposta.return_value = {"ok": True, "response": "olá"}
        state = ConversationState(user_id=123, history=[])

        resposta = engine.responder_mensagem("Quem é você?", state)

        self.assertEqual(resposta, "olá")
        mock_coletar_contexto.assert_not_called()

    def test_deve_usar_contexto_ideias_heuristica(self):
        self.assertTrue(engine._deve_usar_contexto_ideias("Preciso de ideias para um projeto"))
        self.assertTrue(
            engine._deve_usar_contexto_ideias("Quais são minhas prioridades e planos?")
        )
        self.assertFalse(engine._deve_usar_contexto_ideias("Conte uma piada"))


if __name__ == "__main__":
    unittest.main()
