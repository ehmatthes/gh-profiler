# gh-profiler: Developer Documentation

Detailed documentation for working on gh-profiler. This covers the architecture,
the data model, the flag logic, the known issues that have been fixed, Windows
specifics, and how to set up and run every part of the test suite.

For general usage of the tool, see the README.

---

## 1. What the tool does

gh-profiler is a Python CLI that examines a GitHub user's profile and recent
activity, so a maintainer can decide how much effort to invest in reviewing a
new PR or issue. It reports three color flags per area:

| Flag | Meaning |
|---|---|
| Green (🟢) | No concerns found |
| Yellow (🟡) | Some concerns found |
| Red (🔴) | Significant concerns found |

It evaluates three areas:

1. **Profile**: account age, how much profile info is filled in, social accounts.
2. **PR activity**: PRs opened against repos the user owns, repos in public
   orgs, and external repos over the last 21 days. Only *external* PRs feed the
   flags, and only merged vs. closed-without-merging ratios matter.
3. **Issue activity**: issues closed as NOT_PLANNED, and identical issue titles
   opened across multiple repos over the last 21 days (spam signal).

The tool is deliberately not meant to be a hard decision engine. It surfaces
evidence and leaves the decision to the maintainer.

## 2. How it talks to GitHub

gh-profiler does **not** use the GitHub REST API directly. It shells out to the
GitHub CLI (`gh`) for everything:

- `gh api users/<user>` for the profile.
- `gh api users/<user>/orgs` and `gh api users/<user>/social_accounts`.
- `gh api graphql ...` for recent PR and issue activity (search queries).
- `gh api graphql ... repository(...)` for bulk PR processing of a repo.
- `gh pr view` / `gh issue view` when the target is a PR or issue number.
- `gh auth status` to confirm authentication.

All shelling out goes through one function, `infra_utils.run_cmd()`, which
runs a command via `subprocess` and returns a `CommandResult` with `stdout`,
`stderr`, and `returncode`. Environment variables disable color output
(`NO_COLOR=1`, `CLICOLOR_FORCE=0`) so gh's output is always machine-readable
plain text.

`gh` must be installed and authenticated. `git` alone is not enough; being able
to push and pull does not mean `gh` is present.

## 3. Project layout

```
src/gh_profiler/
  cli.py                    # Click entry point; argument parsing, target dispatch
  gh_profiler.py            # high-level main() / profile_url() orchestration
  __main__.py               # enables python -m gh_profiler
  __init__.py               # package marker
  templates/                # GitHub Actions workflow templates (2 files)
  utils/
    profile_data.py         # ProfileData dataclass + singleton pdata
    repo_data.py            # RepoData / PRData dataclasses + repo_data singleton
    cli_config.py           # CLIConfig singleton cli_config (CLI options)
    flags.py                # emoji flag constants
    infra_utils.py          # run_cmd() subprocess wrapper, CommandResult
    profile_utils.py        # fetch + parse user profile and activity data
    analysis_utils.py       # evaluate flags from parsed data
    summary_utils.py        # render full / concise summary text
    cli_utils.py            # PR/issue-number target handling
    repo_fetching.py        # bulk fetch of a repo's PRs
    repo_analysis.py        # bulk profiling + Rich summary table
    workflow_utils.py       # write profile_contributors.yml
tests/
  unit_tests/               # fast tests with no network access
  integration_tests/        # zizmor security checks on generated workflows
  e2e_tests/                # live tests against real GitHub (network + gh)
developer_resources/        # benchmark script + manual actual-user tests
.github/workflows/          # test.yml + this repo's profiling workflow
```

## 4. Data model

### Singleton objects

The codebase uses three module-level singletons. This is a known design
decision (see "Known limitations").

- `ProfileData` (`profile_data.py`) holds everything learned about the target
  user: profile fields, orgs, social accounts, PR/issue counts, and all flags.
  It is `slots=True` so the field list is locked down. `reset_fields()` exists
  only to reuse the singleton per-PR during bulk processing; it is expected to
  disappear when `pdata` stops being a singleton.
- `RepoData` (`repo_data.py`) holds the owner and repo name when targeting a
  repo URL. `PRData` holds one PR's raw and processed info (number, author,
  title, url, merged state, plus the computed flags and summaries for bulk
  output).
- `CLIConfig` (`cli_config.py`) holds the CLI options that bulk processing
  needs (num targets, --back, redact, table-only).

### CommandResult

`infra_utils.CommandResult` is a simple dataclass with `stdout`, `stderr`, and
`returncode`. Callers should check `returncode`; the fetch layer does.

## 5. Fetch, parse, analyze, summarize

The pipeline is deliberately split into stages. Fetching is the only slow part
and is the only part that runs concurrently.

```
cli.py               parse args, decide target type
gh_profiler.py       orchestrate
profile_utils        fetch (thread pool) -> parse into pdata
analysis_utils       evaluate flags from pdata
summary_utils        render summary string
```

### Single-user flow (`gh-profiler <username>`)

1. `cli.main()` validates args and stores behavior flags on `pdata` (concise,
   verbose, redact, benchmark, generate-workflow).
2. `gh_profiler.main()` calls `profile_utils.ensure_gh()`, then
   `profile_utils.get_data()`.
3. `get_data()` submits six fetch calls to a `ThreadPoolExecutor`. The status
   call resolves first and is checked for authentication, then the remaining
   results are collected with per-call error guarding.
4. Parse functions fill `pdata`.
5. `analysis_utils.process_data()` computes flags, then a final
   `_adjust_flags()` pass applies false-positive guards.
6. `summary_utils.show_summary()` builds and prints the summary.

### Bulk flow (`gh-profiler <repo-url>`)

1. `repo_fetching.get_data()` queries the repo for its n most recent open PRs
   (or, with `--back`, closed/merged PRs).
2. `repo_analysis.process_data()` profiles each PR author, reusing profiles for
   repeat authors via `_get_cached_author_info()`.
3. Results print inline and as a rich table. With `--back`, a Merged? column is
   added.

## 6. Flag evaluation logic

### Account age (`analysis_utils._process_account_age`)

| Age | Flag |
|---|---|
| older than 3 years | Green |
| 90 days to 3 years | Yellow |
| younger than 90 days | Red |

`created_at` is parsed with `datetime.fromisoformat`, with a manual fallback
for Python 3.10's stricter handling.

### Profile info (`_process_profile_info`)

Counts filled fields among name, company, blog, location, email, bio, plus
social account URLs.

| Filled count | Flag |
|---|---|
| 0 | Red |
| 1-2 | Yellow |
| 3+ | Green |

### PR activity (`_process_pr_activity`)

Only PRs against *external* repos are analyzed. Below 4 external PRs, both PR
flags are set green (low volume should never trip flags). Otherwise:

- `ratio_closed > 0.5` -> Red flag for closed PRs. `flag_merged_pr` is None
  unless the merge ratio is healthy (never yellow or red for merged).
- The merged flag only ever shows green (PRs sitting open awaiting merge is
  normal, so a low merge ratio is not penalized).

### Issue activity (`_process_issue_activity`)

Only external issues are analyzed.

- NOT_PLANNED count: 0-3 green, 4-5 yellow, 6+ red.
- Repeated identical titles: 0-3 green, 4-5 yellow, 6+ red. Identical titles
  can be legitimate (opening on the wrong repo then the right one), which is
  why the green band is generous.

### Overall flags (`_set_overall_flags`)

An overall section flag is red if any component is red, else yellow if any is
yellow, else green.

### False-positive guard pass (`_adjust_flags`)

- `_adjust_account_age_flag`: if the account age flag is not green but
  everything else is green, the age flag is set green. This stops a brand new
  account from looking bad when the user has no other concerning activity.
- `_adjust_profile_flag_no_pr_issue_activity`: if the user has opened no recent
  PRs or issues, profile and overall-profile flags are set green. This covers
  people who scrubbed their profile but have not deleted their account.

## 7. Target types

`cli.py` routes a target to one of four paths:

| Target | Behavior |
|---|---|
| Bare username (`ehmatthes`) | Single-user profile |
| Profile URL (`https://github.com/ehmatthes`) | Same as username (`_parse_profile_url` detects owner-only URL) |
| Repo URL (`https://github.com/org/repo`) | Bulk processing of recent PRs |
| Integer (`8`) | Look up PR or issue in the current/default repo via `gh repo view` |

A repo URL is detected after the profile-URL check fails. Any target containing
`github.com` that is not a profile URL is treated as a repo URL.

The `ghost` user gets a special case everywhere: it is GitHub's stand-in for a
deleted account, and produces a single red line instead of a normal profile.

## 8. CLI options

| Option | Purpose |
|---|---|
| `-n / --num-targets` | How many PRs to review in bulk mode. Validated to 1..100. |
| `--back` | Look at recently closed/merged PRs instead of open ones. |
| `--table-only` | Bulk mode: only print the final summary table. |
| `--generate-workflow` | Write a `.github/workflows/profile_contributors.yml`. |
| `-v / --verbose` | Print rationale for flag adjustments. |
| `--redact` | Hide identifying info (for demos/screenshots). |
| `--concise` | One line per section instead of the full report. |
| `--benchmark-fetch` | Time just the network fetching block. |
| `-h / --help`, `--version` | Help and version. |

No `--issues` option exists in code; it was removed as dead wiring.

## 9. Workflow generation

`workflow_utils.generate_workflow()` writes a GitHub Actions workflow that runs
`gh-profiler --concise` on every new PR and issue author.

- The user picks whether the concise profile is posted as a comment, or only a
  link to the Actions log is posted.
- The workflow also cleans up: when the issue or PR closes, the profile comment
  and the linked Actions logs are deleted.
- The templates live in `src/gh_profiler/templates/` and are security-checked by
  the zizmor integration test.
- If `.git` is missing, the tool refuses to write a workflow.
- If the workflow file already exists, the user is asked whether to replace it.

## 10. Issues found and fixed

This section records concrete problems fixed while working on the codebase.

### 10.1 `path_cwd` NameError in workflow generation

`workflow_utils._get_workflow_path()` referenced an undefined `path_cwd`. When
`.git` was missing, the intended friendly message was replaced by a
`NameError`. Fixed to use `Path.cwd().as_posix()`.

### 10.2 `_get_repo_slug` whitespace handling

`cli_utils._get_repo_slug()` stripped its output into a local variable, but
checked and returned the unstripped `result.stdout`. Trailing whitespace leaked
into repo slugs, and a whitespace-only reply bypassed the guard. Now the
stripped value is the only one used.

### 10.3 Case-sensitive repo classification drift

Owned-repo matching used `casefold()` for PRs but plain `==` for issues.
GitHub logins are case-insensitive, so a same-user repo could be miscounted as
"external" for issue activity. Both parsers now share one helper,
`_classify_repos()`, which casefolds logins and org names everywhere.

### 10.4 Unreachable branch in `_process_pr_activity`

After the `< 4 external PRs` early return, a second `opened_count_external == 0`
check was unreachable and misleading. Removed.

### 10.5 `issueCount` vs. analyzed nodes

The issue search caps results at 100 nodes, but `issueCount` can report a
larger number. The count now reflects what was actually analyzed
(`len(nodes)`), so reported numbers always agree with the analysis. Page
graph access remains as a known limitation; real pagination is future work.

### 10.6 Fetch failures misreported as timeouts

Every parser blamed timeouts (`Couldn't get ... may have timed out`) whenever
parsing failed, hiding real errors such as 404s, rate limits, and bad tokens.
The fetch layer now checks `returncode` and surfaces gh's `stderr` via
`profile_utils._run_gh_cmd()`. A 404 on the profile call produces a clear
"GitHub user '<name>' not found."

### 10.7 Opaque thread pool failures

A single failing fetch used to crash the whole run with a raw traceback.
`get_data()` now resolves the auth status first, then collects each remaining
result with per-call error guarding, exiting with an explanatory message.

### 10.8 Dead reachability code and dead dependency

`repo_fetching._fetch_reachable()` / `_parse_reachable()` were commented out of
the flow, and the only consumer of the `httpx2` dependency was that dead code.
Both the functions and the `httpx2` dependency (and its transitive packages)
were removed. `uv lock` regenerates a clean lockfile.

### 10.9 Unused `repo_summary.py` and leftover debug

`repo_summary.show_summary()` was commented out at its only call site, so the
module was dead. Deleted. Also removed a commented-out `# breakpoint()`.

### 10.10 Half-wired CLI options

`cli_config.url`, `cli_config.issues`, a `--issues` click option, and a
commented assignment were leftovers. Nothing read them; removed.

### 10.11 `httpx2` in dependency list

See 10.8. pyproject.toml and uv.lock no longer contain `httpx2`.

### 10.12 Encodings on Windows

Two real Windows bugs:

- `infra_utils.run_cmd()` decoded gh output as strict UTF-8. On Windows gh can
  print text in the system codepage (e.g. cp1252), which is not valid UTF-8,
  raising `UnicodeDecodeError`. The decoder now uses `errors="replace"`.
- `rich` writes the emoji flags to stdout; on Windows stdout defaults to the
  system codepage and cannot hold emoji, raising `UnicodeEncodeError` when
  rendering the bulk table. The CLI now reconfigures stdout and stderr to
  UTF-8 at startup (`cli._ensure_utf8_output()`).

### 10.13 Validation of bulk count

`-n / --num-targets` only guarded the upper bound. It now also rejects values
below 1.

## 11. Windows notes

- `gh` output may not be UTF-8; the fetch layer tolerates that (10.12).
- Emoji output requires UTF-8 stdout; the CLI forces it (10.12).
- `infra_utils.run_cmd()` uses `shlex.split`; Windows paths with backslashes in
  commands can therefore be mangled, so tests avoid such paths (they substitute
  forward slashes).
- Tests that shell out (`tests/e2e_tests`, `developer_resources`) run gh through
  `uv run gh-profiler`. The `uv` executable and the `gh` executable must be on
  PATH for the spawned subprocesses.
- The e2e helper guards each run with a 20 second timeout and retries. On a
  busy machine, a run can still time out and the test will skip; see
  `run_with_timeout` in each file.

## 12. Development environment

Requirements:

- Python 3.10 or newer (`.python-version` pins 3.14 for local tooling).
- `uv` (the project uses uv for sync, lock, and running).
- The GitHub CLI `gh`, installed and authenticated (`gh auth login`).

Set up the environment:

```sh
uv sync
```

This creates `.venv` and installs the runtime and dev dependencies
(pytest, pytest-xdist, zizmor). If a fresh shell does not find `uv` or `gh`,
prepend their install directories to PATH (they get installed to Python's
Scripts dir and to the GitHub CLI install dir respectively).

Verify the environment:

```sh
uv run gh --version    # gh CLI
uv run python --version
gh auth status         # logged in? which token scopes?
```

## 13. Running tests

### Unit tests

```sh
uv run pytest tests/unit_tests
```

Fast, no network, no gh. Cover flag evaluation, summary rendering, argument
parsing, fetching/parsing helpers, repo parsing, workflow path handling, and
the subprocess wrapper.

### Integration tests

```sh
uv run pytest tests/integration_tests
```

Requires `zizmor` (a dev dependency). Runs the security checker against the
generated workflow templates. Both templates must report no findings.

### End-to-end tests

```sh
uv run pytest tests/e2e_tests
```

Requires `gh` (installed and authenticated) and network access. These make
real API calls and can be flaky by nature. They are not collected by default
(`conftest.py` uses `collect_ignore`). Tests:

- Full, concise, and redacted runs against the author's account.
- Bulk runs against https://github.com/django/django (open and --back).
- The `ghost` account special case.
- PR/issue number targets, via the default repo. The targets (#1, #3) exist in
  the upstream `ehmatthes/gh-profiler` repo, so the default repo must resolve
  there (`gh repo set-default ehmatthes/gh-profiler`). A fork without those
  PRs/issues will skip those tests.

### Live user checks and benchmark

```sh
uv run pytest developer_resources/test_actual_users.py -s
```

Runs against a set of known-green and known-problematic real users. Usernames
must be stored in a private `actual_users.toml` that lives outside the repo (the
test looks for it via the `PATH_ACTUAL_USERS` env var or
`<repo-parent>/gh-profiler_support/actual_users.toml`). A version with real
names must never be committed.

```sh
uv run developer_resources/benchmark.py
```

Times several runs against a target to watch for performance regressions.

### All local tests

```sh
./test_all.sh
```

Shell script that runs unit, e2e, and live-user tests. Works on macOS and
probably Linux; may not work on Windows.

Running only the collectible suites on any platform (recommended default):

```sh
uv run pytest
```

## 14. Known limitations

- **pdata is a global singleton.** Reused and reset per PR during bulk
  processing via `reset_fields()`. This blocks threading bulk profiling; the
  commented-out parallel path in `repo_analysis` needs a non-singleton data
  object. Until then, state must not leak across tests (fixtures reset it).
- **No pagination on activity fetches.** PR/issue activity is capped at 100
  nodes from the search API. Counts now reflect the analyzed nodes, but a very
  active user could have more activity than is inspected.
- **`--back` set differs from GitHub's UI.** The back-mode query fetches
  closed/merged PRs ordered by `UPDATED_AT` then re-sorts by `closedAt`, so the
  set of PRs shown may not match the repo's "closed" tab (documented in the
  README note).
- **e2e and live-user tests are inherently flaky.** They depend on network
  latency, gh rate limits, and live GitHub data.
- **Windows output depends on UTF-8.** The CLI forces UTF-8 stdout/stderr; on
  legacy consoles the emoji may not render even though output is well-formed.

## 15. Release process

Per README:

1. Update CHANGELOG and bump the version in pyproject.toml.
2. `uv lock`.
3. Commit all changes.
4. `git tag vX.Y.Z`.
5. `git push origin vX.Y.Z`.
6. `rm -rf dist/*`, `uv build`, `uv publish`.

## 16. Code conventions

- Keep fetch -> parse -> analyze -> present separation.
- Fetching is the only part that should touch the network, and the only part
  that runs in parallel.
- Terse output lines over verbose ones (e.g. "0 issues closed as NOT_PLANNED."
  not "0 issues have been closed as NOT_PLANNED.").
- As evaluation rules get complicated, keep the false-positive guard pass
  separate from the individual-flag logic so rules can be reasoned about and
  unit tested in isolation.
- Add a unit test for any new parsing or flagging logic; the modules most prone
  to regressions (profile_utils, repo_fetching, workflow_utils, cli_utils,
  infra_utils) all have dedicated test files.