from enum import StrEnum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SyncMode(StrEnum):
    LINK = "link"
    COPY = "copy"


class ScopeType(StrEnum):
    GLOBAL = "global"
    LOCAL = "local"


class JupConfig(BaseModel):
    scope: ScopeType = Field(default=ScopeType.GLOBAL)
    agents: List[str] = Field(default_factory=list)
    sync_mode: SyncMode = Field(default=SyncMode.LINK, alias="sync-mode")

    model_config = {"populate_by_name": True}


class SkillSource(BaseModel):
    repo: str
    category: Optional[str] = None
    skills: List[str] = Field(default_factory=list)


class SkillsLock(BaseModel):
    version: str = Field(default="0.0.0")
    sources: Dict[str, SkillSource] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    name: str
    global_location: str
    local_location: str


# Pre-defined registry of agents based on known paths, extensible later.
DEFAULT_AGENTS: Dict[str, AgentConfig] = {
    "gemini": AgentConfig(
        name="gemini",
        global_location="~/.gemini/skills",
        local_location="./.gemini/skills",
    ),
    "copilot": AgentConfig(
        name="copilot",
        global_location="~/.copilot/skills",
        local_location="./.copilot/skills",
    ),
    "claude": AgentConfig(
        name="claude",
        global_location="~/.claude/skills",
        local_location="./.claude/skills",
    ),
    "default": AgentConfig(
        name="default",
        global_location="~/.agents/skills",
        local_location="./.agents/skills",
    ),
}
