# Contribuindo

Agradecemos seu interesse em contribuir com o Hermes!

## Fluxo de Pull Request

1. Faça um fork deste repositório e crie um branch para sua feature ou correção.
2. Garanta que testes e linters passem antes de enviar suas alterações.
3. Abra um Pull Request descrevendo claramente suas modificações.

## Ambiente de desenvolvimento

Instale o pacote em modo editável e as ferramentas de desenvolvimento:

```bash
pip install -e .
pip install pre-commit
pre-commit install
```

## Testes

Execute a suíte de testes completa:

```bash
python -m unittest discover -s tests
```

## Linters

Execute os linters localmente antes de commitar:

```bash
pre-commit run --files <arquivos_modificados>
```

Obrigado por ajudar a melhorar o projeto!
