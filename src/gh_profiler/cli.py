"""Main CLI entry point for gh-profiler."""

import click

from . import gh_profiler
from .utils import cli_utils


@click.command()
@click.argument("target")
@click.version_option(package_name="gh-profiler")
def main(target):
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

    # If the main argument is an integer, process the PR/issue number.
    # Otherwise, assume it's the username.
    try:
        pr_issue_num = int(target)
    except ValueError:
        gh_profiler.main(target)

    # The user provided a PR/issue number. Get the relevant username, then
    # call gh_profiler.main().
    username = cli_utils.get_username(pr_issue_num)
    gh_profiler.main(username)
