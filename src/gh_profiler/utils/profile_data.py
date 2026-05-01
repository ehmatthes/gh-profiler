"""One place to store all data about the user."""

from dataclasses import dataclass


@dataclass
class ProfileData:
    username: str = ""

    profile_info: dict | None = None

    account_age: int = 0

    opened_count: int = 0
    merged_count: int = 0
    closed_count: int = 0

    flag_age: str = ""
    flag_merged_pr: str = ""
    flag_closed_pr: str = ""


profile_data = ProfileData()
