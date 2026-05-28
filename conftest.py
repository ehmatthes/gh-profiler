"""Root conftest.py"""

# Any tests in developer_resources/ are meant to be run manually.
# Don't collect e2e tests; only run when specified over CLI.
collect_ignore = ["developer_resources", "tests/e2e_tests"]

# CLI arg for path to file containing actual usernames to test against.
# This is used in developer_resources/test_actual_users.py.
def pytest_addoption(parser):
    parser.addoption("--path-actual-usernames", action="store", default="")