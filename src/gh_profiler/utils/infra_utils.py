"""Utils not really specific to GitHub."""
import os
import shlex
import subprocess

DEFAULT_ENV = {
        **os.environ,
        'CLICOLOR_FORCE': '0',
        'NO_COLOR': '1',
    }

def run_cmd(cmd, env = DEFAULT_ENV):
    """Run a subprocess command, return stdout."""
    cmd_parts = shlex.split(cmd)
    output_obj = subprocess.run(cmd_parts, capture_output=True, env=env)
    return output_obj.stdout.decode()
