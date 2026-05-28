# Run unit tests, and e2e tests.
# 
# As of 5/23/26, e2e tests are taking just about a second to run.
# If they're taking much longer than a few seconds, it's probably worth
# cancelling the run and run again.

# Unit tests.
uv run pytest

# E2e tests.
uv run pytest tests/e2e_tests

# Tests against actual users.
uv run pytest developer_resources/test_actual_users.py -s
