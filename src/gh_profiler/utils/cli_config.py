"""One place to store all CLI options passed by the user."""

from dataclasses import dataclass


@dataclass(slots=True)
class CLIConfig:
    """The main place to store options that are passed in the gh-profiler cmd.
    """

    # If target is a URL, store that here.
    url: str = ""
    num_targets: int | None = None

    issues: bool | None = None
    back: bool | None = None

    redact: bool | None = None
    table_only: bool | None = None


cli_config = CLIConfig()
