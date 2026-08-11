# Datetime & UUID
from datetime import datetime
from uuid import UUID

# Pydantic
from pydantic.networks import IPvAnyAddress

# Application
from base import BaseSchema  # Base
from enums import Communication  # Enums
from schemas.tag import TagRead  # Schema for Tag
from schemas.group import GroupRead  # Schema for Group


# Create Host
class HostCreate(BaseSchema):
    name: str
    description: str

    ipv4: IPvAnyAddress | None = None
    dns: str | None = None
    port: int

    api_key: str
    communication: Communication

    is_active: bool

    group_id: UUID
    tag_ids: list[UUID]


# Update Host
class HostUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None

    ipv4: IPvAnyAddress | None = None
    dns: str | None = None
    port: int | None = None

    api_key: str | None = None
    communication: Communication | None = None

    is_active: bool | None = None

    group_id: UUID | None = None
    tag_ids: list[UUID] | None = None


# Read Host
class HostRead(BaseSchema):
    id: UUID

    name: str
    description: str

    ipv4: IPvAnyAddress
    dns: str
    port: int

    api_key: str
    communication: Communication

    is_active: bool
    agent_availability: bool

    group: GroupRead
    tags: list[TagRead]

    created_at: datetime
    updated_at: datetime
