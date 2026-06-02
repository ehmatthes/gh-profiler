"""Utils not really specific to GitHub."""

import os
import shlex
import subprocess
from dataclasses import dataclass


DEFAULT_ENV = {
    **os.environ,
    "CLICOLOR_FORCE": "0",
    "NO_COLOR": "1",
}

@dataclass
class CommandResult:
    """Decoded subprocess output."""
    stdout: str
    stderr: str
    returncode: int


def run_cmd(cmd, env=DEFAULT_ENV, timeout=None):
    """Run a subprocess command, return CommandResult instance."""
    cmd_parts = shlex.split(cmd)
    output_obj = subprocess.run(cmd_parts, capture_output=True, env=env, timeout=timeout)

    return CommandResult(
        stdout=output_obj.stdout.decode(),
        stderr=output_obj.stderr.decode(),
        returncode=output_obj.returncode,
    )
