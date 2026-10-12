"""Thin async client for the Jullix gateway local HTTP API.

Every endpoint exposed by the gateway firmware (v3.1.0, ``innovoltus-jullix-v2``)
is wrapped here so the rest of the integration never has to build URLs or deal
with transport concerns. Read methods return the decoded JSON (or ``None`` on
error); write methods return the decoded JSON response and raise
``JullixApiError`` on a transport/HTTP failure so callers can surface it.

The local API uses HTTP Basic auth; credentials are optional (many LAN
deployments leave the API open) and only sent when configured.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10


class JullixApiError(Exception):
    """Raised when a request to the gateway fails."""


class JullixApiClient:
    """Wraps the Jullix gateway's local REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._host = host.rstrip("/")
        self._timeout = timeout
        self._auth = (
            aiohttp.BasicAuth(username, password or "")
            if username
            else None
        )

    # -- transport ---------------------------------------------------------

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Any | None = None,
        data: Any | None = None,
        params: dict | None = None,
        raise_on_error: bool = False,
    ) -> Any:
        url = f"{self._host}{endpoint}"
        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.request(
                    method,
                    url,
                    json=json,
                    data=data,
                    params=params,
                    auth=self._auth,
                )
                response.raise_for_status()
                if response.content_type == "application/json":
                    return await response.json()
                text = await response.text()
                return text or None
        except Exception as err:  # noqa: BLE001 - normalise all transport errors
            _LOGGER.debug("Jullix %s %s failed: %s", method, endpoint, err)
            if raise_on_error:
                raise JullixApiError(f"{method} {endpoint} failed: {err}") from err
            return None

    async def _get(self, endpoint: str, params: dict | None = None) -> Any:
        return await self._request("GET", endpoint, params=params)

    async def get(self, endpoint: str, params: dict | None = None) -> Any:
        """Public GET for an arbitrary endpoint (used by the coordinator)."""
        return await self._get(endpoint, params=params)

    async def _post(self, endpoint: str, json: Any | None = None, data: Any | None = None) -> Any:
        return await self._request(
            "POST", endpoint, json=json, data=data, raise_on_error=True
        )

    # -- EMS live telemetry ------------------------------------------------

    async def get_ems(self, kind: str) -> Any:
        """``kind`` is one of meter, solar, battery, charger, plug."""
        return await self._get(f"/api/ems/{kind}")

    async def get_meter(self) -> Any:
        return await self.get_ems("meter")

    async def get_solar(self) -> Any:
        return await self.get_ems("solar")

    async def get_battery(self) -> Any:
        return await self.get_ems("battery")

    async def get_charger(self) -> Any:
        return await self.get_ems("charger")

    async def get_plug(self) -> Any:
        return await self.get_ems("plug")

    # -- DSMR / P1 ---------------------------------------------------------

    async def get_dsmr_status(self) -> Any:
        return await self._get("/api/dsmr/status")

    async def get_dsmr_settings(self) -> Any:
        return await self._get("/api/dsmr/settings")

    async def set_dsmr_settings(self, settings: dict) -> Any:
        return await self._post("/api/dsmr/settings", json=settings)

    # -- Inverter ----------------------------------------------------------

    async def get_inverter_models(self, filter: str | None = None) -> Any:
        params = {"filter": filter} if filter else None
        return await self._get("/api/inverter/models", params=params)

    async def get_inverter_model(self, inverter_id: str) -> Any:
        return await self._get(f"/api/inverter/model/{inverter_id}")

    async def get_inverter_status(self, inverter_id: str | None = None) -> Any:
        endpoint = (
            f"/api/inverter/status/{inverter_id}"
            if inverter_id
            else "/api/inverter/status"
        )
        return await self._get(endpoint)

    async def set_inverter_model(self, inverter_id: str, model: dict) -> Any:
        return await self._post(f"/api/inverter/model/{inverter_id}", json=model)

    # -- Modbus-TCP --------------------------------------------------------

    async def get_modbustcp_status(self, device_id: str | None = None) -> Any:
        endpoint = (
            f"/api/modbustcp/status/{device_id}"
            if device_id
            else "/api/modbustcp/status"
        )
        return await self._get(endpoint)

    async def get_modbustcp_models(self) -> Any:
        return await self._get("/api/modbustcp/models")

    async def get_modbustcp_config(self) -> Any:
        return await self._get("/api/modbustcp/config")

    async def set_modbustcp_config(self, config: dict) -> Any:
        return await self._post("/api/modbustcp/config", json=config)

    # -- SunSpec -----------------------------------------------------------

    async def get_sunspec_status(self) -> Any:
        return await self._get("/api/sunspec/status")

    async def get_sunspec_models(self) -> Any:
        return await self._get("/api/sunspec/models")

    async def get_sunspec_config(self) -> Any:
        return await self._get("/api/sunspec/config")

    async def set_sunspec_config(self, config: dict) -> Any:
        return await self._post("/api/sunspec/config", json=config)

    # -- Charger / Plug control -------------------------------------------

    async def get_charger_status(self) -> Any:
        return await self._get("/api/charger/status")

    async def set_charger_config(self, config: dict) -> Any:
        return await self._post("/api/charger/config", json=config)

    async def get_plug_status(self) -> Any:
        return await self._get("/api/plug/status")

    async def set_plug_config(self, config: dict) -> Any:
        return await self._post("/api/plug/config", json=config)

    async def reset_plug(self) -> Any:
        return await self._post("/api/plug/reset", data="true")

    # -- Networking --------------------------------------------------------

    async def get_wifi_status(self) -> Any:
        return await self._get("/api/wifi/status")

    async def get_wifi_scan(self) -> Any:
        return await self._get("/api/wifi/scan")

    async def get_wifi_settings(self) -> Any:
        return await self._get("/api/wifi/settings")

    async def set_wifi_settings(self, settings: dict) -> Any:
        return await self._post("/api/wifi/settings", json=settings)

    async def get_ethernet_status(self) -> Any:
        return await self._get("/api/ethernet/status")

    async def get_mdns_scan(self) -> Any:
        return await self._get("/api/mdns/scan")

    async def network_ping(self, target: str | None = None) -> Any:
        params = {"target": target} if target else None
        return await self._get("/api/network/ping", params=params)

    # -- Comms (peripheral pairing bus) -----------------------------------

    async def get_comms_status(self) -> Any:
        return await self._get("/api/comms/status")

    async def set_comms_mode(self, mode: Any) -> Any:
        return await self._post("/api/comms/mode", json={"mode": mode})

    async def comms_config(
        self, channel: int = 1, ssid: str | None = None, password: str | None = None
    ) -> Any:
        payload: dict[str, Any] = {"channel": channel}
        if ssid is not None:
            payload["ssid"] = ssid
        if password is not None:
            payload["password"] = password
        return await self._post("/api/comms/config", json=payload)

    async def comms_join(self, mac: str, pubkey: str, pair: Any) -> Any:
        return await self._post(
            "/api/comms/join", json={"mac": mac, "pubkey": pubkey, "pair": pair}
        )

    async def comms_reset(self) -> Any:
        return await self._post("/api/comms/reset", data="true")

    # -- System / firmware / logging --------------------------------------

    async def get_dashboard_system(self) -> Any:
        return await self._get("/api/dashboard/system")

    async def get_system_settings(self) -> Any:
        return await self._get("/api/system/settings")

    async def set_system_settings(self, settings: dict) -> Any:
        return await self._post("/api/system/settings", json=settings)

    async def get_setup_status(self) -> Any:
        return await self._get("/api/setup/status")

    async def get_connection(self) -> Any:
        return await self._get("/api/connection/get")

    async def get_firmware_info(self) -> Any:
        return await self._get("/api/firmware/info")

    async def firmware_update(self, force: bool = False) -> Any:
        endpoint = "/api/firmware/update/force" if force else "/api/firmware/update"
        return await self._post(endpoint)

    async def check_restart(self) -> Any:
        return await self._get("/api/check_restart")

    # -- Historical logger -------------------------------------------------

    async def get_logger_day(self, year: int, month: int, day: int) -> Any:
        return await self._get(f"/api/logger/day/{year}/{month}/{day}")

    async def get_logger_month(self, year: int, month: int) -> Any:
        return await self._get(f"/api/logger/month/{year}/{month}")

    async def get_logger_year(self, year: int) -> Any:
        return await self._get(f"/api/logger/year/{year}")
