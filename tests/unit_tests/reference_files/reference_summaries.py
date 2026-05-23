"""Reference output for testing summary."""

full_summary = """
GitHub user: ehmatthes
  🟢 Account age: 13 years

  🟢 Profile information:
      name: Eric Matthes
      blog: https://www.mostlypython.com
      location: western North Carolina
      email: ehmatthes@gmail.com
     Empty fields: company, bio

  🟢 ehmatthes opened fewer than 10 PRs in the last 21 days.

  🟢 ehmatthes opened 7 new issues in the last 21 days.
     🟢 0 issues closed as NOT_PLANNED.
     🟢 0 issues opened with the same title.
""".strip()

summary_empty_profile = """
GitHub user: ehmatthes
  🟢 Account age: 13 years

  🔴 No profile information provided.

  🟢 ehmatthes opened fewer than 10 PRs in the last 21 days.

  🟢 ehmatthes opened 7 new issues in the last 21 days.
     🟢 0 issues closed as NOT_PLANNED.
     🟢 0 issues opened with the same title.
""".strip()
