# SQLAlchemy
from sqlalchemy.orm import Session

# Logging
import logging

# UUID
import uuid

# Types
from typing import Any

# Datetime
from datetime import datetime

# Application
from models import Host  # App Models
from andromeda.models import Metric  # Andromeda Models

# Logger
logger = logging.getLogger("andromeda.service")


def update_host_availability(
    db: Session,
    host_id: uuid.UUID,
    available: bool,
) -> None:
    host = db.get(Host, host_id)

    if host and host.agent_availability != available:
        host.agent_availability = available

        db.commit()


def save_agent_metrics(
    db: Session,
    host_id: uuid.UUID,
    raw_metrics: list[dict[str, Any]],
) -> list[uuid.UUID]:
    if not raw_metrics:
        return []

    processed_ids: list[uuid.UUID] = []

    for item in raw_metrics:
        try:
            agent_metric_id = uuid.UUID(item["id"])
            collected_at = datetime.fromisoformat(item["collected_at"])

            metric = Metric(
                host_id=host_id,
                agent_metric_id=agent_metric_id,
                collector=item["collector"],
                collected_at=collected_at,
                metrics=item["metrics"],
            )

            db.add(metric)
            processed_ids.append(agent_metric_id)
        except Exception as e:
            logger.error("Malformed metric record skipped for host %s: %s", host_id, e)

    db.commit()

    return processed_ids
