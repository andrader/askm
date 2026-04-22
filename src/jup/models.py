from enum import StrEnum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SyncMode(StrEnum):
    LINK = "link"
    COPY = "copy"


class ScopeType(StrEnum):
    USER = "user"
    LOCAL = "local"


class HarnessConfig(BaseModel):
    name: str
    global_location: str
    local_location: str


class JupConfig(BaseModel):
    scope: ScopeType = Field(default=ScopeType.USER)
    harnesses: List[str] = Field(default_factory=list)
    custom_harnesses: Dict[str, HarnessConfig] = Field(default_factory=dict)
    sync_mode: SyncMode = Field(default=SyncMode.LINK, alias="sync-mode")

    model_config = {"populate_by_name": True}

    @field_validator("scope", mode="before")
    @classmethod
    def map_global_to_user(cls, v: str) -> str:
        if v == "global":
            return "user"
        return v


class SkillSource(BaseModel):
    repo: Optional[str] = None
    source_type: str = "github"
    source_path: Optional[str] = None
    source_layout: Optional[str] = None
    category: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    version: Optional[str] = None
    source: Optional[str] = None
    last_updated: Optional[str] = None  # ISO format datetime
    last_install_date: Optional[datetime] = None


class SkillsLock(BaseModel):
    version: str = Field(default="0.0.0")
    sources: Dict[str, SkillSource] = Field(default_factory=dict)


# Pre-defined registry of harnesses based on known paths, extensible later.
# Includes support for GitHub Copilot, Claude Code, Cursor, Codex, Gemini CLI, Antigravity.
DEFAULT_HARNESSES: Dict[str, HarnessConfig] = {
    "copilot": HarnessConfig(
        name="copilot",
        global_location="~/.copilot/skills",
        local_location="./.agents/skills",
    ),
    "claude": HarnessConfig(
        name="claude",
        global_location="~/.claude/skills",
        local_location="./.agents/skills",
    ),
    "cursor": HarnessConfig(
        name="cursor",
        global_location="~/.cursor/skills",
        local_location="./.agents/skills",
    ),
    "codex": HarnessConfig(
        name="codex",
        global_location="~/.codex/skills",
        local_location="./.agents/skills",
    ),
    "gemini": HarnessConfig(
        name="gemini",
        global_location="~/.gemini/skills",
        local_location="./.agents/skills",
    ),
    "antigravity": HarnessConfig(
        name="antigravity",
        global_location="~/.gemini/antigravity/skills",
        local_location="./.agents/skills",
    ),
    ".agents": HarnessConfig(
        name=".agents",
        global_location="~/.agents/skills",
        local_location="./.agents/skills",
    ),
}
