# SQLAlchemy
from sqlalchemy import Enum as SQLEnum, ForeignKey, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

# UUID
import uuid

# Application
from base import BaseModel
from enums.widget import ChartType


class Widget(BaseModel):
    __tablename__ = "widgets"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        nullable=False,
    )
    chart_type: Mapped[ChartType] = mapped_column(
        SQLEnum(ChartType),
        nullable=False,
        default=ChartType.LINE,
    )
    collector: Mapped[str] = mapped_column(
        nullable=False,
    )
    metric_item: Mapped[str] = mapped_column(
        nullable=False,
    )
    # Layout configuration for dashboard grid positioning ({ "x": 0, "y": 0, "w": 6, "h": 4 })
    grid_pos: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"x": 0, "y": 0, "w": 6, "h": 4},
    )

    # Foreign Keys
    page_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    host_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("hosts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    page: Mapped["Page"] = relationship(
        "Page",
        back_populates="widgets",
    )
    host: Mapped["Host"] = relationship(
        "Host",
        back_populates="widgets",
    )
