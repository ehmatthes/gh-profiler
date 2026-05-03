"""Utils not really specific to GitHub."""
import os
import shlex
import subprocess


def run_cmd(cmd, env=None):
    """Run a subprocess command, return stdout."""
    cmd_parts = shlex.split(cmd)
    output_obj = subprocess.run(cmd_parts, capture_output=True, env=env or os.environ)
    return output_obj.stdout.decode()
