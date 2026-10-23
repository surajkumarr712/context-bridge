"""Pydantic models describing project data at the API boundary."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

ProjectName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]


class ProjectCreate(BaseModel):
    """Information a client must send to create a project."""

    name: ProjectName
    description: str = Field(default="", max_length=500)


class Project(ProjectCreate):
    """Complete project returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def normalize_created_at_to_utc(cls, value: datetime) -> datetime:
        """Guarantee that API timestamps always include an explicit UTC zone."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

