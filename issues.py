#!/usr/bin/env python3
import requests
import argparse as ap

p = ap.ArgumentParser('issues')
p.add_argument('repo')
p.add_argument('--token')

a = p.parse_args()

# API URL for fetching issues
url = f"https://api.github.com/repos/{a.repo}/issues?state=all&per_page=100"

headers = {"Accept": "application/vnd.github.v3+json"}

if a.token:
    headers["Authorization"] = f"token {a.token}"

issues = []

# Fetch issues
response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json()

# Print issues and conversations
for issue in issues:
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"URL: {issue['html_url']}")
    print(f"State: {issue['state']}")
    print(f"Created by: {issue['user']['login']}")
    print(f"Description: {issue.get('body', 'No description')}\n")

    # Fetch issue comments
    comments_url = issue["comments_url"]
    comments_response = requests.get(comments_url, headers=headers)
    if comments_response.status_code == 200:
        comments = comments_response.json()
        for comment in comments:
            print(f"Comment by {comment['user']['login']}:")
            print(f"{comment['body']}\n")

    print("=" * 80 + "\n")
