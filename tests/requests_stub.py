import sys
import types

# Provide a minimal 'requests' stub if the real library is unavailable.
if "requests" not in sys.modules:
    requests_stub = types.ModuleType("requests")

    class RequestException(Exception):
        """Base exception matching requests.RequestException."""

    class ConnectionError(RequestException):
        """Simple stand-in for requests.ConnectionError."""

    requests_stub.exceptions = types.SimpleNamespace(
        RequestException=RequestException, ConnectionError=ConnectionError
    )
    requests_stub.post = lambda *a, **k: None
    sys.modules["requests"] = requests_stub

__all__ = ["requests_stub"]
