gh-profiler
===

Like many, I've gotten waves of open source contributions where many of the new issues and PRs aren't worth engaging with. But it takes me a bit of time to sort through each of them.

People like to say that code should "speak for itself", but I've found that looking at a GitHub user's profile has been more helpful in making a quick determination about how much time to invest in the issue or PR. I typically look at a few quick things:

- Has the person made an unusually high number of PRs lately?
- Have a significant portion of these PRs been closed without merging?
- Have they opened an excessive number of issues?
- How old is the account?
- Is there any meaningful information on their profile?

I don't make a final decision about PRs and issues based on the answers to these questions, but many times I see enough red flags here that I have a good idea not to spend much time evaluating the contribution. (I'm mostly talking about PRs and issues where there's been no prior discussion, and there's a lot of text or changes in the PR/issue to review if I'm going to take it seriously.)

The goal of this project is to get a quick snapshot of this kind of information, without having to do a bunch of clicking on GitHub. The output is a summary of what's found, with a quick visual cue as to which factors support investing time in the PR/issue, and which factors suggest it's better off being closed and ignored. I have no interest in calculating some kind of trust score, or any other single number.

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

Installing and then running
---

You can also install the project, and then run the bare `gh-profiler` command:

```sh
(.venv) $ pip install gh-profiler
Installed 1 package in 4ms
 + gh-profiler==0.1.0
(.venv) $ gh-profiler ehmatthes

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
$ rm -rf dist/*
$ uv build
$ uv publish
```
