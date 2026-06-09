"""Utils for writing a profile_contributors workflow to the user's repo."""

from pathlib import Path
import sys
import importlib.resources

import click


def generate_workflow():
    """Write a profile_contributors.yml workflow file to the user's repo."""
    workflow_choice = _get_workflow_choice()

    path = _get_workflow_path()
    _confirm_write_workflow(path, workflow_choice)
    _write_workflow(path, workflow_choice)
    _show_closing_message(path)

def _get_workflow_choice():
    """Prompt the user for the kind of workflow they'd like to generate.

    They can choose to write profile output as a comment on PRs and issues, 
    or just write a link to the Actions log that contains the profile output.
    """
    msg = "Would you like to write the concise profile output as a comment on each new PR/issue,"
    msg += "\nor just write a link to the Actions log containing the profile output?"
    msg += "\n\n1) Write concise profile output as a comment."
    msg += "\n2) Only write the link to the Actions log."
    msg += "\n\nWorkflow type"

    response = ""
    while response not in ("1", "2"):
        response = click.prompt(msg)

        if response not in ("1", "2"):
            msg_invalid = "\nPlease enter 1 or 2."
            click.echo(msg_invalid)

    if response == "1":
        return "concise_profile"
    else:
        return "link_only"


def _get_workflow_path():
    """Determine the path we'd like to write the workflow to."""
    path_workflows = Path.cwd() / ".github" / "workflows"
    path_pc_workflow = path_workflows / "profile_contributors.yml"

    # If the workflows directory exists but the workflow file does not, no conflicts.
    if path_workflows.exists() and not path_pc_workflow.exists():
        return path_pc_workflow

    # If the workflow already exists, inform and exit.
    if path_pc_workflow.exists():
        msg = f"The file {path_pc_workflow.as_posix()} already exists."
        msg += "\nIf you want to regenerate this file, please delete the existing file and run this command again."
        sys.exit(msg)

    path_git_dir = Path.cwd() / ".git"

    # If there's no .git directory, we probably shouldn't proceed.
    if not path_git_dir.exists() or not path_git_dir.is_dir():
        msg = f"Could not find a .git dir at: {path_cwd.as_posix()}"
        msg += "\nAre you in the root directory of your project's repository?"
        sys.exit(msg)

    # No conflicts found. Note that .github/workflows/ may not exist.
    return path_pc_workflow

def _confirm_write_workflow(path_workflow, workflow_choice):
    """Confirm the user wants the file written to the calculated location."""
    if workflow_choice == "concise_profile":
        msg = "\n\nThis will generate a GitHub action that will automatically run gh-profiler"
        msg += "\nwhenever someone opens a new issue or PR in your repository. The profile"
        msg += "\noutput will be written as a comment on the issue or PR."
    else:
        msg = "\n\nThis will generate a GitHub action that will automatically run gh-profiler"
        msg += "\nwhenever someone opens a new issue or PR in your repository. The profile"
        msg += "\noutput will be written to the Actions log. A link to the Actions log"
        msg += "\nwill be written as a comment on the issue or PR."

    msg += "\n\nThe workflow will be written at the following location:"
    msg += f"\n  {path_workflow.as_posix()}"
    msg += "\n\nAre you sure you want to do this? (y/n) "

    confirmed = ""
    while confirmed.lower() not in ("y", "yes", "n", "no"):
        confirmed = input(msg)
        if confirmed.lower() in ("y", "yes"):
            return
        elif confirmed.lower() in ("n", "no"):
            sys.exit()

def _write_workflow(path_workflow, workflow_choice):
    """Write the workflow file to the correct location."""
    # Read source file.
    path_templates = importlib.resources.files("gh_profiler") / "templates"
    if workflow_choice == "concise_profile":
        path_src = path_templates / "profile_contributors.yml"
    else:
        path_src = path_templates / "profile_contributors_link_only.yml"
    contents = path_src.read_text()

    # Make .github/workflows dirs as needed.
    path_workflows = path_workflow.parent
    if not path_workflows.exists():
        path_workflows.mkdir(parents=True)

    # Write profile_contributors.yml file.
    path_workflow.write_text(contents)

def _show_closing_message(path):
    """Workflow was written, describe next steps."""
    msg = "\nThe new workflow file was written:"
    msg += f"\n  {path.as_posix()}"
    msg += "\n\nTo start seeing profiles when new issues and PRs are opened:"
    msg += "\n- Commit the workflow file to your main branch."
    msg += "\n- Push your main branch to GitHub."
    msg += "\n- Make sure Actions are enabled on your project."
    msg += "\n- Open a new issue, and make sure a comment appears with a profile of your account."
    msg += "\n\nIf you don't see a comment right away, look under the Actions tab and see if there's an obvious issue."
    msg += "\nIf it's still not working, please open an issue on the gh-profiler repo:"
    msg += "\n  https://github.com/ehmatthes/gh-profiler/issues"

    print(msg)
