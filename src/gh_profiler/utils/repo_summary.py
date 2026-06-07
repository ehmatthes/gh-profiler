"""Utils for summarizing bulk PRs."""




def show_summary(target_prs):
    """Show summary for all processed PRs."""
    for pr in target_prs:
        print(pr.summary)