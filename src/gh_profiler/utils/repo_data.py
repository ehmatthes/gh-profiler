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
    
    merged: bool | None = None
    closed_at: dt | None = None


    # Processed info
    author_summary: str = ""
    summary: str = ""

    # User flags
    # When pdata is not a singleton, we shouldn't need to store these here.
    profile_flag: str = ""
    pr_flag: str = ""
    issue_flag: str = ""


repo_data = RepoData()