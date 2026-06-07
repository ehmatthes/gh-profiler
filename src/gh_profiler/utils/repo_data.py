"""One place to store all data about the targeted repo."""

from dataclasses import dataclass
from datetime import datetime as dt, timezone


@dataclass(slots=True)
class RepoData:
    """The main data store for what we need to know about a targeted repo.

    """
    owner: str = ""
    repo_name: str = ""


@dataclass(slots=True)
class PRData:
    """Data store for a PR we're targeting."""
    # Raw info
    pr_num: int | None = None
    author: str = ""
    title: str = ""
    url: str = ""
    
    closed_state: str = ""
    created_at: dt | None = None


    # Processed info
    summary: str = ""


repo_data = RepoData()