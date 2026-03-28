from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

StatusLiteral = Literal["draft", "active", "paused", "completed"]


class Project(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    status: StatusLiteral = "draft"
    srid: int = 4674
    description: str | None = None


class Job(BaseModel):
    id: str | None = None
    project_id: str
    code: str = Field(min_length=1, max_length=80)
    status: StatusLiteral = "draft"


class Layer(BaseModel):
    id: str | None = None
    project_id: str
    name: str = Field(min_length=1, max_length=120)
    visible: bool = True
    source: str = "workspace"


class UserProfile(BaseModel):
    id: str | None = None
    full_name: str = Field(min_length=1, max_length=120)
    email: str
    role: str
