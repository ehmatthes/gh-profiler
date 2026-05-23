"""Benchmark real-world performance.

This is meant to help avoid the tool taking longer and longer to run as it
does more analysis.

Analysis should take no time compared to fetching data. Fetching data should
not take meaningfully longer than the slowest single fetching call.

This tool helps prove that these claims are holding true.

Goal: Make ~5 runs against a real-world target, rejecting any runs where
the GH CLI hangs. Report minimum and median time, and full list of times.
Minimum time is meaningful, max is not. That's more likely to indicate gh
API response time issues.

Usage:
$ uv run developer_resources/benchmark.py
$ uv run developer_resources/benchmark.py <target>
"""

from time import perf_counter
import shlex
import subprocess
import statistics
import sys

# Benchmark against any target.
try:
    target = sys.argv[1]
except IndexError:
    target = "ehmatthes"

cmd = f"uv run gh-profiler {target}"
cmd_parts = shlex.split(cmd)

run_times = []
while len(run_times) < 5:
    ts_start = perf_counter()

    output_obj = subprocess.run(cmd_parts, capture_output=True)

    ts_end = perf_counter()
    run_time = round((ts_end - ts_start), 2)

    if run_time < 5:
        run_times.append(run_time)
        print(f"Successful run: {run_time} sec")
    else:
        print(f"Failed run: {run_time} sec")

# Report results.
summary = f"\nMedian time: {statistics.median(run_times)} sec"
summary += f"\nMinimum time: {min(run_times)} sec"
summary += f"\nAll times: {run_times}"

print(summary)