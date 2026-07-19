"""Domain entities: plain Python dataclasses with no dependency on FastAPI,
SQLAlchemy, or Pydantic. This is the innermost layer of the architecture."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class Project:
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.ACTIVE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Project name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
