"""
Módulo DNS: zonas y registros del cliente. Envuelve /v1/dns/*.

Los diccionarios que entran y salen de este módulo usan exactamente los
mismos nombres de campo que el JSON de la API (rrtype, rrtypename,
primaryns, defaultttl, etc.) — no se convierten a otro estilo.
"""

from urllib.parse import quote


class Dns:
    def __init__(self, api):
        self.api = api

    def list_zones(self) -> dict:
        """Lista las zonas (dominios) del cliente. GET /v1/dns/zone

        -> {"status", "zones": [Zone], "count"}
        """
        resp = self.api.get("/v1/dns/zone")
        return resp.decode()

    def get_zone(self, key_or_domain) -> dict:
        """Obtiene una zona (por clave numérica o por nombre de dominio) junto
        con sus registros. GET /v1/dns/zone/{key|domain}

        -> {"status", "zone": Zone, "records": [Record], "ns": [str]}
        """
        resp = self.api.get(f"/v1/dns/zone/{quote(str(key_or_domain), safe='')}")
        return resp.decode()

    def add_zone(self, name: str) -> dict:
        """Crea una nueva zona. POST /v1/dns/zone

        -> {"status", "key", "name"}
        """
        resp = self.api.post("/v1/dns/zone", {"name": name})
        return resp.decode()

    def add_record(self, zone_key: int, record: dict) -> dict:
        """Agrega un registro a una zona. POST /v1/dns/zone/{key}/record

        record: {"name", "rrtype", "ttl", "data", "priority"?, "weight"?, "port"?, "tag"?}
        -> {"status", "key", "zone"}
        """
        resp = self.api.post(f"/v1/dns/zone/{zone_key}/record", record)
        return resp.decode()

    def update_record(self, record_key: int, fields: dict) -> dict:
        """Modifica un registro existente. PUT /v1/dns/record/{key}

        fields: diccionario con SOLO los campos a cambiar
          (name, ttl, data, priority, weight, port, tag, status) — los que
          no incluyas no se tocan.
        -> {"status", "key"}
        """
        resp = self.api.put(f"/v1/dns/record/{record_key}", fields)
        return resp.decode()

    def delete_record(self, record_key: int) -> dict:
        """Elimina un registro. DELETE /v1/dns/record/{key}

        -> {"status", "key"}
        """
        resp = self.api.delete(f"/v1/dns/record/{record_key}")
        return resp.decode()

    def delete_zone(self, zone_key: int) -> dict:
        """Elimina una zona y todos sus registros. DELETE /v1/dns/zone/{key}

        -> {"status", "key", "name"}
        """
        resp = self.api.delete(f"/v1/dns/zone/{zone_key}")
        return resp.decode()
