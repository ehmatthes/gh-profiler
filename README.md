gh-profiler
===

Many of us have received waves of open source contributions where many of the new "contributions" aren't worth engaging with. gh-profiler lets you quickly see a snapshot of the submitter's profile, and recent PR activity.

This meant to give you some quick context about how much to invest in reviewing the PR. It's not meant to give an immediate signal to close the PR or issue.

Running as a tool
---

If you have uv installed, you can run this as a tool against any GitHub user:

```sh
$ uvx gh-profiler ehmatthes

GitHub user: ehmatthes
  🟢 Account age: 5058 days

  🟢 Profile information:
      name: Eric Matthes
      company:
      blog: https://www.mostlypython.com
      location: western North Carolina
      email: ehmatthes@gmail.com
      bio:

  🟢 ehmatthes has opened fewer than 10 PRs in the last 21 days.
```

If you're working in your local project directory, you can simply provide a PR or issue number. The tool will look up the PR or issue, identify the user who opened it, and give a report on that user:

```sh
$ uvx gh-profiler 8

GitHub user: ehmatthes
  🟢 Account age: 5058 days
  ...
```

Installing and then running
---

You can also install the project, and then run the bare `gh-profiler` command:

```sh
(.venv) $ pip install gh-profiler
(.venv) $ gh-profiler ehmatthes

GitHub user: ehmatthes
  🟢 Account age: 5058 days
  ...
```

When you've installed the project, you can also run it as a module:

```sh
$ python -m gh_profiler <username>
```

Maintaining
---

### Add/ modify a requirement

- Add or modify a requirement by modifying pyproject.toml, or running `uv add <package>`.
- Then run `uv lock`.

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
