"""Main CLI entry point for gh-profiler."""

import sys
from urllib.parse import urlparse

import click

from . import gh_profiler
from .utils import cli_utils
from .utils.profile_data import profile_data as pdata
from .utils.repo_data import repo_data
from .utils.cli_config import cli_config


@click.command()
@click.argument("target", required=False)
@click.version_option(package_name="gh-profiler")
@click.option("--concise", is_flag=True, help="Show concise output; one flag per category.")
@click.option("-n", "--num-targets", default=10, help="Preview: How many PRs to review?")
# @click.option("--issues", is_flag=True, help="Profile contributors of issues rather than PRs.")
@click.option("--back", is_flag=True, help="Look back over recently merged and closed PRs.")
@click.option(
    "--generate-workflow",
    is_flag=True,
    help="Generate a workflow that will automatically run `gh-profiler --concise` for every new PR and issue.",
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose output, including explanations for decisions about flags.")
@click.option("--redact", is_flag=True, help="Redact identifying information.")
@click.option("--benchmark-fetch", is_flag=True, help="Benchmark the code that fetches external data.")
def main(target, concise, num_targets, back, generate_workflow, verbose, redact, benchmark_fetch):
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

    \b
    Bulk concise profiling of most recently opened PRs:
    $ gh-profiler <repo-url>    # 10 most recent PRs
    $ gh-profiler <repo-url> -n 3
    """
    _validate_command(target, concise, generate_workflow, verbose, redact, benchmark_fetch)

    # Parse CLI options.
    pdata.concise = concise
    pdata.verbose = verbose
    pdata.redact = redact
    pdata.benchmark_fetch = benchmark_fetch
    pdata.generate_workflow = generate_workflow

    # If --generate-workflow was passed, go straight to that work.
    if generate_workflow:
        gh_profiler.main()
        sys.exit()

    # Check if we're processing a repo URL.
    if "github.com" in target:
        cli_config.url = target
        _parse_repo_options(num_targets, back)
        _parse_repo_info(target)
        gh_profiler.profile_url()

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

def _validate_command(target, concise, generate_workflow, verbose, redact, benchmark_fetch):
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

def _parse_repo_options(num_targets, back):
    """Get options relevant to targeting a repo URL."""
    cli_config.num_targets = num_targets
    # cli_config.issues = issues
    cli_config.back = back

def _parse_repo_info(target):
    """Parse info about the repo from the target.

    Looking for owner and repo name.
    """
    parsed_url = urlparse(target)
    url_parts = parsed_url.path.split("/")
    repo_data.owner = url_parts[1]
    repo_data.repo_name = url_parts[2]
