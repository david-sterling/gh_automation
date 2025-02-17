"""
GitHub Pull Request Auto-Approver

This script automatically approves and merges GitHub pull requests that contain a specific keyword
in their titles. It uses the GitHub CLI (gh) to interact with GitHub.

Requirements:
    - GitHub CLI (gh) must be installed and authenticated
    - Python 3.6+
    - GitHub permissions to approve and merge PRs

Usage:
    Simply run the script:
    $ python autoapprove.py

    The script will:
    1. Search for open PRs where you are requested as a reviewer
    2. For PRs containing 'YOURFAVOURITEKEYWORD' in the title:
       - Automatically approve the PR with the comment 'lit'
       - Attempt to merge the PR using squash strategy
       - Delete the source branch after merging
"""

import json
import subprocess
import logging
from typing import Tuple, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

KEYWORD = "YOURFAVOURITEKEYWORD"
APPROVAL_MESSAGE = "lit"

def run_command(command: str) -> Tuple[int, bytes, bytes]:
    """Execute a shell command and return its output."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def fetch_pull_requests() -> List[Dict]:
    """Fetch open pull requests that require review."""
    search_command = "gh search prs --state=open --review-requested=@me --json url,title -L 100 > prs.json"
    returncode, _, stderr = run_command(search_command)

    if returncode != 0:
        logging.error(f"Failed to search PRs: {stderr.decode()}")
        return []

    try:
        with open('prs.json', 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return []

def process_pull_request(pr: Dict) -> None:
    """Process a single pull request for approval and merging."""
    pr_title = pr['title']
    repo_url = pr['url']

    if KEYWORD.lower() not in pr_title.lower():
        logging.info(f'Skipping PR "{pr_title}" - no keyword match')
        return

    # Approve PR
    approve_command = f'gh pr review {repo_url} --approve -b "{APPROVAL_MESSAGE}"'
    returncode, _, stderr = run_command(approve_command)
    
    if returncode != 0:
        logging.error(f'Failed to approve PR {repo_url}: {stderr.decode()}')
        return

    logging.info(f'Successfully approved PR: {repo_url}')

    # Merge PR
    merge_command = f'gh pr merge {repo_url} --squash --auto --merge --delete-branch -A email'
    returncode, _, stderr = run_command(merge_command)
    
    if returncode == 0:
        logging.info(f'Successfully merged PR: {repo_url}')
    else:
        logging.error(f'Failed to merge PR {repo_url}: {stderr.decode()}')

def main():
    """Main function to process all pull requests."""
    pull_requests = fetch_pull_requests()
    
    if not pull_requests:
        logging.warning("No pull requests found")
        return

    for pr in pull_requests:
        process_pull_request(pr)

if __name__ == "__main__":
    main()


