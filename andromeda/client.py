# Logging
import logging

# UUID
import uuid

# Types
from typing import Any

# Requests
import httpx

# Application
from enums.communication import CommunicationType  # Enum
from models import Host  # App Models

# Logger
logger = logging.getLogger("andromeda.client")


class AgentClient:
    def __init__(self, host: Host, timeout: float = 10.0):
        self.host = host
        self.timeout = timeout
        self.base_url = self._build_base_url()
        self.headers = {
            "X-API-KEY": host.api_key,
            "User-Agent": "Andromeda-Cloud-Collector/1.0",
        }

    def _build_base_url(self) -> str:
        address = (
            self.host.ipv4
            if self.host.communication == CommunicationType.IPV4
            else self.host.dns
        )

        if not address:
            raise ValueError(
                f"Host {self.host.id} missing target address for mode {self.host.communication}"
            )

        return f"http://{address}:{self.host.port}/api"

    async def ping(self) -> bool:
        url = f"{self.base_url}/ping"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(url, headers=self.headers)

                return res.status_code == 200
        except Exception as e:
            logger.debug("Ping failed for host %s (%s): %s", self.host.name, url, e)

            return False

    async def pull_metrics(self, limit: int = 100) -> list[dict[str, Any]]:
        url = f"{self.base_url}/pull"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(
                    url, headers=self.headers, params={"limit": limit}
                )

                if res.status_code == 200:
                    return res.json()

                logger.error(
                    "Pull returned status %d for host %s",
                    res.status_code,
                    self.host.name,
                )

                return []
        except Exception as e:
            logger.error("Failed to pull metrics from host %s: %s", self.host.name, e)

            return []

    async def acknowledge_metrics(self, metric_ids: list[uuid.UUID]) -> bool:
        if not metric_ids:
            return True

        url = f"{self.base_url}/ack"
        payload = {"metric_ids": [str(m_id) for m_id in metric_ids]}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, headers=self.headers, json=payload)

                return res.status_code == 200
        except Exception as e:
            logger.error(
                "Failed to acknowledge metrics for host %s: %s", self.host.name, e
            )

            return False
