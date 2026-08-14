"""
🚧 Stub — calca el contrato del SDK de Go (github.com/webability/webability-go/mail).

La capa de transporte (WaApi en __init__.py) ya está implementada; falta
conectar send()/status() a WaApi.request()/get()/post(). Las firmas ya están
fijadas para que la implementación futura sea un port directo de mail.go, no
un rediseño.
"""

from dataclasses import dataclass, field
from typing import Any


class QueueStatus:
    """Estados posibles de queue_status en SendResult y StatusResult."""

    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    ERROR = "error"


@dataclass
class Address:
    email: str
    name: str = ""


@dataclass
class Recipient:
    email: str
    name: str = ""
    vars: dict[str, Any] = field(default_factory=dict)


@dataclass
class SendRequest:
    """Campos para POST /v1/mail/send."""

    from_: Address
    to: Recipient
    subject: str = ""
    html: str = ""
    text: str = ""
    # Si viene (no vacío), es el id de una plantilla ya registrada y activa
    # en templates_template bajo la cuenta que autentica el request — el
    # servidor arma el correo con esa plantilla en vez de subject/html/text
    # (que se ignoran si template viene). La personalización usa las vars de
    # `to`, igual que en el envío ad-hoc. El servidor valida que la plantilla
    # exista y esté activa ANTES de encolar el correo: si no, send() lanza
    # ApiError con el error de la API (códigos 3025/3026), no un envío
    # "pending" fallido.
    template: str = ""
    tags: list[str] = field(default_factory=list)
    track_opens: bool = False
    track_clicks: bool = False
    # Si es True, el servidor espera (hasta ~20s) el resultado real del envío
    # antes de responder, en vez de responder de inmediato con
    # queue_status="pending". Ver Mail.send().
    wait_send: bool = False


@dataclass
class SendResult:
    """Respuesta de Mail.send()."""

    status: str
    queue_key: int
    queue_status: str
    to: str
    error_detail: str = ""


@dataclass
class StatusResult:
    """Respuesta de Mail.status()."""

    status: str
    queue_key: int
    queue_status: str
    error_detail: str = ""


class Mail:
    def __init__(self, api):
        self.api = api

    def send(self, req: SendRequest) -> SendResult:
        """Envía un correo a un solo destinatario. POST /v1/mail/send

        🚧 Pendiente de implementar (ver mail.go para el contrato de referencia).
        """
        raise NotImplementedError("Mail.send() aún no está implementado en el SDK de Python.")

    def status(self, queue_key: int) -> StatusResult:
        """Consulta el estatus real de un envío hecho con send().
        GET /v1/mail/status/{queue_key}

        🚧 Pendiente de implementar (ver mail.go para el contrato de referencia).
        """
        raise NotImplementedError("Mail.status() aún no está implementado en el SDK de Python.")
