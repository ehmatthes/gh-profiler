"""One place to store all data about the targeted repo."""

from dataclasses import dataclass


@dataclass(slots=True)
class RepoData:
    """The main data store for what we need to know about a targeted repo.

    """
    owner: str = ""
    repo_name: str = ""


repo_data = RepoData()
