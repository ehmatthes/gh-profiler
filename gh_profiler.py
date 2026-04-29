"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.

Scores:
3: green
2: yellow
1: red

Package, so usage can be:
$ uvx gh-profiler ehmatthes

Or, maybe from within a project:
$ uvx gh-profiler <pr-num>

Given a PR number, it finds the author of the PR and runs the profiler on that 
user?
"""

from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta
import subprocess
import sys
import shlex
import json


gh_user = sys.argv[1]

red_flag = "\U0001F534"
yellow_flag = "\U0001F7E1"
green_flag = "\U0001F7E2"

# --- Helper functions ---
def run_cmd(cmd):
    """Run a subprocess command, return stdout."""
    cmd_parts = shlex.split(cmd)
    output_obj = subprocess.run(cmd_parts, capture_output=True)
    return output_obj.stdout.decode()


# How old is the account?
cmd = f"gh api users/{gh_user} --jq '{{login, name, created_at}}'"
results = json.loads(run_cmd(cmd))
ts_created = dt.fromisoformat(results["created_at"])
account_age = dt.now(tz.utc) - ts_created

if account_age.days > 3*365:
    flag_age = green_flag
elif account_age.days > 90:
    flag_age = yellow_flag
else: 
    flag_age = red_flag


# What does recent PR activity look like?
from urllib.parse import quote

cutoff = (dt.now(tz.utc) - timedelta(days=21)).date().isoformat()
base_query = f"author:{gh_user} is:pr created:>={cutoff}"

opened_cmd = (
    f'gh api "search/issues?q={quote(base_query)}" --jq .total_count'
)
merged_cmd = (
    f'gh api "search/issues?q={quote(base_query + " is:merged")}" --jq .total_count'
)
closed_cmd = (
    f'gh api "search/issues?q={quote(base_query + " is:closed -is:merged")}" --jq .total_count'
)

opened_count = int(run_cmd(opened_cmd).strip())
merged_count = int(run_cmd(merged_cmd).strip())
closed_count = int(run_cmd(closed_cmd).strip())

ratio_merged = merged_count / opened_count
ratio_closed = closed_count / opened_count

if ratio_closed > 0.5:
    flag_closed_pr = red_flag
elif ratio_closed > 0.15:
    flag_closed_pr = yellow_flag
else:
    flag_closed_pr = green_flag

flag_merged_pr = None
if ratio_merged > 0.5:
    flag_merged_pr = green_flag


# How much of the profile is filled out?
# email? website? social?

# Summarize findings.
print(f"\nGitHub user: {gh_user}")
print(f"  {flag_age} Account age: {account_age.days} days")

if opened_count >= 10:
    # Only show merged if it's a good sign.
    if flag_merged_pr == green_flag:
        print(f"  {flag_merged_pr} {merged_count} of {opened_count} PRs have been merged in the last 21 days.")
    print(f"  {flag_closed_pr} {closed_count} of {opened_count} PRs have been closed without merging in the last 21 days.")
else:
    print(f"  {gh_user} has opened fewer than 10 PRs in the last 21 days.")
print("")
