Changelog: gh-profiler
===

For inspiration and motivation, see [Keep a CHANGELOG](https://keepachangelog.com/en/0.3.0/).

0.x - Initial releases
---

These initial releases have usable behavior, but may have some rough edges for some users and use cases.

### Unreleased

#### External changes

- Redacts user's org info.
- Fixes broken usage against PRs and issue numbers, since 0.6.6.
- Supports bulk processing of recently opened PRs.

#### Internal changes

- When parsing PR and issue numbers, treat `run_cmd()` result as an object, not a string.
- E2e test for PR and issue number as target.
- Uses a `cli_config` object, to store CLI args and behavioral settings off the pdata object.
- Adds `httpx2`, for checking if provided URL is reachable.
- In `test_all.sh`, run e2e and live user tests in parallel. ~14s -> ~5s.

### 0.7.1

#### External changes

- Checks for slightly shorter auth message, because `gh auth status` emits a different message on Windows.

#### Internal changes

- NA

### 0.7.0

#### External changes

- Identifies PRs and issues in three categories: against repos the user owns, against orgs the user is publicly associated with, and against external orgs. All analysis for evaluating flags is based on the user's activity in external repos.
- Reports orgs the user is publicly associated with.
- README emphasizes concise usage first, before showing full output.

#### Internal changes

- Ensure no doubled blank lines in summary.
- More consistent separation of fetching, parsing, and evaluating user activity data.

### 0.6.7

#### External changes

- Bumped PR activity thresholds slightly, so extremely low volume PR activity does not trip flags. ie, having one or two PRs closed does not raise any flags, even though the ratio of closed to opened might be above the threshold.
- Also fixes unreported bug where overall number of PRs opened was being checked against external PR threshold.

#### Internal changes

- NA

### 0.6.6

#### External changes

- Users who are not authenticated on one account but are authenticated on another account should be able to run gh-profiler without running into an authentication failure issue.

#### Internal changes

- The `run_cmd()` utility returns a `CommandResult` instance instead of just stdout. The result instance has `stdout`, `stderr`, and `returncode` fields.
- If the auth check does not pass when looking at stdout, it looks at stderr. If the "Logged in to GitHub" message is in either of those, execution proceeds.

### 0.6.5

#### External changes

- Reports number of PRs opened, regardless of how many. (Previously did not report specifics under 10 PRs.)
- Differentiates between PRs opened against repos the user owns, vs external repos.
- Added note to README about not flagging good-faith behavior.

#### Internal changes

- Includes `developer_resources/test_actual_users.py`, which runs tests against a series of actual users.
  - Targets users in `actual_users.toml`, which is stored outside this repo so as not to call attention to any specific users.
  - Targets users who should only ever return green flags, and users who are expected to raise at least one yellow or red flag.
  - Includes a template data file in `developer_resources/actual_users.toml`.
- Implements better timeouts and checks for empty API responses in e2e tests.

### 0.6.4

#### External changes

- If a user has 0 new PRs or issues, the profile flags are set to green. This is important, for example, for people who have left GitHub and scrubbed their profile info, but not deleted their account. They haven't opened any PRs or issues, but they don't want to see yellow or red flags if someone runs gh-profiler against their account.
- Supports `-v`, `--verbose`. When passed, this prints the rationale for adjust flags. This can expand to dump explanations for any decisions made in the analysis work.

#### Internal changes

- NA

### 0.6.3

#### External changes

- Full summaries have the same section headers as concise summaries.
- Messages are more consistent across categories, ie no usernames in detail lines.
- More consistent alignment throughout summary.

#### Internal changes

- Simplified tests to make them less fragile. For example, only test lines relevant to the test, not the entire summary (except initial full summary test).

#### External changes

### 0.6.2

#### External changes

- When a user has a newer account, but no other red/yellow flags, their account age and overall profile flags are set green. This avoids discouraging newer contributors who are engaging in no problematic behaviors.

#### Internal changes

- Includes unit tests for combinations of flags. This is a good start for implementing more complex evaluation rules, without accidentally contradicting earlier behavior.

### 0.6.1

#### External changes

- Start documenting talks and discussions of this project in README.
- Much clearer output when the user's gh CLI tool is not authenticated.

#### Internal changes

- Run tests in CI via tox.
- Small helper script `test_all.sh` to run unit tests, then all e2e tests.
- Benchmarking script to ensure consistent performance over time.
    - Benchmarking script has a 5-second cutoff for API calls that seem to hang.
- Check the output of `gh auth status` explicitly.
    - This is done in a batched mode, so it does not impact performance.
    - The call to fetch the target user's profile dict is batched now as well.
    - Performance is improved by about 0.25 seconds against my own profile, close to 0.10 seconds on users with more activity.

### 0.6.0

#### External changes

- gh-profiler runs meaningfully faster, by parallelizing the calls that fetch external data.

#### Internal changes

- Basic e2e tests for full and --concise runs. E2e tests are flaky because they make actual gh API calls. E2e tests must be run explicitly, ie `uv run pytest tests/e2e_tests -k full`.
- Uses `ThreadPoolExecutor` to parallelize the fetching calls. We shouldn't add many more calls, but this should mean a few more quick calls are essentially free. The call to fetch issue activity is the slowest, so any fetch significantly faster than that should add not add to execution time in any meaningful way.
- Supports `--benchmark-fetch`, which lets us easily benchmark just the fetching block.

### 0.5.1

#### External changes

- Commas in account ages over 999 days.
- PR search is restricted to public activity.
- Thresholds upped for problematic behavior related to opening multiple identical issues. For example opening an issue on the wrong repo, closing it, and opening an identical issue on the correct repo should not raise any flags. Old thresholds: 0 green, 1-3 yellow, 4+ red. New: 0-3 green, 4-5 yellow, 6+ red.
- Shows all social media accounts present in user's GH profile.
- Works for Python 3.10. (Was failing on a timestamp-parsing library.)

#### Internal changes

- Manually parse account created_at timestamp. `datetime.fromisoformat()` doesn't work as generally in Python <3.11.

### 0.5.0

#### External changes

- Supports `--generate-workflow`. This writes a `.github/workflows/profile_contributors.yml` file that runs `gh-profiler --concise` any time a new PR or issue is opened on the user's repository. The output is written as a comment on the new PR or issue.

#### Internal changes

- Whenever someone opens a new PR or issue on this repository, the workflow profile_contributors.yml automatically runs gh-profiler against the author. The output is written as a comment on the PR or issue.
- Target is optional in CLI, but validation requires it if not running `--generate-workflow`.

### 0.4.0

#### External changes

- Supports `--concise` flag, which generates a more condensed summary that only shows one line for each major section: profile, recent PR activity, and recent issue activity.

#### Internal changes
---

- Simplified CLI argument parsing.

### 0.3.5

#### External changes

- If target is a PR or issue number, shows the number and title in summary.

#### Internal changes

- cli util sets `pdata.username` directly.
- `ProfileData` uses slots to lock down fields (not values). This ensures that `ProfileData` is an accurate listing of all fields that can be filled in about the user.

### 0.3.4

#### External changes

- Support `--redact`, which replaces primary identifying information with "<redacted>".

#### Internal changes

- Simpler main file. Calls one function to get data, and one function to process data.
- Move test fixtures to conftest file.

### 0.3.3

#### External changes

- Increased exception handling, should catch some failed gh calls.
- Fewer external calls, should run faster by about 1-2 seconds.

#### Internal changes

- Makes one call to get recent PR activity instead of three.
- Check for authentication at first external gh call, rather than separate call just to check authentication.

### 0.3.2

#### External changes

- Fix `usename` -> `username` bug when user hasn't opened any recent issues.
- Show green flag when user hasn't opened recent issues.

#### Internal changes

- Simpler test for user with no recent issues; just test snippets of output.

### 0.3.1

#### External changes

- Fixes bug where overall issues flag was not taking into account repeated issue titles.

#### Internal changes

- Simpler logic for processing overall issues flag.

### 0.3.0

#### External changes

- Summarize recent public issue activity.
    - Look for multiple issues closed as `NOT_PLANNED`.
    - Look for multiple issues filed with identical titles, usually across multiple repositories.

#### Internal changes

- Strip ASCII color codes from gh output. We're only analyzing that text, so we didn't need it anyway. #28

### 0.2.5

#### External changes

- Simplify output: fewer blank lines, don't print individual lines for empty profile fields.

#### Internal changes

- Build summary string and then print that string, instead of using a series of print calls.
- Helper functions to build sections of summary.
- Initial unit tests for `_get_summary()`.
- Simpler logic for generating summary sections.

### 0.2.4

#### External changes

- Invalid usernames no longer cause a crash on older versions of the `gh` CLI.

### 0.2.3

#### External changes

- Supports `--version` flag.
- Added MIT license.

### 0.2.2

#### External changes

- Fix bug with yellow flag for account age. (#19)

### 0.2.1

#### External changes

- If status is 404 when getting initial profile information, exit with invalid GitHub username message.
- @hugovk was right, `created_at` is a better check than `status`. `status` not present for valid users. (#11)
- Ensure that gh CLI tool is authenticated before running. (#12)
- Use gh's default remote, rather than parsing output of `git remote -v` and taking first result. (#13)
- If a user has opened fewer than 10 PRs recently, don't analyze PR activity. Fixes zero division error bug from #14.
- Clarify gh CLI unauthenticated message to state that the API may have hung.

#### Internal changes

- Move CLI helper functions to utils module.

### 0.2.0

#### External changes

- Makes sure gh tool is installed.
- Show a `--help` message.
- Works from a GitHub username, PR number, or issue number.
- Clarify issue when PR activity call hangs.
- Simplified README.

#### Internal changes

- Use Click for CLI.

### 0.1.1

#### External changes

- Revise description.
- Require Python >= 3.10, not 3.14.
- Add usage instructions to README.
- Document release process.

#### Internal changes

- NA

### 0.1.0

Initial release. Shows a summary including username, account age, profile information, and recent PR activity. Uses green/ yellow/ red flags.
