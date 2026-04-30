"""Utils not really specific to GitHub."""

import shlex
import subprocess


def run_cmd(cmd):
    """Run a subprocess command, return stdout."""
    cmd_parts = shlex.split(cmd)
    output_obj = subprocess.run(cmd_parts, capture_output=True)
    return output_obj.stdout.decode()
