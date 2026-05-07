"""Main CLI entry point for gh-profiler."""

import click

from . import gh_profiler
from .utils import cli_utils
from .utils.profile_data import profile_data as pdata


@click.command()
@click.argument("target")
@click.version_option(package_name="gh-profiler")
@click.option("--redact", is_flag=True, help="Redact identifying information.")
def main(target, redact):
    """Examine a GitHub user's profile, to help quickly decide how much to invest in their contributions.

    You can target a GitHub username, or a PR/issue number from the repository you're working in.

    \b
    Usage as a tool:
    $ uvx gh-profiler ehmatthes
    $ uvx gh-profiler 8

    \b
    Usage when installing gh-profiler:
    $ gh-profiler ehmatthes
    $ python -m gh_profiler ehmatthes
      ...
    """
    # Parse CLI options.
    if redact:
        pdata.redact = True

    # If the main argument is an integer, process the PR/issue number.
    # Otherwise, assume it's the username.
    try:
        pr_issue_num = int(target)
    except ValueError:
        # target is a username.
        pdata.username = target
        gh_profiler.main()
    else:
        pdata.username = cli_utils.get_username(pr_issue_num)
        gh_profiler.main()
