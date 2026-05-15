"""Main CLI entry point for gh-profiler."""

import sys

import click

from . import gh_profiler
from .utils import cli_utils
from .utils.profile_data import profile_data as pdata


@click.command()
@click.argument("target", required=False)
@click.version_option(package_name="gh-profiler")
@click.option("--concise", is_flag=True, help="Show concise output; one flag per category.")
@click.option(
    "--generate-workflow",
    is_flag=True,
    help="Generate a workflow that will automatically run `gh-profiler --concise` for every new PR and issue.",
)
@click.option("--redact", is_flag=True, help="Redact identifying information.")
def main(target, concise, generate_workflow, redact):
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
    _validate_command(target, concise, generate_workflow, redact)

    # Parse CLI options.
    pdata.concise = concise
    pdata.redact = redact
    pdata.generate_workflow = generate_workflow

    # If --generate-workflow was passed, go straight to that work.
    if generate_workflow:
        gh_profiler.main()
        sys.exit()

    # If the main argument is an integer, process the PR/issue number.
    # Otherwise, assume it's the username.
    try:
        pr_issue_num = int(target)
    except ValueError:
        # target is a username.
        pdata.username = target
        gh_profiler.main()
    else:
        # Target is a PR or an issue number.
        cli_utils.process_pr_issue_num(pr_issue_num)
        gh_profiler.main()

def _validate_command(target, concise, generate_workflow, redact):
    """Validate arguments that were passed in the CLI call."""

    # If target is not passed, --generate-workflow must be passed.
    if not target and not generate_workflow:
        msg = "You must either include a target, or the --generate-workflow option."
        msg += "\nA target can be a username, or PR/issue number."
        sys.exit(msg)

    # If target is passed, --generate-workflow can not be passed.
    if target and generate_workflow:
        msg = "Please either include a target or --generate-workflow, but not both."
        sys.exit(msg)
