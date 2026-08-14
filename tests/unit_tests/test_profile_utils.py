"""Tests for fetching and parsing user data from GitHub."""

import pytest

from gh_profiler.utils import infra_utils
from gh_profiler.utils import profile_utils
from gh_profiler.utils.profile_data import profile_data as pdata


@pytest.fixture(autouse=True)
def clean_pdata():
    """Start each test with a fresh pdata, to avoid state leaking between tests."""
    pdata.reset_fields()
    pdata.username = "octocat"


def _repo_node(owner, **kwargs):
    """Build a minimal node with a repository owner."""
    node = {"repository": {"owner": {"login": owner}}}
    node.update(kwargs)
    return node


# --- _classify_repos ---

def test_classify_repos_handles_case():
    """Repo owner and org logins should match case-insensitively."""
    nodes = [
        _repo_node("octocat"),
        _repo_node("OctoCat"),
        _repo_node("acme"),
        _repo_node("Acme"),
        _repo_node("otheruser"),
    ]

    owned, in_orgs, external = profile_utils._classify_repos(nodes, "octocat", ["ACME"])

    assert len(owned) == 2
    assert len(in_orgs) == 2
    assert len(external) == 1


def test_classify_repos_no_orgs():
    """A user with no orgs should still split owned from external."""
    nodes = [_repo_node("octocat"), _repo_node("otheruser")]

    owned, in_orgs, external = profile_utils._classify_repos(nodes, "octocat", [])

    assert len(owned) == 1
    assert len(in_orgs) == 0
    assert len(external) == 1


# --- _parse_pr_activity ---

def test_parse_pr_activity_counts():
    """Counts should reflect owned, org, and external PR buckets."""
    prs_json = {
        "data": {
            "search": {
                "nodes": [
                    _repo_node("octocat", mergedAt=None, state="OPEN"),
                    _repo_node("acme", mergedAt=None, state="OPEN"),
                    _repo_node("other1", mergedAt="2024-01-01T00:00:00Z", state="MERGED"),
                    _repo_node("other2", mergedAt=None, state="CLOSED"),
                ]
            }
        }
    }
    pdata.orgs = ["ACME"]

    profile_utils._parse_pr_activity(__import__("json").dumps(prs_json))

    assert pdata.opened_count == 4
    assert pdata.opened_count_owned == 1
    assert pdata.opened_count_orgs == 1
    assert pdata.opened_count_external == 2
    assert pdata.merged_count_external == 1
    assert pdata.closed_count_external == 1


# --- _parse_issue_activity ---

def test_parse_issue_activity_counts():
    """Issue buckets, NOT_PLANNED, and repeated titles should all be found."""
    issues_json = {
        "data": {
            "search": {
                "nodes": [
                    _repo_node("octocat", stateReason=None, title="My own issue"),
                    _repo_node("acme", stateReason=None, title="Org issue"),
                    _repo_node("other1", stateReason="NOT_PLANNED", title="Spam title"),
                    _repo_node("other2", stateReason=None, title="Spam title"),
                    _repo_node("other3", stateReason=None, title="Unique title"),
                ]
            }
        }
    }
    pdata.orgs = ["ACME"]

    profile_utils._parse_issue_activity(__import__("json").dumps(issues_json))

    assert pdata.new_issue_count == 5
    assert pdata.issues_owned == 1
    assert pdata.issues_orgs == 1
    assert pdata.issues_external == 3
    assert pdata.issues_not_planned == 1
    assert pdata.total_repeats == 2
    assert pdata.repeated_issue_titles == {"Spam title": 2}


def test_parse_issue_activity_matches_analyzed_nodes():
    """new_issue_count should match what we actually analyzed, not issueCount.

    The search API caps results at 100, so a large issueCount could disagree
    with the nodes we got back. Reporting the node count keeps the numbers
    consistent with the rest of the analysis.
    """
    issues_json = {
        "data": {
            "search": {
                "issueCount": 5,
                "nodes": [
                    _repo_node("other1", stateReason=None, title="A"),
                    _repo_node("other2", stateReason=None, title="B"),
                ],
            }
        }
    }
    pdata.orgs = []

    profile_utils._parse_issue_activity(__import__("json").dumps(issues_json))

    assert pdata.new_issue_count == 2


# --- _run_gh_cmd ---

def test_run_gh_cmd_success(monkeypatch):
    """A successful command returns its result."""
    result = infra_utils.CommandResult(stdout="{}", stderr="", returncode=0)
    monkeypatch.setattr(infra_utils, "run_cmd", lambda cmd: result)

    returned = profile_utils._run_gh_cmd("gh api x", "test")

    assert returned is result


def test_run_gh_cmd_failure_raises(monkeypatch):
    """A failed command raises ValueError with gh's stderr."""
    result = infra_utils.CommandResult(stdout="", stderr="gh: Not Found (HTTP 404)", returncode=1)
    monkeypatch.setattr(infra_utils, "run_cmd", lambda cmd: result)

    with pytest.raises(ValueError, match="404"):
        profile_utils._run_gh_cmd("gh api x", "test")


# --- get_data ---

def test_get_data_end_to_end(monkeypatch):
    """A full get_data run should parse everything from the fake gh calls."""
    profile_json = '{"login":"octocat","name":"Octo","created_at":"2020-01-01T00:00:00Z","company":null,"blog":"","location":null,"email":null,"bio":null}'
    orgs_json = '[{"login":"ACME","description":null,"url":"x"}]'
    socials_json = "[]"
    prs_json = __import__("json").dumps({
        "data": {"search": {"nodes": [_repo_node("other1", mergedAt=None, state="CLOSED")]}}
    })
    issues_json = __import__("json").dumps({
        "data": {"search": {"nodes": [_repo_node("other1", stateReason="NOT_PLANNED", title="T")]}}
    })

    def fake_run_cmd(cmd):
        if "auth status" in cmd:
            return infra_utils.CommandResult(stdout="Logged in to github.com as octocat\n", stderr="", returncode=0)
        if "--jq" in cmd and "orgs" in cmd:
            return infra_utils.CommandResult(stdout=orgs_json, stderr="", returncode=0)
        if "social_accounts" in cmd:
            return infra_utils.CommandResult(stdout=socials_json, stderr="", returncode=0)
        if "is:pull-request" in cmd:
            return infra_utils.CommandResult(stdout=prs_json, stderr="", returncode=0)
        if "is:issue" in cmd:
            return infra_utils.CommandResult(stdout=issues_json, stderr="", returncode=0)
        if "users/octocat" in cmd:
            return infra_utils.CommandResult(stdout=profile_json, stderr="", returncode=0)
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(infra_utils, "run_cmd", fake_run_cmd)

    profile_utils.get_data()

    assert pdata.orgs == ["ACME"]
    assert pdata.opened_count == 1
    assert pdata.opened_count_external == 1
    assert pdata.new_issue_count == 1
    assert pdata.issues_not_planned == 1


def test_get_data_failed_fetch_exits_cleanly(monkeypatch):
    """A failed gh call should exit with a message, not crash with a traceback."""
    profile_json = '{"login":"octocat","created_at":"2020-01-01T00:00:00Z"}'

    def fake_run_cmd(cmd):
        if "auth status" in cmd:
            return infra_utils.CommandResult(stdout="Logged in to github.com as octocat\n", stderr="", returncode=0)
        if "orgs" in cmd:
            return infra_utils.CommandResult(stdout="", stderr="gh: rate limit exceeded", returncode=1)
        if "users/octocat" in cmd:
            return infra_utils.CommandResult(stdout=profile_json, stderr="", returncode=0)
        return infra_utils.CommandResult(stdout="{}", stderr="", returncode=0)

    monkeypatch.setattr(infra_utils, "run_cmd", fake_run_cmd)

    with pytest.raises(SystemExit):
        profile_utils.get_data()
