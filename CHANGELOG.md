Changelog: gh-profiler
===

For inspiration and motivation, see [Keep a CHANGELOG](https://keepachangelog.com/en/0.3.0/).

0.x - Initial releases
---

These initial releases have usable behavior, but may have some rough edges for some users and use cases.

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
