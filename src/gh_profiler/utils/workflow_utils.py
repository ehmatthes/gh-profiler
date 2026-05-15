"""Utils for writing a profile_contributors workflow to the user's repo."""

from pathlib import Path


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


