"""Test the workflows that gh-profiler generates."""

import subprocess
from pathlib import Path
import shlex

import pytest


path_templates = Path(__file__).parents[2] / "src" / "gh_profiler" / "templates"
        
@pytest.mark.parametrize(
    "path_workflow",
    [
        path_templates / "profile_contributors.yml",
        path_templates / "profile_contributors_link_only.yml",
    ]
)
def test_zizmor_checks(path_workflow):
    """Test that zizmor checks pass for generated workflows."""
    cmd = f"zizmor {path_workflow.as_posix()} --offline --quiet"
    cmd_parts = shlex.split(cmd)
    output = subprocess.run(cmd_parts, capture_output=True, text=True)

    assert "No findings to report. Good job!" in output.stdout
