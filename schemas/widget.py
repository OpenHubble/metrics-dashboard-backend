# Datetime & UUID
from datetime import datetime
from uuid import UUID

# Pydantic
from pydantic import Field

# Application
from base import BaseSchema  # Base
from enums.widget import ChartType  # Enums


# Grid Schema
class GridPosSchema(BaseSchema):
    x: int = 0
    y: int = 0
    w: int = 6
    h: int = 4


# Create Widget
class WidgetCreate(BaseSchema):
    title: str
    chart_type: ChartType = ChartType.LINE
    collector: str
    metric_item: str
    grid_pos: GridPosSchema = Field(default_factory=GridPosSchema)
    host_id: UUID


# Update Widget
class WidgetUpdate(BaseSchema):
    title: str | None = None
    chart_type: ChartType | None = None
    collector: str | None = None
    metric_item: str | None = None
    grid_pos: GridPosSchema | None = None
    host_id: UUID | None = None


# Read Widget
class WidgetRead(WidgetCreate):
    id: UUID

    page_id: UUID

    created_at: datetime
    updated_at: datetime
