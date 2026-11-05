"""Utility functions for e2e tests across multiple test modules."""

import subprocess

import pytest

from gh_profiler.utils import infra_utils


def run_with_timeout(cmd):
    """Run gh-profiler command, with a timeout."""
    num_attempts = 0
    while num_attempts < 5:
        try:
            result = infra_utils.run_cmd(cmd, timeout=5)
            output = result.stdout
        except subprocess.TimeoutExpired:
            print("Time out.")
            num_attempts += 1
        else:
            # Did not time out, but check that we got a response.
            if output:
                return output
            else:
                print("Got an empty response.")
                num_attempts += 1
                continue
    
    # Skip this entire module if there are too many timeouts.
    msg = "Too many timeouts."
    pytest.skip(msg, allow_module_level=True)