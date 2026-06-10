gh-profiler
===

Many of us have received waves of open source contributions where many of the new "contributions" aren't worth engaging with. gh-profiler lets you quickly see a snapshot of the submitter's profile, and recent PR activity.

This meant to give you some quick context about how much to invest in reviewing the PR. It's not meant to give an immediate signal to close the PR or issue.

This tool should not flag anyone making good-faith efforts to contribute to open source projects. If you think it is, please open an issue and describe the behavior that's being flagged.

Running as a tool
---

If you have uv installed, you can run this as a tool against any GitHub user:

```txt
$ uvx gh-profiler <redacted> --concise
GitHub user: <redacted>
🟡 Some concerns found with user's profile.
🟢 No concerns found with recent PR activity.
🔴 Significant concerns found with recent issue activity.

For a more detailed report, run `gh-profiler <redacted>`.
```

This is the concise output, which gives you a quick sense of whether the user has any recent activity that indicates problematic open source behavior.

The full output gives you much more specific information:

```txt
$ uvx gh-profiler <redacted>
GitHub user: <redacted>
🟡 Some concerns found with user's profile.
   🟡 Account age: 6 months
   🟢 Profile information:
        name: <redacted>
        blog: <redacted>
        email: <redacted>
      Empty fields: company, location, bio

🟢 No concerns found with recent PR activity.
   2 PRs opened in the last 21 days.
      0 opened against repos the user owns.
      0 opened against repos in publicly associated orgs.
      2 opened against external repos.

   🟢 1 of 2 external PRs merged in the last 21 days.
   🟢 1 of 2 external PRs closed without merging in the last 21 days.

🔴 Significant concerns found with recent issue activity.
   79 new issues opened in the last 21 days.
      0 opened in repos the user owns.
      0 opened in repos in publicly associated orgs.
      79 opened in external repos.

   🟢 1 external issue closed as NOT_PLANNED.
   🔴 78 external issues opened with the same title:
        📋 Documentation Enhancement Suggestion (70)
```

If you're working in your local project directory, you can simply provide a PR or issue number. The tool will look up the PR or issue, identify the user who opened it, and give a report on that user:

```txt
$ uvx gh-profiler 8
Issue #8: Accept a username or an issue/ pr number.
Author: ehmatthes
  🟢 Account age: 13 years
  ...
```

Installing and then running
---

You can also install the project, and then run the bare `gh-profiler` command:

```sh
(.venv) $ pip install gh-profiler
(.venv) $ gh-profiler ehmatthes
GitHub user: ehmatthes
  🟢 Account age: 13 years
  ...
```

When you've installed the project, you can also run it as a module:

```sh
$ python -m gh_profiler <username>
```

Verbose output
---

The `-v` or `--verbose` flag will print some of the rationales for evaluating flags:

```txt
$ uv run gh-profiler <redacted> -v

Flag adjusted: Set account age flag green. This user has a newer account,
  but they have no other concerning activity.

Flags adjusted: Set profile info and overall profile flags green. This user has not
  opened any recent PRs or issues, so they have no concerning activity.

--- Summary ---

GitHub user: <redacted>
🟢 No concerns found with user's profile.
   🟢 Account age: 20 minutes
   🟢 Profile information:
      Empty fields: name, company, blog, location, email, bio
...
```

Concise output
---

If you want just the simplest summary, you can pass the `--concise` flag:

```txt
$ uvx gh-profiler <redacted> --concise
GitHub user: <redacted>
🟡 Some concerns found with user's profile.
🟢 No concerns found with recent PR activity.
🔴 Significant concerns found with recent issue activity.

For a more detailed report, run `gh-profiler <redacted>`.
```

Bulk profiling of recent PRs
---

You can run concise profiles of the most recently opened PRs by passing the repo URL as the target:

```txt
$ uvx gh-profiler https://github.com/django/django
PR 21427: Fixed #37147 -- Fixed rendering empty values for models with db_default on primary key.
https://github.com/django/django/pull/21427

  GitHub user: <redacted>
  🟢 No concerns found with user's profile.
  ...


PR 21426: Fixed #37130 -- Skip DB cache deletion when culling offset is zero.
https://github.com/django/django/pull/21426

  GitHub user: <redacted>
  🟢 No concerns found with user's profile.
  ...

            Comparison of gh-profiler results with final merged state:             
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PR num ┃ gh-profiler ┃ Author     ┃ PR link                                     ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 21427  │ 🟢🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21427 │
│ 21425  │ 🔴🟡🟢      │ <redacted> │ https://github.com/django/django/pull/21425 │
...
│ 21416  │ 🟢🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21416 │
│ 21415  │ 🟡🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21415 │
└────────┴─────────────┴────────────┴─────────────────────────────────────────────┘
```

By default, this will process the 10 most recently opened PRs. If you want to process a different number, use the `-n` arg:

```txt
$ uvx gh-profiler <repo-url> -n 3
```

You can also look back at the most recently closed PRs, and request just the final summary table:

```txt
$ uv run gh-profiler https://github.com/django/django --back --table-only --redact
Fetching user profiles ..........

                 Comparison of gh-profiler results with final merged state:                  
┏━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ PR num ┃ Merged? ┃ gh-profiler ┃ Author     ┃ PR link                                     ┃
┡━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 21428  │   🔴    │ 🟢🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21428 │
│ 21423  │   🔴    │ 🔴🟡🟢      │ <redacted> │ https://github.com/django/django/pull/21423 │
│ 21197  │   🟣    │ 🟢🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21197 │
...
│ 21401  │   🟣    │ 🟢🟢🟢      │ <redacted> │ https://github.com/django/django/pull/21401 │
└────────┴─────────┴─────────────┴────────────┴─────────────────────────────────────────────┘
```

> [!NOTE]
> When using `--back` to look at merged and closed PRs, the output may differ from what you see on GitHub's PR tab in the corresponding repo. The gh API returns a different filtered set than what we see when we click "closed" on the PR tab in a browser. The data you see for each PR should be accurate; if it's not, please open an issue.

False positives
---

Some checks are in place to ensure that people who are not engaged in clear problematic behavior don't raise red or yellow flags. For example, a new user who opens a bunch of identical issues or PRs will have a red flag for the account age. But a new user who does not show any other signs of problematic behavior will have their account age flag set to green.

If you see an example of red or yellow flags being raised with no clear indication of problematic behavior, please consider opening an issue.

GitHub Actions
---

gh-profiler can write a GitHub Action that will automatically run `gh-profiler --concise` any time a new PR or issue is opened on your project. You can choose to have the profile output written as a comment on the new PR or issue, or you can have the workflow only write a link to the Action log containing the profile output.

See a [working demo](https://github.com/ehmatthes/workflow_sandbox), where you can open a new issue and see both kinds of output.

The `--generate-workflow` option asks which kind of workflow you'd like to use, and then writes a `profile_contributors.yml` file to `.github/workflows`:

```txt
$ uvx gh-profiler --generate-workflow
Would you like to write the concise profile output as a comment on each new PR/issue,
or just write a link to the Actions log containing the profile output?

1) Write concise profile output as a comment.
2) Only write the link to the Actions log.

Workflow type: 
  ...
```

> [!NOTE]
> You don't need Python if you want to run gh-profiler each time a PR or issue is opened in a repository. You can copy the [profiler_contributors.yml](https://github.com/ehmatthes/gh-profiler/blob/main/src/gh_profiler/templates/profile_contributors.yml) file or the [profiler_contributors_link_only.yml](https://github.com/ehmatthes/gh-profiler/blob/main/src/gh_profiler/templates/profile_contributors_link_only.yml) file and paste it into your own `.github/workflows/` directory.
> 
> From that point forward, you'll see a comment on each new PR and issue with a concise summary of the user that opened the PR or issue or a link to the Actions log containing the profile output. [Example](https://github.com/ehmatthes/gh-profiler/issues/67#issuecomment-4492670239)

Talks & discussion
---

This is a list of talks and discussions related to gh-profiler.

- PyCon US 2026 lightning talk (video not released yet)
- Real Python [episode 296](https://realpython.com/podcasts/rpp/296/#t=2296) (brief overview of project)

Maintaining
---

### `--redact`

For live demos and screenshots, you can pass the `--redact` flag. The username and profile information sections will show "\<redacted\>" in place of identifying information:

```txt
$ uv run gh-profiler 39 --redact
Issue #39: Add a `--redact` flag
Author: <redacted>
  🟢 Account age: 13 years

  🟢 Profile information:
      name: <redacted>
      blog: <redacted>
      ...
```

### Add/ modify a requirement

- Add or modify a requirement by modifying pyproject.toml, or running `uv add <package>`.
- For a dev dependency, run `uv add --dev <package>`.
- Then run `uv lock`.

Running tests
---

Run all tests except end-to-end tests:

```sh
$ uv run pytest
```

End-to-end tests are slower because they make actual API calls. You have to run them explicitly:

```sh
$ uv run pytest tests/e2e_tests
```

There's a test that runs against a longer set of actual users. It pulls from a data file that's stored outside this repo, because we don't want to call attention to any specific users. There's an empty data file template in `developer_resources/`, for people who want to start testing against actual users.

```sh
$ export PATH_ACTUAL_USERS=<path/to/actual_users.toml>
$ uv run pytest developer_resources/test_actual_users.py -s
```

The `-s` flag is helpful to see each user account that's being tested. For fuller documentation, see the comments in `test_actual_users.py`. This test will likely be moved to `tests/e2e_tests/`, but the usernames will always be kept outside this repo.

There's a shell script that runs all these tests. It works on macOS and probably linux, but may not work on Windows.

```sh
$ ./test_all.sh
```

Profiling
---

```sh
$ uv run python -m cProfile -s cumtime -m gh_profiler ehmatthes > profile.txt
```

Style notes
---

- When composing output messages, prefer terse messages over verbose messages:
    - "0 issues closed as NOT_PLANNED." over "0 issues have been closed as NOT_PLANNED."

Benchmarking
---

To track overall real-world performance over time, use the benchmarking script:

```sh
$ uv run developer_resources/benchmark.py
$ uv run developer_resources/benchmark.py <target>
```

Benchmarking is pretty straightforward when:

- Using `git switch` to switch between main and dev branches;
- Using Git to check out different tags and commits.
- Using `uv run --python 3.14`, `uv run --python 3.14t`, etc.

New releases
---

Update changelog and bump version, then:

```sh
$ uv lock
# Commit all changes.
$ git tag vX.Y.Z
$ git push origin vX.Y.Z
$ rm -rf dist/*
$ uv build
$ uv publish
```
