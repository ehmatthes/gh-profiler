gh-profiler
===

Many of us have received waves of open source contributions where many of the new "contributions" aren't worth engaging with. gh-profiler lets you quickly see a snapshot of the submitter's profile, and recent PR activity.

This meant to give you some quick context about how much to invest in reviewing the PR. It's not meant to give an immediate signal to close the PR or issue.

> [!NOTE]
> You don't need Python if you want to run gh-profiler each time a PR or issue is opened in a repository. You can copy the [profiler_contributors.yml](https://github.com/ehmatthes/gh-profiler/blob/main/src/gh_profiler/templates/profile_contributors.yml) file and paste it into your own `.github/workflows/` directory. From that point forward, you'll see a comment on each new PR and issue with a concise summary of the user that opened the PR or issue. [Example](https://github.com/ehmatthes/gh-profiler/issues/67#issuecomment-4492670239)

Running as a tool
---

If you have uv installed, you can run this as a tool against any GitHub user:

```sh
$ uvx gh-profiler <redacted>
GitHub user: <redacted>
  🟡 Account age: 159 days

  🟢 Profile information:
      name: <redacted>
      blog: https://<redacted>.com
      email: info@<redacted>.com
     Empty fields: company, location, bio

  🟢 <redacted> has opened fewer than 10 PRs in the last 21 days.

  🔴 <redacted> has opened 6 new issues in the last 21 days.
     🟢 0 issues have been closed as NOT_PLANNED.
     🔴 6 issues were opened with the same title:
        📋 Documentation Enhancement Suggestion (6)
```

If you're working in your local project directory, you can simply provide a PR or issue number. The tool will look up the PR or issue, identify the user who opened it, and give a report on that user:

```sh
$ uvx gh-profiler 8
Issue #8: Accept a username or an issue/ pr number.
Author: ehmatthes
  🟢 Account age: 5,058 days
  ...
```

Installing and then running
---

You can also install the project, and then run the bare `gh-profiler` command:

```sh
(.venv) $ pip install gh-profiler
(.venv) $ gh-profiler ehmatthes
GitHub user: ehmatthes
  🟢 Account age: 5,058 days
  ...
```

When you've installed the project, you can also run it as a module:

```sh
$ python -m gh_profiler <username>
```

Concise output
---

If you want just the simplest summary, you can pass the `--concise` flag:

```sh
$ uvx gh-profiler <redacted> --concise
GitHub user: <redacted>
🟡 Some concerns found with user's profile.
🟢 No concerns found with recent PR activity.
🔴 Significant concerns found with recent issue activity.

For a more detailed report, run `gh-profiler <redacted>`.
```

GitHub Actions
---

gh-profiler can write a GitHub Action that will automatically run `gh-profiler --concise` any time a new PR or issue is opened on your project. The output will be written as a comment on the new PR or issue.

The `--generate-workflow` flag does this by writing a `profile_contributors.yml` file to `.github/workflows`:

```txt
$ uvx gh-profiler --generate-workflow
This will generate a GitHub action that will automatically run gh-profiler
whenever someone opens a new issue or PR in your repository. The profile
output will be written as a comment on the issue or PR.

The workflow will be written at the following location:
  /.../.github/workflows/profile_contributors.yml

Are you sure you want to do this? (y/n) y

The new workflow file was written:
  /.../.github/workflows/profile_contributors.yml

To start seeing profiles when new issues and PRs are opened:
- Commit the workflow file to your main branch.
- Push your main branch to GitHub.
  ...
```

Talks & discussion
---

This is a list of talks and discussions related to gh-profiler.

- PyCon US 2026 lightning talk (video not released yet)
- Real Python [episode 296](https://realpython.com/podcasts/rpp/296/#t=2296) (brief overview of project)

Maintaining
---

### `--redact`

For live demos and screenshots, you can pass the `--redact` flag. The username and profile information sections will show "\<redacted\>" in place of identifying information:

```sh
$ uv run gh-profiler 39 --redact
Issue #39: Add a `--redact` flag
Author: <redacted>
  🟢 Account age: 5,058 days

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

End-to-end tests are slower, and flakier because they make actual API calls. It's best to run a specific e2e test:

```sh
$ uv run pytest tests/e2e_tests -k full
$ uv run pytest tests/e2e_tests -k concise
```

There's a shell script that runs all of these tests. It works on macOS and probably linux, but may not work on Windows.

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
