"""Reference output for testing summary."""

full_summary = """
GitHub user: ehmatthes
  🟢 Account age: 5058 days

  🟢 Profile information:
      name: Eric Matthes
      blog: https://www.mostlypython.com
      location: western North Carolina
      email: ehmatthes@gmail.com
     empty fields: company, bio

  🟢 ehmatthes has opened fewer than 10 PRs in the last 21 days.
""".strip()

summary_empty_profile = """
GitHub user: ehmatthes
  🟢 Account age: 5058 days

  🔴 No profile information has been provided.

  🟢 ehmatthes has opened fewer than 10 PRs in the last 21 days.
""".strip()
