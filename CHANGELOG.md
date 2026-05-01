Changelog: gh-profiler
===

For inspiration and motivation, see [Keep a CHANGELOG](https://keepachangelog.com/en/0.3.0/).

0.x - Initial releases
---

These initial releases have usable behavior, but may have some rough edges for some users and use cases.

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
