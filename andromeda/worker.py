# Asyncio
import asyncio

# Logging
import logging

# UUID
import uuid

# Types
from typing import NoReturn

# Application
from database.database import session as db_session_factory  # Database
from base import BaseSchema
from models import Host  # Models

# Andromeda
from andromeda.client import AgentClient
from andromeda.service import save_agent_metrics, update_host_availability

# Logger
logger = logging.getLogger("andromeda.worker")

# Cap concurrent host processing tasks
MAX_CONCURRENT_HOST_WORKERS = 50


class HostData(BaseSchema):
    id: uuid.UUID


async def process_host(host_data: HostData, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        with db_session_factory() as db:
            host = db.get(Host, host_data.id)

            if not host or not host.is_active:
                return

            client = AgentClient(host)

            is_alive = await client.ping()
            update_host_availability(db, host.id, is_alive)

            if not is_alive:
                return

            raw_metrics = await client.pull_metrics(limit=100)
            if not raw_metrics:
                return

            saved_metric_ids = save_agent_metrics(db, host.id, raw_metrics)

            if saved_metric_ids:
                ack_success = await client.acknowledge_metrics(saved_metric_ids)

                if ack_success:
                    logger.info(
                        "Synced %d metrics from host %s",
                        len(saved_metric_ids),
                        host.name,
                    )


async def run_andromeda_cycle(semaphore: asyncio.Semaphore) -> None:
    with db_session_factory() as db:
        host_ids = db.query(Host.id).where(Host.is_active == True).all()
        host_payloads = [HostData(id=h_id) for (h_id,) in host_ids]

    if not host_payloads:
        return

    tasks = [process_host(h_data, semaphore) for h_data in host_payloads]
    await asyncio.gather(*tasks, return_exceptions=True)


async def start_andromeda_worker(poll_interval: int = 10) -> NoReturn:
    logger.info("Starting Andromeda Metric Collector Worker...")
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_HOST_WORKERS)

    while True:
        try:
            await run_andromeda_cycle(semaphore)
        except Exception as e:
            logger.error("Error in Andromeda worker cycle: %s", e, exc_info=True)

        await asyncio.sleep(poll_interval)
