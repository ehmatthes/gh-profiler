"""Root conftest.py"""

# Any tests in developer_resources/ are meant to be run manually.
# Don't collect e2e tests; only run when specified over CLI.
collect_ignore = ["developer_resources", "tests/e2e_tests"]
