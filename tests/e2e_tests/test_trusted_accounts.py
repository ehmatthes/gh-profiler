"""Tests the trusted accounts behavior."""

from pathlib import Path
import tomllib

import pytest

import e2e_utils


@pytest.fixture()
def ensure_config():
    """Make sure config is what we expect for these tests."""
    path = Path(__file__).parents[2] / "gh-profiler.toml"
    assert path.exists(), "A gh-profiler.toml config file is required for this test."

    with path.open("rb") as f:
        config = tomllib.load(f)

    assert "ehmatthes" in config["trusted_contributors"]
    assert "dependabot[bot]" in config["trusted_bots"]


def test_trusted_contributor(ensure_config):
    """Test that a user in the trusted_contributors list is not profiled."""
    cmd = "uv run gh-profiler ehmatthes"
    output = e2e_utils.run_with_timeout(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    assert output == "User ehmatthes is a trusted contributor.\n"

def test_trusted_bot(ensure_config):
    """Test that a bot in the trusted_bot list is not profiled."""
    cmd = "uv run gh-profiler 'dependabot[bot]'"
    output = e2e_utils.run_with_timeout(cmd)

    if output == "":
        msg = "Output was empty, which may indicate a gh timeout rather than a problem with the code."
        pytest.fail(msg)

    assert output == "User dependabot[bot] is a trusted contributor.\n"
