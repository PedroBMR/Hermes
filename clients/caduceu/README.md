# Caduceu Client

This client interacts with a Hermes server for recording ideas and asking
questions. It loads configuration from `config.yaml` and uses a push-to-talk
style workflow.

## Configuration

Edit `config.yaml` to match your environment:

```yaml
server: "http://localhost:8000"  # Base URL of the Hermes server
token: "replace-with-secret-token"  # API token for authentication
device_id: "cozinha"  # Identifier for this client device
```

## Usage

Run the client directly:

```bash
python clients/caduceu/client.py
```

Press **Enter** to trigger the push-to-talk prompt, then type your idea.
The client sends a `POST /ideas` request with JSON data `{user, title, body}`
and headers `X-Token` and `X-Device-Id`.

The server response is expected to include a `source` field like
`caduceu_<device_id>`, for example `caduceu_cozinha`.

After submitting an idea you may optionally enter a prompt to
`POST /ask`. The response is spoken aloud using the offline
[`pyttsx3`](https://pyttsx3.readthedocs.io/) text‑to‑speech engine.
