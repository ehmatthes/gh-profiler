"""Tests for running subprocess commands."""

import sys

from gh_profiler.utils import infra_utils


def _exe():
    """Path to the current interpreter, in a form shlex.split won't mangle.

    shlex treats backslashes as escape characters, so a Windows path needs
    forward slashes here.
    """
    return sys.executable.replace("\\", "/")


def test_run_cmd_handles_non_utf8_output():
    """A subprocess that emits non-UTF-8 bytes should not crash.

    gh on Windows can print text in the local codepage, which isn't valid
    UTF-8. We replace the offending bytes rather than raising.
    """
    cmd = f'{_exe()} -c "import sys; sys.stdout.buffer.write(bytes([0x61, 0x85]))"'
    result = infra_utils.run_cmd(cmd)

    assert result.returncode == 0
    assert "\ufffd" in result.stdout


def test_run_cmd_captures_stderr():
    """Errors on stderr should be captured, not lost."""
    cmd = f"{_exe()} -c \"import sys; sys.stderr.write('boom')\""
    result = infra_utils.run_cmd(cmd)

    assert "boom" in result.stderr
