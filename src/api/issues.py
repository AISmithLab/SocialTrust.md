from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


def get_issues_by_state(owner, repo, token, params=None, state=None):
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state={state}"
    headers = {'Authorization': f'token {token}'}
    page = 1
    issues_fetched = 0
    while True:
        paged_params = params.copy() if params else {}
        paged_params.update({'page': page, 'per_page': 100})
        try:
            issues_response = requests.get(issues_url, params=paged_params, headers=headers)
            issues_response.raise_for_status()
            issues_data = issues_response.json()
            if not issues_data:
                break
            for issue in issues_data:
                if 'pull' not in issue.get('html_url', ''):
                    issues_fetched += 1
            page += 1
        except RequestException as e:
            print(f"An error occurred while fetching issues: {e}")
            raise
    return issues_fetched


def get_abandoned_issues(owner, repo, token, params=None):
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=closed"
    headers = {'Authorization': f'token {token}'}
    page = 1
    issues_fetched = 0
    while True:
        paged_params = params.copy() if params else {}
        paged_params.update({'page': page, 'per_page': 100})
        try:
            issues_response = requests.get(issues_url, params=paged_params, headers=headers)
            issues_response.raise_for_status()
            issues_data = issues_response.json()
            if not issues_data:
                break
            for issue in issues_data:
                if 'pull' not in issue.get('html_url', '') and issue['state_reason'] == 'not_planned':
                    issues_fetched += 1
            page += 1
        except RequestException as e:
            print(f"An error occurred while fetching issues: {e}")
            raise
    return issues_fetched


def get_comments_by_issue(owner, repo, token, issue_number):
    comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {'Authorization': f'token {token}'}
    comments_response = requests.get(comments_url, headers=headers)
    if comments_response.status_code == 200:
        return comments_response.json()
    else:
        print(f"Failed to retrieve comments for issue {issue_number}. Status code: {comments_response.status_code}")
        return None


def get_issue_by_number(owner, repo, token, issue_number):
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {'Authorization': f'token {token}'}
    issue_response = requests.get(issue_url, headers=headers)
    if issue_response.status_code == 200:
        return issue_response.json()
    else:
        print(f"Failed to retrieve issue {issue_number}. Status code: {issue_response.status_code}")
        return None


def get_recent_issues(owner, repo, token, params=None):
    start_date = "2023-07-01T00:00:01Z"
    issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&since={start_date}"
    headers = {'Authorization': f'token {token}'}
    issues = []
    page = 1
    while True:
        paged_params = params.copy() if params else {}
        paged_params.update({'page': page, 'per_page': 100})
        try:
            issues_response = requests.get(issues_url, params=paged_params, headers=headers)
            issues_response.raise_for_status()
            issues_data = issues_response.json()
            if not issues_data:
                break
            for issue in issues_data:
                if 'pull' not in issue.get('html_url', ''):
                    issues.append(issue)
            page += 1
        except RequestException as e:
            print(f"An error occurred while fetching issues : {e}")
            raise
    return issues


def get_issues_rate(owner, repo):
    url = f"https://github.com/{owner}/{repo}/issues"
    print("GET " + url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html.parser")
            open_issues = soup.find_all('a', {'data-ga-click': "Issues, Table state, Open"})
            closed_issues = soup.find_all('a', {'data-ga-click': "Issues, Table state, Closed"})
            if open_issues and closed_issues:
                data = {
                    'open_issues': int(open_issues[0].text.strip().split(" ")[0].replace(',', '')),
                    'closed_issues': int(closed_issues[0].text.strip().split(" ")[0].replace(',', ''))
                }
                return data
    except RequestException as e:
        print(f"An error occurred while fetching: {e}. Skipping this issue.")
        return None
