"""Utils for writing a profile_contributors workflow to the user's repo."""

from pathlib import Path
import sys
import importlib.resources


def generate_workflow():
    """Write a profile_contributors.yml workflow file to the user's repo."""
    path = _get_workflow_path()
    _confirm_write_workflow(path)
    _write_workflow(path)

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

def _confirm_write_workflow(path_workflow):
    """Confirm the user wants the file written to the calculated location."""
    msg = "This will generate a GitHub action that will automatically run gh-profiler"
    msg += "\nwhenever someone opens a new issue or PR in your repository."
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

def _write_workflow(path_workflow):
    """Write the workflow file to the correct location."""
    # Read source file.
    path_templates = importlib.resources.files("gh_profiler") / "templates"
    path_src = path_templates / "profile_contributors.yml"
    contents = path_src.read_text()

    # Make .github/workflows dirs as needed.
    path_workflows = path_workflow.parent
    if not path_workflows.exists():
        path_workflows.mkdir(parents=True)

    # Write profile_contributors.yml file.
    path_workflow.write_text(contents)
