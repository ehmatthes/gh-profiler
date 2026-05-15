"""Utils for writing a profile_contributors workflow to the user's repo."""

from pathlib import Path
import sys


def generate_workflow():
    """Write a profile_contributors.yml workflow file to the user's repo."""
    path = _get_workflow_path()
    print(f"Writing to: {path.as_posix()}...")

def _get_workflow_path():
    """Determine the path we'd like to write the workflow to."""
    path_cwd = Path.cwd()

    # If the path we want exists and there's no conflict, move forward.
    path_workflows = path_cwd / ".github" / "workflows"
    path_pc_workflow = path_workflows / "profile_contributors.yml"
    if path_workflows.exists() and not path_pc_workflow.exists():
        return path_pc_workflow

    # If the workflow already exists, inform and exit.
    if path_pc_workflow.exists():
        msg = f"The file {path_pc_workflow.as_posix()} already exists."
        msg += "\nIf you want to generate this file, please delete the existing file and run this command again."
        sys.exit(msg)

    # If there's a .git directory, we can move forward.
    path_git_dir = path_cwd / ".git"
    if not path_git_dir.exists() or not path_git_dir.is_dir():
        msg = f"Could not find a .git dir at: {path_cwd.as_posix()}"
        msg += "\nAre you in the root directory of your project's repository?"
        sys.exit(msg)
