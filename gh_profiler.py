"""Examine a user's profile, and highlight evidence they're human or AI.

The goal is to help make quick, evidence-based decisions about how much time
to invest in reviewing PRs, and general interaction on open source projects.

Scores:
3: green
2: yellow
1: red
"""

from datetime import datetime as dt
from datetime import timezone as tz
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



# Summarize findings.
print(f"GitHub user: {gh_user}")
print(f"{flag_age} Account age: {account_age.days} days")
