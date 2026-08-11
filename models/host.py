# SQLAlchemy
from sqlalchemy import Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# UUID
import uuid

# Application
from base import BaseModel  # Base


# Host Model
class Host(BaseModel):
    __tablename__ = "hosts"

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        nullable=False,
    )
    ipv4: Mapped[str] = mapped_column(
        nullable=True,
    )
    dns: Mapped[str] = mapped_column(
        nullable=True,
    )
    port: Mapped[int] = mapped_column(
        nullable=False,
    )
    api_key: Mapped[str] = mapped_column(
        nullable=False,
    )
    communication: Mapped[str] = mapped_column(
        nullable=False,
    )
    agent_availability: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("groups.id"),
        index=True,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="hosts",
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="hosts",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="host_tags",
        back_populates="hosts",
    )
    metrics: Mapped[["Metric"]] = relationship(
        "Metric",
        back_populates="host",
    )
