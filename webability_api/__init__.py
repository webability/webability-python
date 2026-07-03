"""
🚧 En construcción.

Cliente base para la API de WebAbility (https://api.webability.info).
Seguirá el mismo esquema de autenticación que el cliente Go de referencia
(github.com/webability/webability-go): ClientID + Token, firma HMAC-SHA256 en los
headers X-WA-Client / X-WA-Timestamp / X-WA-Digest. El Token nunca viaja
en el request.
"""


class WaApi:
    def __init__(self, client_id: str, token: str, base_url: str = "https://api.webability.info"):
        self.client_id = client_id
        self.token = token
        self.base_url = base_url
