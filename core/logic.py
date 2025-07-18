def interpretar_comando(texto: str) -> str:
    """Interpretar comandos simples enviados pelo usuário."""
    if "ideia" in texto:
        return "Ideia registrada (simulação)."
    elif "lembrete" in texto:
        return "Lembrete criado (simulação)."
    else:
        return "Comando não reconhecido."
