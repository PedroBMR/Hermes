import json
import sys
import types


# Provide a minimal 'requests' stub if the real library is unavailable.
if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    class RequestException(Exception):
        """Base exception matching requests.RequestException."""

    class ConnectionError(RequestException):
        """Simple stand-in for requests.ConnectionError."""

    class Timeout(RequestException):
        """Simple stand-in for requests.Timeout."""

    class Response:
        """Minimal Response object with just enough for tests."""

        def __init__(self) -> None:
            self.status_code = 200
            self._content = b""

        def json(self):
            return json.loads(self._content.decode())

        def raise_for_status(self):
            if not 200 <= self.status_code < 400:
                raise RequestException(f"status code: {self.status_code}")

    class HTTPAdapter:
        """HTTPAdapter placeholder; `send` is patched in tests."""

        def __init__(self, max_retries=None) -> None:
            self.max_retries = max_retries

        def send(self, request, **kwargs):  # pragma: no cover - patched in tests
            return Response()

    adapters = types.ModuleType("requests.adapters")
    adapters.HTTPAdapter = HTTPAdapter
    sys.modules["requests.adapters"] = adapters

    class Session:
        """Session placeholder using a single adapter."""

        def __init__(self) -> None:
            self._adapter = HTTPAdapter()

        def mount(self, prefix, adapter):
            self._adapter = adapter

        def post(self, *args, **kwargs):
            return self._adapter.send(None)

        def close(self) -> None:  # pragma: no cover - no-op
            pass

    requests_stub.exceptions = types.SimpleNamespace(
        RequestException=RequestException,
        ConnectionError=ConnectionError,
        Timeout=Timeout,
    )
    requests_stub.Response = Response
    requests_stub.Session = Session
    requests_stub.adapters = adapters
    sys.modules["requests"] = requests_stub

__all__ = ["requests_stub"]
