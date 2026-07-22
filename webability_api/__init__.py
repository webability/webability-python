"""
Cliente base para la API de WebAbility (https://api.webability.info).

Firma cada request con HMAC-SHA256 (headers X-WA-Client, X-WA-Timestamp,
X-WA-Digest) — mismo esquema que el SDK de Go
(github.com/webability/webability-go/wa). El Token nunca viaja en el
request: solo se usa localmente para calcular el digest.

Sin dependencias externas: usa únicamente la librería estándar
(urllib, hmac, hashlib, json, time).
"""

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.webability.info"


def build_message(method: str, path: str, timestamp: str, client_id: str) -> str:
    """Construye el mensaje canónico a firmar: "{METODO}|{PATH}|{TIMESTAMP}|{CLIENTID}".

    path debe ser la ruta del request sin query string.
    """
    return f"{method}|{path}|{timestamp}|{client_id}"


class ApiError(Exception):
    """Error devuelto por la API en formato {status, code, message}."""

    def __init__(self, status_code: int, code, message: str):
        super().__init__(f"wa api error {code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message


class Response:
    """Respuesta cruda de un request a la API."""

    def __init__(self, status_code: int, headers, body: bytes):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def decode(self):
        """Decodifica el cuerpo JSON de la respuesta."""
        if not self.body:
            return {}
        return json.loads(self.body.decode("utf-8"))


class WaApi:
    def __init__(self, client_id: str, token: str, base_url: str = DEFAULT_BASE_URL):
        self.client_id = client_id
        self.token = token
        self.base_url = base_url

    def digest(self, message: str) -> str:
        """Retorna hex(HMAC-SHA256(self.token, message))."""
        mac = hmac.new(self.token.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        return mac.hexdigest()

    def request(self, method: str, path: str, body=None) -> Response:
        """Firma y envía un request HTTP a la API.

        path debe ser la ruta absoluta (ej: "/v1/dns/zone"), sin el host y
        sin query string. body, si no es None, se codifica como JSON y se
        envía como cuerpo del request.
        """
        timestamp = str(int(time.time()))
        message = build_message(method, path, timestamp, self.client_id)

        headers = {
            "X-WA-Client": self.client_id,
            "X-WA-Timestamp": timestamp,
            "X-WA-Digest": self.digest(message),
        }

        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                return Response(resp.status, dict(resp.headers), resp.read())
        except urllib.error.HTTPError as err:
            raw = err.read()
            result = Response(err.code, dict(err.headers or {}), raw)
            try:
                parsed = result.decode()
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed = {}
            if parsed.get("message"):
                raise ApiError(err.code, parsed.get("code"), parsed["message"]) from err
            raise Exception(f"error HTTP {err.code}") from err
        except urllib.error.URLError as err:
            raise Exception(f"enviando request: {err.reason}") from err

    def get(self, path: str) -> Response:
        """Envía un GET a path."""
        return self.request("GET", path)

    def post(self, path: str, body=None) -> Response:
        """Envía un POST a path con body codificado en JSON."""
        return self.request("POST", path, body if body is not None else {})

    def put(self, path: str, body=None) -> Response:
        """Envía un PUT a path con body codificado en JSON."""
        return self.request("PUT", path, body if body is not None else {})

    def delete(self, path: str) -> Response:
        """Envía un DELETE a path."""
        return self.request("DELETE", path)
