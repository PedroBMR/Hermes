import requests

def gerar_resposta(prompt: str) -> str:
    """Enviar o prompt ao modelo local e retornar a resposta."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        dados = response.json()
        return dados.get("response", "[ERRO] Sem resposta do modelo").strip()
    except Exception as e:
        return f"[FALHA] {str(e)}"
